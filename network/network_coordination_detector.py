"""
network_coordination_detector.py — Validator Collusion Detection (v4.5)

Identifies potential validator coordination through graph-based analysis of validation
patterns, timestamp proximity, and semantic similarity. Helps flag clusters
that may indicate bias, manipulation, or non-independent validation.

Part of superNova_2177's audit resilience system.
"""

import logging
from functools import lru_cache
from typing import List, Dict, Any, Set, Tuple
from collections import defaultdict
from datetime import datetime, timedelta
from statistics import mean
import itertools
from concurrent.futures import ProcessPoolExecutor
import os
import math

logger = logging.getLogger("superNova_2177.coordination")


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


@lru_cache(maxsize=1)
def _load_sentence_transformer():
    """Load and cache the sentence transformer model."""
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer("paraphrase-MiniLM-L6-v2")


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

    # Detect communities using simple clustering
    communities = detect_graph_communities(edges, set(validator_data.keys()))

    return {
        "edges": edges,
        "nodes": set(validator_data.keys()),
        "hypothesis_coverage": dict(hypothesis_validators),
        "communities": communities,
    }


def _detect_graph_communities_impl(
    edges: List[Tuple[str, str, float]], nodes: Set[str]
) -> List[Set[str]]:
    """
    Simple community detection using connected components.

    Args:
        edges: List of (validator1, validator2, weight) tuples
        nodes: Set of all validator nodes

    Returns:
        List of communities (sets of validator_ids)
    """
    # Build adjacency list for strong connections
    # TODO: profile with cProfile; consider using NetworkX for large graphs
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
            dfs(neighbor, community)  # Recursive DFS, replace with iterative if needed

    for node in nodes:
        if node not in visited and node in adj:
            community = set()
            dfs(node, community)
            if len(community) >= Config.MIN_CLUSTER_SIZE:
                communities.append(community)

    return communities


def _communities_cache_key(
    edges: List[Tuple[str, str, float]], nodes: Set[str]
) -> Tuple[Tuple[Tuple[str, str, float], ...], Tuple[str, ...]]:
    """Helper to create a hashable cache key."""
    return (
        tuple((e1, e2, float(w)) for e1, e2, w in edges),
        tuple(sorted(nodes)),
    )


@lru_cache(maxsize=128)
def _cached_detect_graph_communities(
    edges_key: Tuple[Tuple[str, str, float], ...], nodes_key: Tuple[str, ...]
) -> Tuple[Tuple[str, ...], ...]:
    communities = _detect_graph_communities_impl(
        [tuple(e) for e in edges_key], set(nodes_key)
    )
    return tuple(tuple(sorted(c)) for c in communities)


def detect_graph_communities(
    edges: List[Tuple[str, str, float]], nodes: Set[str]
) -> List[Set[str]]:
    """Cached wrapper for community detection."""
    key = _communities_cache_key(edges, nodes)
    cached = _cached_detect_graph_communities(*key)
    return [set(c) for c in cached]


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
            timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
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
    chunks = [pairs[i : i + chunk_size] for i in range(0, len(pairs), chunk_size)]

    with ProcessPoolExecutor() as executor:
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
    chunks = [items[i : i + chunk_size] for i in range(0, len(items), chunk_size)]

    with ProcessPoolExecutor() as executor:
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

    @lru_cache(maxsize=32)
    def _compute_embeddings_cached(texts_key: Tuple[str, ...]):
        texts = list(texts_key)
        try:
            model = _load_sentence_transformer()
            return model.encode(texts)
        except Exception as e:  # pragma: no cover - fallback rarely triggered
            logger.warning(
                f"SentenceTransformer unavailable: {e}; using TF-IDF fallback"
            )
            from sklearn.feature_extraction.text import TfidfVectorizer

            vec = TfidfVectorizer().fit(texts)
            return vec.transform(texts).toarray()

    # Cache embeddings to avoid expensive recomputation
    embeddings = _compute_embeddings_cached(tuple(all_notes))

    idx = 0
    validator_embeddings = {}
    for vid, notes in validator_texts.items():
        note_embeds = embeddings[idx : idx + len(notes)]
        idx += len(notes)
        validator_embeddings[vid] = note_embeds.mean(axis=0)

    semantic_clusters = []
    flags = []
    validators = list(validator_embeddings.keys())

    for v1, v2 in itertools.combinations(validators, 2):
        emb1 = validator_embeddings[v1]
        emb2 = validator_embeddings[v2]
        # Cosine similarity
        dot = float(emb1 @ emb2)
        norm = float((emb1 @ emb1) ** 0.5 * (emb2 @ emb2) ** 0.5)
        # TODO: profile NumPy operations; consider vectorization for large data
        similarity = dot / norm if norm else 0.0

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


@lru_cache(maxsize=256)  # memoization for repeated scoring
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
            "graph": {"edges": [], "nodes": set(), "communities": []},
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
            "graph": {"edges": [], "nodes": set(), "communities": []},
            "risk_breakdown": {"temporal": 0, "score": 0, "semantic": 0},
        }


def profile_coordination(validations: List[Dict[str, Any]], sort_by: str = "cumtime") -> None:
    """Profile coordination analysis to find performance issues."""
    import cProfile
    import pstats
    import io

    pr = cProfile.Profile()
    pr.enable()
    analyze_coordination_patterns(validations)
    pr.disable()
    s = io.StringIO()
    pstats.Stats(pr, stream=s).sort_stats(sort_by).print_stats(10)
    logger.debug("Coordination profiling results:\n%s", s.getvalue())


# TODO v4.6:
# - Integrate with reputation_influence_tracker for feedback loop
# - Add advanced NLP for semantic similarity (sentence embeddings)
# - Implement more sophisticated graph clustering algorithms (Louvain, Leiden)
# - Add validator organization/affiliation cross-reference
# - Include validation outcome correlation analysis
# - Add time-series analysis for evolving coordination patterns
# - Profile with cProfile to locate NumPy/NetworkX hot spots
