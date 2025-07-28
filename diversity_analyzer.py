"""
diversity_analyzer.py — Validator diversity scoring and analysis

Analyzes validation records to produce quality scores, detect contradictions,
and recommend certification levels for scientific hypotheses.

This module provides the foundation for automated peer review and consensus
tracking in the superNova_2177 scientific reasoning system.

This module can be profiled with ``cProfile`` to inspect NumPy-based
sentiment scoring or other bottlenecks::

    python -m cProfile -s time diversity_analyzer.py
"""

import logging
from typing import List, Dict, Any, Tuple
from functools import lru_cache
from datetime import datetime
from statistics import mean
from itertools import combinations
from difflib import SequenceMatcher

from validators.reputation_influence_tracker import compute_validator_reputations
from temporal_consistency_checker import analyze_temporal_consistency
from network.network_coordination_detector import detect_score_coordination

logger = logging.getLogger("superNova_2177.certifier")
logger.propagate = False


# --- Configuration ---
class Config:
    """Configurable thresholds and weights for validation certification."""

    # Certification thresholds (0.0 - 1.0)
    STRONG_THRESHOLD = 0.85  # High confidence, peer-reviewed quality
    PROVISIONAL_THRESHOLD = 0.65  # Moderate confidence, needs more evidence
    EXPERIMENTAL_THRESHOLD = 0.45  # Low confidence, early stage

    # Validation requirements
    MIN_VALIDATIONS = 2  # Minimum validations for certification

    # Keyword sets for sentiment analysis
    CONTRADICTION_KEYWORDS = ["contradict", "disagree", "refute", "oppose"]
    AGREEMENT_KEYWORDS = ["support", "agree", "confirm", "verify"]

    # Scoring weights (must sum to 1.0)
    SIGNAL_WEIGHT = 0.3  # Weight for signal_strength field
    CONFIDENCE_WEIGHT = 0.4  # Weight for confidence field
    NOTE_MATCH_WEIGHT = 0.3  # Weight for note sentiment analysis

    # Reputation system (placeholder)
    DEFAULT_VALIDATOR_REPUTATION = 0.5  # Until reputation tracking implemented
    MAX_NOTE_SCORE = 1.0  # Maximum boost/penalty from note analysis


@lru_cache(maxsize=512)
def _note_sentiment(note: str) -> float:
    """Return sentiment score for a note."""
    score = 0.0
    for keyword in Config.AGREEMENT_KEYWORDS:
        if keyword in note:
            score += 0.5
    for keyword in Config.CONTRADICTION_KEYWORDS:
        if keyword in note:
            score -= 0.5
    return max(min(score, Config.MAX_NOTE_SCORE), -Config.MAX_NOTE_SCORE)


@lru_cache(maxsize=512)
def _score_validation_cached(confidence: float, signal: float, note: str) -> float:
    """Memoized scoring helper used by :func:`score_validation`."""
    note_score = _note_sentiment(note)
    return (
        Config.CONFIDENCE_WEIGHT * confidence
        + Config.SIGNAL_WEIGHT * signal
        + Config.NOTE_MATCH_WEIGHT * (note_score + 1) / 2
    )


def compute_diversity_score(validations: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Compute a simple diversity metric for a list of validations.

    The score is based on the proportion of unique ``validator_id``,
    ``specialty`` and ``affiliation`` values present.  A value of ``1``
    indicates maximum diversity while ``0`` means no diversity.

    Parameters
    ----------
    validations:
        Sequence of validation dictionaries which may contain the keys
        ``validator_id``, ``specialty`` and ``affiliation``.

    Returns
    -------
    Dict[str, Any]
        Dictionary with the overall ``diversity_score`` in ``[0, 1]`` and
        optional ``flags`` if low diversity is detected.  Counts of unique
        fields are also returned for debugging purposes.
    """
    # For very large datasets consider numpy vectorization; profile with
    # ``cProfile`` to identify any set-building bottlenecks.

    total = len(validations) or 1

    ids = {v.get("validator_id") for v in validations if v.get("validator_id")}
    specialties = {v.get("specialty") for v in validations if v.get("specialty")}
    affiliations = {v.get("affiliation") for v in validations if v.get("affiliation")}
    types = {
        v.get("validator_type") or v.get("type")
        for v in validations
        if v.get("validator_type") or v.get("type")
    }

    ratios = [
        len(ids) / total,
        len(specialties) / total,
        len(affiliations) / total,
        (len(types) / total) if types else 1.0,
    ]
    diversity_score = max(0.0, min(1.0, sum(ratios) / len(ratios)))

    flags = []
    if diversity_score < 0.3:
        flags.append("low_diversity")

    return {
        "diversity_score": round(diversity_score, 3),
        "counts": {
            "unique_validators": len(ids),
            "unique_specialties": len(specialties),
            "unique_affiliations": len(affiliations),
            "unique_validator_types": len(types),
        },
        "flags": flags,
    }


def detect_semantic_contradictions(
    validations: List[Dict[str, Any]], threshold: float = 0.7
) -> List[Dict[str, Any]]:
    """Detect pairs of notes that are semantically similar yet opposing."""

    notes: List[Tuple[str, str]] = [
        (v.get("validator_id", f"v{i}"), str(v.get("note", "")).lower())
        for i, v in enumerate(validations)
        if v.get("note")
    ]

    contradictions: List[Dict[str, Any]] = []

    for (id1, n1), (id2, n2) in combinations(notes, 2):
        ratio = SequenceMatcher(None, n1, n2).ratio()
        if ratio >= threshold:
            has1 = any(k in n1 for k in Config.CONTRADICTION_KEYWORDS)
            has2 = any(k in n2 for k in Config.CONTRADICTION_KEYWORDS)
            if has1 != has2:
                contradictions.append(
                    {"validators": [id1, id2], "similarity": round(ratio, 3)}
                )

    return contradictions


def score_validation(val: Dict[str, Any]) -> float:
    """
    Score a single validation based on confidence, signal strength, and note sentiment.

    Args:
        val: Validation dictionary with optional fields:
             - confidence (float): Validator's confidence level (0.0-1.0)
             - signal_strength (float): Strength of supporting evidence (0.0-1.0)
             - note (str): Free-text validation commentary

    Returns:
        float: Quality score between 0.0 and 1.0

    Scientific Basis:
        Combines quantitative metrics (confidence, signal) with qualitative
        analysis (note sentiment) using configurable weights.
    """
    try:
        confidence = float(val.get("confidence", 0.5))
        signal = float(val.get("signal_strength", 0.5))
        note = str(val.get("note", "")).lower()

        final_score = _score_validation_cached(confidence, signal, note)

        return max(0.0, min(1.0, final_score))  # Ensure valid range

    except Exception as e:
        logger.warning(f"Malformed validation dict: {val} — {e}")
        return 0.0


def certify_validations(validations: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyze a list of validations and return certification summary.

    Args:
        validations: List of validation dictionaries

    Returns:
        Dict containing:
        - certified_validations: Original validations (for transparency)
        - consensus_score: Average quality score (0.0-1.0)
        - recommended_certification: Certification level string
        - flags: List of detected issues
        - diversity: Diversity analysis results

    Certification Levels:
        - "strong": High consensus, peer-reviewed quality
        - "provisional": Moderate consensus, needs more evidence
        - "experimental": Low consensus, early stage research
        - "disputed": Contains contradictions
        - "weak": Below experimental threshold
        - "insufficient_data": Too few validations
    """
    if not validations or len(validations) < Config.MIN_VALIDATIONS:
        return {
            "certified_validations": [],
            "consensus_score": 0.0,
            "recommended_certification": "insufficient_data",
            "flags": ["too_few_validations"],
            "diversity": {},
        }

    # Score each validation
    scores = [score_validation(v) for v in validations]
    avg_score = mean(scores)

    # Check for contradictions
    contradictory = any(
        any(
            keyword in str(v.get("note", "")).lower()
            for keyword in Config.CONTRADICTION_KEYWORDS
        )
        for v in validations
    )

    semantic_contradictions = detect_semantic_contradictions(validations)
    if semantic_contradictions:
        contradictory = True

    # Determine certification level
    if contradictory:
        certification = "disputed"
    elif avg_score >= Config.STRONG_THRESHOLD:
        certification = "strong"
    elif avg_score >= Config.PROVISIONAL_THRESHOLD:
        certification = "provisional"
    elif avg_score >= Config.EXPERIMENTAL_THRESHOLD:
        certification = "experimental"
    else:
        certification = "weak"

    # Compute diversity with error handling
    try:
        diversity_result = compute_diversity_score(validations)
    except Exception as e:
        logger.warning(f"Diversity analysis failed: {e}")
        diversity_result = {
            "diversity_score": 0.0,
            "flags": ["diversity_analysis_failed"],
        }

    # Reputation tracking
    try:
        rep_inputs = []
        for v, score in zip(validations, scores):
            item = dict(v)
            item.setdefault("hypothesis_id", "default")
            item.setdefault("score", score)
            rep_inputs.append(item)

        reputation_result = compute_validator_reputations(
            rep_inputs, {"default": avg_score}
        )
    except Exception as e:  # pragma: no cover - unexpected failure
        logger.warning(f"Reputation computation failed: {e}")
        reputation_result = {
            "validator_reputations": {},
            "flags": ["reputation_failed"],
            "stats": {},
        }

    # Temporal consistency analysis
    try:
        temporal_result = analyze_temporal_consistency(
            validations, reputation_result.get("validator_reputations", {})
        )
    except Exception as e:
        logger.warning(f"Temporal analysis failed: {e}")
        temporal_result = {
            "flags": ["temporal_analysis_failed"],
            "avg_delay_hours": 0.0,
            "consensus_volatility": 0.0,
            "weighted_volatility": 0.0,
            "timeline": [],
            "business_hours_ratio": 0.0,
        }

    # Cross-validation detection
    try:
        cross_validation_result = detect_score_coordination(rep_inputs)
    except Exception as e:
        logger.warning(f"Cross-validation detection failed: {e}")
        cross_validation_result = {"score_clusters": [], "flags": ["cross_val_failed"]}

    # Adjust certification based on low diversity
    if diversity_result.get("diversity_score", 0) < 0.3 and certification == "strong":
        certification = "provisional"

    # Compile results
    result = {
        "certified_validations": validations,
        "consensus_score": round(avg_score, 3),
        "recommended_certification": certification,
        "flags": [],
        "diversity": diversity_result,
        "reputations": reputation_result,
        "temporal_consistency": temporal_result,
        "cross_validation": cross_validation_result,
        "semantic_contradictions": semantic_contradictions,
    }

    if contradictory:
        result["flags"].append("has_contradiction")
    if semantic_contradictions:
        result["flags"].append("semantic_contradiction")
    if len(validations) < 3:
        result["flags"].append("limited_consensus")
    if "low_diversity" in diversity_result.get("flags", []):
        result["flags"].append("low_diversity")
    if cross_validation_result.get("flags"):
        result["flags"].extend(cross_validation_result["flags"])
    if temporal_result.get("flags"):
        result["flags"].extend(temporal_result["flags"])

    logger.info(
        f"Certified {len(validations)} validations: {certification} (score: {avg_score:.3f})"
    )

    return result


# v4.3 Enhancements implemented:
# - Validator reputation tracking
# - Temporal consistency analysis
# - Cross-validation pattern detection
# - Diversity scoring across validator types
# - Semantic contradiction checks

# Basic profiling hook. Execute this file directly to profile certification
# over a ``sample_validations.json`` dataset.
if __name__ == "__main__":  # pragma: no cover - manual profiling
    import cProfile
    import json
    import pstats
    from pathlib import Path

    sample = Path("sample_validations.json")
    data = json.loads(sample.read_text()) if sample.exists() else []
    profiler = cProfile.Profile()
    profiler.enable()
    certify_validations(data)
    profiler.disable()
    pstats.Stats(profiler).sort_stats("cumtime").print_stats(10)
