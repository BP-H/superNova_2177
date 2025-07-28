"""
network_coordination_detector.py — Validator Collusion Detection (v4.5)

Identifies potential validator coordination through graph-based analysis of validation
patterns, timestamp proximity, and semantic similarity. Helps flag clusters
that may indicate bias, manipulation, or non-independent validation.

Part of superNova_2177's audit resilience system.

This module can be profiled with ``cProfile`` to identify heavy NumPy or
NetworkX sections when analyzing large validation graphs::

    python -m cProfile -s time network/network_coordination_detector.py

To avoid issues when running under Streamlit, the detection functions use
``ThreadPoolExecutor`` by default instead of spawning new processes. Set the
``COORDINATION_USE_PROCESS_POOL`` environment variable to ``1`` to force the
use of ``ProcessPoolExecutor`` when true concurrency is desirable.
"""

import itertools
import logging
import math
import os
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from datetime import datetime, timedelta
from functools import lru_cache
from multiprocessing import get_context
from statistics import mean
from typing import Any, Dict, List, Set, Tuple

logger = logging.getLogger("superNova_2177.coordination")
logger.propagate = False

# Use threads by default because spawning new processes can fail in
# restricted environments like Streamlit. Set the environment variable
# ``COORDINATION_USE_PROCESS_POOL=1`` to force ``ProcessPoolExecutor``.
USE_PROCESS_POOL = os.environ.get("COORDINATION_USE_PROCESS_POOL") == "1"


class Config:
    # Temporal coordination thresholds
    TEMPORAL_WINDOW_MINUTES = 5
    MIN_TEMPORAL_OCCURRENCES = 3

    # Score similarity thresholds
    SCORE_SIMILARITY_THRESHOLD = 0.1
    MIN_SCORE_SIMILARITY_COUNT = 4

    # Graph clustering thresholds
    MIN_CLUSTER_SIZE = 3
    COORDINATION_EDGE_THRESHOLD = 0.7

    # Semantic similarity (placeholder for future NLP)
    SEMANTIC_SIMILARITY_THRESHOLD = 0.8
    REPEATED_PHRASE_MIN_LENGTH = 10

    # Risk scoring parameters
    MAX_FLAGS_FOR_NORMALIZATION = 20
    TEMPORAL_WEIGHT = 0.4
    SCORE_WEIGHT = 0.4
    SEMANTIC_WEIGHT = 0.2


@lru_cache(maxsize=1024)
def _parse_timestamp(ts: str) -> datetime:
    """Memoized ISO8601 parser used by temporal coordination."""
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


def build_validation_graph(validations: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Build a graph of validator relationships based on co-validation patterns.

    Args:
        validations: List of validation records

    Returns:
        Dict containing graph structure and metadata
    """
    hypothesis_validators = defaultdict(list)
    validator_data = defaultdict(list)

    for v in validations:
        validator_id = v.get("validator_id")
        hypothesis_id = v.get("hypothesis_id")
        if validator_id and hypothesis_id:
            hypothesis_validators[hypothesis_id].append(validator_id)
            validator_data[validator_id].append(v)

    edges = []
    edge_weights = defaultdict(float)

    for hypothesis_id, validators in hypothesis_validators.items():
        if len(validators) < 2:
            continue
        for v1, v2 in itertools.combinations(set(validators), 2):
            edge_key = tuple(sorted([v1, v2]))
            edge_weights[edge_key] += 1.0

    max_weight = max(edge_weights.values()) if edge_weights else 1.0
    for (v1, v2), weight in edge_weights.items():
        normalized_weight = weight / max_weight
        if normalized_weight >= 0.1:
            edges.append((v1, v2, normalized_weight))

    # Collect node list explicitly for use by callers expecting an ordered
    # sequence rather than a set.
    nodes = list(validator_data.keys())

    # Detect communities using simple clustering
    communities = detect_graph_communities(edges, set(nodes))

    return {
        "edges": edges,
        "nodes": nodes,
        "hypothesis_coverage": dict(hypothesis_validators),
        "communities": [list(c) for c in communities],
    }


def detect_graph_communities(
    edges: List[Tuple[str, str, float]], nodes: Set[str]
) -> List[Set[str]]:
    """
    Simple community detection using connected components.
    For larger graphs consider using ``networkx`` community functions and
    profile with ``cProfile`` to locate bottlenecks.

    Args:
        edges: List of (validator1, validator2, weight) tuples
        nodes: Set of all validator nodes

    Returns:
        List of communities (sets of validator_ids)
    """
    # Build adjacency list for strong connections
    adj = defaultdict(set)
    for v1, v2, weight in edges:
        if weight >= Config.COORDINATION_EDGE_THRESHOLD:
            adj[v1].add(v2)
            adj[v2].add(v1)

    visited = set()
    communities = []

    def dfs(node: str, community: Set[str]):
        if node in visited:
            return
        visited.add(node)
        community.add(node)
        for neighbor in adj[node]:
            dfs(neighbor, community)

    for node in nodes:
        if node not in visited and node in adj:
            community = set()
            dfs(node, community)
            if len(community) >= Config.MIN_CLUSTER_SIZE:
                communities.append(community)

    return communities


def _temporal_worker(
    pairs: List[Tuple[str, str, List[datetime], List[datetime]]],
    window: timedelta,
) -> Tuple[List[Dict[str, Any]], List[str]]:
    clusters: List[Dict[str, Any]] = []
    flags: List[str] = []
    for v1, v2, ts1_list, ts2_list in pairs:
        close_submissions = sum(
            1 for ts1 in ts1_list for ts2 in ts2_list if abs(ts1 - ts2) <= window
        )
        if close_submissions >= Config.MIN_TEMPORAL_OCCURRENCES:
            coordination_likelihood = min(1.0, close_submissions / 10.0)
            clusters.append(
                {
                    "validators": [v1, v2],
                    "close_submissions": close_submissions,
                    "coordination_likelihood": coordination_likelihood,
                }
            )
            flags.append(f"temporal_coordination_{v1}_{v2}")
    return clusters, flags


def _score_worker(
    items: List[Tuple[Tuple[str, str], List[Tuple[str, float, float]]]],
) -> Tuple[List[Dict[str, Any]], List[str]]:
    clusters: List[Dict[str, Any]] = []
    flags: List[str] = []
    for (v1, v2), similar_scores in items:
        if len(similar_scores) >= Config.MIN_SCORE_SIMILARITY_COUNT:
            avg_difference = mean([abs(s1 - s2) for _, s1, s2 in similar_scores])
            coordination_likelihood = min(1.0, len(similar_scores) / 10.0)
            clusters.append(
                {
                    "validators": [v1, v2],
                    "similar_score_count": len(similar_scores),
                    "avg_score_difference": round(avg_difference, 3),
                    "coordination_likelihood": coordination_likelihood,
                }
            )
            flags.append(f"score_coordination_{v1}_{v2}")
    return clusters, flags


def detect_temporal_coordination(validations: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Detect validators who consistently submit validations within suspicious time windows.

    Args:
        validations: List of validation records

    Returns:
        Dict with temporal coordination analysis
    """
    validator_timestamps = defaultdict(list)

    for v in validations:
        validator_id = v.get("validator_id")
        timestamp_str = v.get("timestamp")
        if not validator_id or not timestamp_str:
            continue
        try:
            timestamp = _parse_timestamp(timestamp_str)
            validator_timestamps[validator_id].append(timestamp)
        except Exception as e:
            logger.warning(f"Invalid timestamp for validator {validator_id}: {e}")
            continue

    temporal_clusters: List[Dict[str, Any]] = []
    flags: List[str] = []
    validators = list(validator_timestamps.keys())
    window = timedelta(minutes=Config.TEMPORAL_WINDOW_MINUTES)

    pairs = [
        (v1, v2, validator_timestamps[v1], validator_timestamps[v2])
        for v1, v2 in itertools.combinations(validators, 2)
    ]

    if not pairs:
        return {"temporal_clusters": [], "flags": []}

    cpu_count = os.cpu_count() or 1
    chunk_size = max(1, (len(pairs) + cpu_count - 1) // cpu_count)
    chunks = [
        pairs[i : i + chunk_size]  # noqa: E203
        for i in range(0, len(pairs), chunk_size)
    ]

    executor_cls = ProcessPoolExecutor if USE_PROCESS_POOL else ThreadPoolExecutor
    ctx = {"mp_context": get_context("spawn")} if USE_PROCESS_POOL else {}
    with executor_cls(**ctx) as executor:
        results = executor.map(_temporal_worker, chunks, itertools.repeat(window))
        for clusters, chunk_flags in results:
            temporal_clusters.extend(clusters)
            flags.extend(chunk_flags)

    return {"temporal_clusters": temporal_clusters, "flags": flags}


def detect_score_coordination(validations: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Detect validators who give suspiciously similar scores across multiple hypotheses.

    Args:
        validations: List of validation records

    Returns:
        Dict with score coordination analysis
    """
    hypothesis_scores = defaultdict(dict)

    for v in validations:
        validator_id = v.get("validator_id")
        hypothesis_id = v.get("hypothesis_id")
        score = v.get("score")
        if validator_id and hypothesis_id and score is not None:
            try:
                hypothesis_scores[hypothesis_id][validator_id] = float(score)
            except (ValueError, TypeError):
                continue

    validator_pairs = defaultdict(list)

    for hypothesis_id, scores in hypothesis_scores.items():
        validators = list(scores.keys())
        for v1, v2 in itertools.combinations(validators, 2):
            score1 = scores[v1]
            score2 = scores[v2]
            if abs(score1 - score2) <= Config.SCORE_SIMILARITY_THRESHOLD:
                validator_pairs[(v1, v2)].append((hypothesis_id, score1, score2))

    score_clusters: List[Dict[str, Any]] = []
    flags: List[str] = []

    items = list(validator_pairs.items())

    if not items:
        return {"score_clusters": [], "flags": []}

    cpu_count = os.cpu_count() or 1
    chunk_size = max(1, (len(items) + cpu_count - 1) // cpu_count)
    chunks = [
        items[i : i + chunk_size]  # noqa: E203
        for i in range(0, len(items), chunk_size)
    ]

    executor_cls = ProcessPoolExecutor if USE_PROCESS_POOL else ThreadPoolExecutor
    ctx = {"mp_context": get_context("spawn")} if USE_PROCESS_POOL else {}
    with executor_cls(**ctx) as executor:
        results = executor.map(_score_worker, chunks)
        for clusters, chunk_flags in results:
            score_clusters.extend(clusters)
            flags.extend(chunk_flags)

    return {"score_clusters": score_clusters, "flags": flags}


def detect_semantic_coordination(validations: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Detect validators who use suspiciously similar language in their
    validation notes using sentence embeddings.

    This replaces the older phrase-based approach with cosine similarity on
    averaged sentence embeddings. If the embedding model cannot be loaded (e.g.,
    due to network restrictions), the function falls back to a TF‑IDF based
    embedding.

    Args:
        validations: List of validation records

    Returns:
        Dict with semantic coordination analysis
    """

    validator_texts = defaultdict(list)

    for v in validations:
        validator_id = v.get("validator_id")
        note = v.get("note", "")
        if not validator_id or len(note) < Config.REPEATED_PHRASE_MIN_LENGTH:
            continue
        validator_texts[validator_id].append(note.lower().strip())

    if not validator_texts:
        return {"semantic_clusters": [], "flags": []}

    all_notes = [text for notes in validator_texts.values() for text in notes]

    @lru_cache(maxsize=128)
    def _compute_embeddings(texts: Tuple[str, ...]):
        """Heavy embedding computation cached for reuse."""
        try:
            from sentence_transformers import SentenceTransformer

            # Avoid accidental network downloads by forcing offline mode if unset
            os.environ.setdefault("HF_HUB_OFFLINE", "1")
            os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
            try:
                model = SentenceTransformer("paraphrase-MiniLM-L6-v2")
                return model.encode(list(texts))
            except Exception as st_exc:
                logger.warning(
                    f"SentenceTransformer failed: {st_exc}; using TF-IDF fallback"
                )
        except Exception as import_exc:  # pragma: no cover - fallback rarely triggered
            logger.warning(
                f"SentenceTransformer unavailable: {import_exc}; using TF-IDF fallback"
            )
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer

            vec = TfidfVectorizer().fit(list(texts))
            return vec.transform(list(texts)).toarray()
        except Exception as tfidf_exc:  # pragma: no cover - minimal fallback
            logger.error(
                f"TF-IDF fallback unavailable: {tfidf_exc}; using simple counts"
            )
            try:
                import numpy as np

                vocab = sorted({w for t in texts for w in t.split()})

                def to_counts(text: str) -> np.ndarray:
                    counts = [text.split().count(tok) for tok in vocab]
                    return np.array(counts, dtype=float)

                return np.stack([to_counts(t) for t in texts])
            except Exception as np_exc:  # pragma: no cover - extremely rare
                logger.error(f"NumPy unavailable: {np_exc}; using pure Python counts")

                vocab = sorted({w for t in texts for w in t.split()})

                def to_counts_list(text: str) -> List[float]:
                    return [float(text.split().count(tok)) for tok in vocab]

                return [to_counts_list(t) for t in texts]

    # Heavy embedding generation can dominate runtime on large datasets.
    # Profile with ``cProfile`` to verify and consider batching strategies.
    embeddings = _compute_embeddings(tuple(all_notes))

    def _average_vectors(vectors: List[Any]):
        """Compute mean of vectors supporting numpy arrays or lists."""
        try:
            import numpy as np

            if isinstance(vectors, np.ndarray):
                return vectors.mean(axis=0)
            if vectors and isinstance(vectors[0], np.ndarray):
                stacked = np.stack(vectors)
                return stacked.mean(axis=0)
        except Exception:
            pass

        length = len(vectors[0]) if vectors else 0
        sums = [0.0] * length
        for v in vectors:
            for i, val in enumerate(v):
                sums[i] += float(val)
        return [s / len(vectors) for s in sums]

    idx = 0
    validator_embeddings = {}
    for vid, notes in validator_texts.items():
        note_embeds = embeddings[idx : idx + len(notes)]  # noqa: E203
        idx += len(notes)
        validator_embeddings[vid] = _average_vectors(note_embeds)

    semantic_clusters = []
    flags = []
    validators = list(validator_embeddings.keys())

    for v1, v2 in itertools.combinations(validators, 2):
        emb1 = validator_embeddings[v1]
        emb2 = validator_embeddings[v2]

        def _cosine_similarity(a: Any, b: Any) -> float:
            try:
                import numpy as np

                if isinstance(a, np.ndarray) and isinstance(b, np.ndarray):
                    dot = float(a @ b)
                    norm = math.sqrt(float(a @ a) * float(b @ b))
                    return dot / norm if norm else 0.0
            except Exception:
                pass

            dot = sum(x * y for x, y in zip(a, b))
            norm1 = math.sqrt(sum(x * x for x in a))
            norm2 = math.sqrt(sum(y * y for y in b))
            norm = norm1 * norm2
            return dot / norm if norm else 0.0

        similarity = _cosine_similarity(emb1, emb2)

        if similarity >= Config.SEMANTIC_SIMILARITY_THRESHOLD:
            semantic_clusters.append(
                {
                    "validators": [v1, v2],
                    "similarity_score": round(similarity, 3),
                    "coordination_likelihood": similarity,
                }
            )
            flags.append(f"semantic_coordination_{v1}_{v2}")

    return {
        "semantic_clusters": semantic_clusters,
        "flags": flags,
    }


@lru_cache(maxsize=256)
def calculate_sophisticated_risk_score(
    temporal_flags: int, score_flags: int, semantic_flags: int, total_validators: int
) -> float:
    """
    Calculate a sophisticated risk score using weighted factors and normalization.

    Args:
        temporal_flags: Number of temporal coordination flags
        score_flags: Number of score coordination flags
        semantic_flags: Number of semantic coordination flags
        total_validators: Total number of validators analyzed

    Returns:
        float: Risk score between 0.0 and 1.0
    """
    if total_validators == 0:
        return 0.0

    # Normalize by validator count (more validators should reduce individual flag impact)
    validator_factor = math.log(max(2, total_validators)) / math.log(
        10
    )  # Log scale normalization

    # Weight different types of coordination
    weighted_score = (
        Config.TEMPORAL_WEIGHT * temporal_flags
        + Config.SCORE_WEIGHT * score_flags
        + Config.SEMANTIC_WEIGHT * semantic_flags
    )

    # Normalize by validator factor and max expected flags
    normalized_score = weighted_score / (
        validator_factor * Config.MAX_FLAGS_FOR_NORMALIZATION
    )

    # Apply sigmoid function for smooth scaling
    risk_score = 2 / (1 + math.exp(-4 * normalized_score)) - 1

    return max(0.0, min(1.0, risk_score))


def analyze_coordination_patterns(validations: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Comprehensive coordination analysis combining temporal, score, and semantic detection.
    Enhanced with sophisticated risk scoring and community detection.

    Args:
        validations: List of validation records

    Returns:
        Dict with comprehensive coordination analysis
    """
    if not validations:
        return {
            "overall_risk_score": 0.0,
            "coordination_clusters": [],
            "flags": ["no_validations"],
            "graph": {"edges": [], "nodes": [], "communities": []},
            "risk_breakdown": {"temporal": 0, "score": 0, "semantic": 0},
        }

    try:
        # Run all detection methods
        graph = build_validation_graph(validations)
        temporal_result = detect_temporal_coordination(validations)
        score_result = detect_score_coordination(validations)
        semantic_result = detect_semantic_coordination(validations)

        # Collect flags by type
        temporal_flags = temporal_result.get("flags", [])
        score_flags = score_result.get("flags", [])
        semantic_flags = semantic_result.get("flags", [])

        all_flags = temporal_flags + score_flags + semantic_flags

        coordination_clusters = {
            "temporal": temporal_result.get("temporal_clusters", []),
            "score": score_result.get("score_clusters", []),
            "semantic": semantic_result.get("semantic_clusters", []),
        }

        # Calculate sophisticated risk score
        total_validators = len(graph.get("nodes", set()))
        risk_score = calculate_sophisticated_risk_score(
            len(temporal_flags), len(score_flags), len(semantic_flags), total_validators
        )

        risk_breakdown = {
            "temporal": len(temporal_flags),
            "score": len(score_flags),
            "semantic": len(semantic_flags),
        }

        logger.info(
            f"Coordination analysis: {len(all_flags)} total flags "
            f"(T:{len(temporal_flags)}, S:{len(score_flags)}, Sem:{len(semantic_flags)}), "
            f"risk score: {risk_score:.3f}, validators: {total_validators}"
        )

        return {
            "overall_risk_score": round(risk_score, 3),
            "coordination_clusters": coordination_clusters,
            "flags": all_flags,
            "graph": graph,
            "risk_breakdown": risk_breakdown,
        }

    except Exception as e:
        logger.error(f"Coordination analysis failed: {e}", exc_info=True)
        return {
            "overall_risk_score": 0.0,
            "coordination_clusters": [],
            "flags": ["coordination_analysis_failed"],
            "graph": {"edges": [], "nodes": [], "communities": []},
            "risk_breakdown": {"temporal": 0, "score": 0, "semantic": 0},
        }


# TODO v4.6:
# - Integrate with reputation_influence_tracker for feedback loop
# - Add advanced NLP for semantic similarity (sentence embeddings)
# - Implement more sophisticated graph clustering algorithms (Louvain, Leiden)
# - Add validator organization/affiliation cross-reference
# - Include validation outcome correlation analysis
# - Add time-series analysis for evolving coordination patterns

# Profiling entry point. Run this file directly to profile the main analysis
# routine and inspect potential NumPy/NetworkX hotspots.
if __name__ == "__main__":  # pragma: no cover - manual profiling
    import cProfile
    import pstats
    from pathlib import Path

    sample_path = Path("sample_validations.json")
    if sample_path.exists():
        import json

        with sample_path.open() as fh:
            sample_data = json.load(fh)
    else:
        sample_data = []

    profiler = cProfile.Profile()
    profiler.enable()
    analyze_coordination_patterns(sample_data)
    profiler.disable()
    stats = pstats.Stats(profiler).sort_stats("cumtime")
    stats.print_stats(10)
