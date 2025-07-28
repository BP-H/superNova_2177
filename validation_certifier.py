"""
validation_certifier.py — Unified Validation & Integrity Analysis Pipeline (v4.6)

Complete validation orchestrator that analyzes validation records through multiple
dimensions: quality scoring, diversity analysis, reputation tracking, temporal
consistency, and coordination detection.

This is the primary interface for comprehensive validation analysis in superNova_2177.
"""

import logging
from typing import List, Dict, Any, Tuple
from datetime import datetime
from statistics import mean

# Import all v4.x analysis modules
from diversity_analyzer import compute_diversity_score
from validators.reputation_influence_tracker import compute_validator_reputations
from network.network_coordination_detector import analyze_coordination_patterns
from temporal_consistency_checker import analyze_temporal_consistency, assess_temporal_trust_factor

logger = logging.getLogger("superNova_2177.certifier")
logger.propagate = False

class Config:
    """Unified configuration for all validation analysis components."""

    # Certification thresholds (0.0 - 1.0)
    STRONG_THRESHOLD = 0.85
    PROVISIONAL_THRESHOLD = 0.65
    EXPERIMENTAL_THRESHOLD = 0.45

    # Validation requirements
    MIN_VALIDATIONS = 2

    # Quality scoring weights
    SIGNAL_WEIGHT = 0.3
    CONFIDENCE_WEIGHT = 0.4
    NOTE_MATCH_WEIGHT = 0.3

    # Integrity analysis weights
    REPUTATION_WEIGHT = 0.3
    DIVERSITY_WEIGHT = 0.25
    TEMPORAL_WEIGHT = 0.25
    COORDINATION_WEIGHT = 0.2

    # Risk thresholds
    HIGH_RISK_THRESHOLD = 0.7
    MEDIUM_RISK_THRESHOLD = 0.4

    # Keywords for sentiment analysis
    CONTRADICTION_KEYWORDS = ["contradict", "disagree", "refute", "oppose"]
    AGREEMENT_KEYWORDS = ["support", "agree", "confirm", "verify"]

    MAX_NOTE_SCORE = 1.0

def score_validation(val: Dict[str, Any]) -> float:
    """
    Score a single validation based on confidence, signal strength, and note sentiment.

    Args:
        val: Validation dictionary with confidence, signal_strength, note fields

    Returns:
        float: Quality score between 0.0 and 1.0
    """
    try:
        confidence = float(val.get("confidence", 0.5))
        signal = float(val.get("signal_strength", 0.5))
        note = str(val.get("note", "")).lower()

        # Sentiment analysis on validation note
        note_score = 0.0
        for keyword in Config.AGREEMENT_KEYWORDS:
            if keyword in note:
                note_score += 0.5
        for keyword in Config.CONTRADICTION_KEYWORDS:
            if keyword in note:
                note_score -= 0.5

        # Clamp note score
        note_score = max(min(note_score, Config.MAX_NOTE_SCORE), -Config.MAX_NOTE_SCORE)

        # Weighted combination
        final_score = (
            Config.CONFIDENCE_WEIGHT * confidence +
            Config.SIGNAL_WEIGHT * signal +
            Config.NOTE_MATCH_WEIGHT * (note_score + 1) / 2
        )

        return max(0.0, min(1.0, final_score))

    except Exception as e:
        logger.warning(f"Malformed validation dict: {val} — {e}")
        return 0.0

def calculate_integrity_score(
   diversity_result: Dict[str, Any],
   reputation_result: Dict[str, Any],
   temporal_result: Dict[str, Any],
   coordination_result: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Calculate overall integrity score from all analysis components.

    Args:
        diversity_result: Output from compute_diversity_score
        reputation_result: Output from compute_validator_reputations
        temporal_result: Output from analyze_temporal_consistency
        coordination_result: Output from analyze_coordination_patterns

    Returns:
        Dict with integrity analysis and overall score
    """
    # Extract key metrics
    diversity_score = diversity_result.get("diversity_score", 0.0)

    reputation_stats = reputation_result.get("stats", {})
    avg_reputation = reputation_stats.get("avg_reputation", 0.5)

    temporal_trust = assess_temporal_trust_factor(temporal_result)

    coordination_risk = coordination_result.get("overall_risk_score", 0.0)
    coordination_safety = max(0.0, 1.0 - coordination_risk)

    # Weighted integrity score
    integrity_score = (
        Config.DIVERSITY_WEIGHT * diversity_score +
        Config.REPUTATION_WEIGHT * avg_reputation +
        Config.TEMPORAL_WEIGHT * temporal_trust +
        Config.COORDINATION_WEIGHT * coordination_safety
    )

    # Collect all risk flags
    all_risk_flags = []
    all_risk_flags.extend(diversity_result.get("flags", []))
    all_risk_flags.extend(reputation_result.get("flags", []))
    all_risk_flags.extend(temporal_result.get("flags", []))
    all_risk_flags.extend(coordination_result.get("flags", []))

    # Determine risk level
    risk_level = "low"
    if integrity_score < Config.MEDIUM_RISK_THRESHOLD:
        risk_level = "high"
    elif integrity_score < Config.HIGH_RISK_THRESHOLD:
        risk_level = "medium"

    return {
        "overall_integrity_score": round(integrity_score, 3),
        "risk_level": risk_level,
        "component_scores": {
            "diversity": diversity_score,
            "reputation": avg_reputation,
            "temporal_trust": temporal_trust,
            "coordination_safety": coordination_safety
        },
        "risk_flags": all_risk_flags,
        "flag_count": len(all_risk_flags)
    }


def run_full_integrity_analysis(
    validations: List[Dict[str, Any]],
    avg_score: float,
    certification: str,
) -> Tuple[Dict[str, Any], List[str], str]:
    """Run integrity analysis modules and update certification."""

    consensus_scores = {"default_hypothesis": avg_score}

    # Run diversity, coordination, and reputation analysis concurrently
    import concurrent.futures

    with concurrent.futures.ThreadPoolExecutor() as executor:
        diversity_future = executor.submit(compute_diversity_score, validations)
        coordination_future = executor.submit(
            analyze_coordination_patterns, validations
        )
        reputation_future = executor.submit(
            compute_validator_reputations,
            validations,
            consensus_scores,
        )

        # Reputation is needed for temporal analysis
        reputation_result = reputation_future.result()

        temporal_future = executor.submit(
            analyze_temporal_consistency,
            validations,
            reputation_result.get("validator_reputations", {}),
        )

        diversity_result = diversity_future.result()
        coordination_result = coordination_future.result()
        temporal_result = temporal_future.result()

    integrity_analysis = calculate_integrity_score(
        diversity_result,
        reputation_result,
        temporal_result,
        coordination_result,
    )

    recommendations: List[str] = []
    integrity_score = integrity_analysis.get("overall_integrity_score", 1.0)
    risk_level = integrity_analysis.get("risk_level", "low")

    if risk_level == "high":
        if certification in ["strong", "provisional"]:
            certification = "experimental"
            recommendations.append(
                "Certification downgraded due to high integrity risk",
            )
    elif risk_level == "medium":
        if certification == "strong":
            certification = "provisional"
            recommendations.append(
                "Certification downgraded due to medium integrity risk",
            )

    if diversity_result.get("diversity_score", 0) < 0.3:
        recommendations.append(
            "Increase validator diversity across specialties and affiliations",
        )

    if coordination_result.get("overall_risk_score", 0) > 0.5:
        recommendations.append(
            "Investigate potential validator coordination patterns",
        )

    if temporal_result.get("consensus_volatility", 0) > 0.4:
        recommendations.append(
            "Review temporal consistency of validation submissions",
        )

    return integrity_analysis, recommendations, certification

def certify_validations_comprehensive(
   validations: List[Dict[str, Any]],
   enable_full_analysis: bool = True
) -> Dict[str, Any]:
    """
    Complete validation certification with full integrity analysis.

    Main certification logic used by v4.6+. If enable_full_analysis is False, 
    runs only basic scoring; otherwise, performs full integrity diagnostics 
    across all modules.

    Args:
        validations: List of validation dictionaries
        enable_full_analysis: If True, runs all v4.x analysis modules

    Returns:
        Dict containing:
        - Basic certification (consensus_score, recommended_certification)
        - Full integrity analysis (diversity, reputation, temporal, coordination)
        - Risk assessment and flags
        - Actionable recommendations
    """
    if not validations or len(validations) < Config.MIN_VALIDATIONS:
        return {
            "certified_validations": [],
            "consensus_score": 0.0,
            "recommended_certification": "insufficient_data",
            "flags": ["too_few_validations"],
            "integrity_analysis": {},
            "recommendations": ["Collect more validations before certification"]
        }

    # Step 1: Basic validation scoring
    scores = [score_validation(v) for v in validations]
    avg_score = mean(scores)

    # TODO: In future versions, upgrade to SUPERMAJORITY_THRESHOLD (e.g., 0.66 or 0.75 or anything else) instead of fixed 0.66
    # SUPERMAJORITY_THRESHOLD = 0.75  # Placeholder for symbolic governance upgrade (currently unused)
    
    # Binary trust scaffold for future decentralized ownership verification
    binary_score = 100 if avg_score >= 0.75 else 0


    # Step 2: Check for contradictions
    contradictory = any(
        any(keyword in str(v.get("note", "")).lower() for keyword in Config.CONTRADICTION_KEYWORDS)
        for v in validations
    )

    # Step 3: Determine base certification level
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

    # Step 4: Full integrity analysis (if enabled)
    integrity_analysis = {}
    recommendations = []

    if enable_full_analysis:

        try:
            (
                integrity_analysis,
                recommendations,
                certification,
            ) = run_full_integrity_analysis(
                validations,
                avg_score,
                certification,
            )
        except Exception as e:
            logger.exception("Integrity analysis failed")
            integrity_analysis = {"error": "Analysis failed", "details": str(e)}
            recommendations.append("Manual review recommended due to analysis failure")

    # Step 5: Compile final results
    flags = []
    if contradictory:
        flags.append("has_contradiction")
    if len(validations) < 3:
        flags.append("limited_consensus")

    # Add integrity flags if analysis was performed
    if integrity_analysis and "risk_flags" in integrity_analysis:
        flags.extend(integrity_analysis["risk_flags"])

    result = {
        "certified_validations": validations,
        "consensus_score": binary_score,
        "recommended_certification": certification,
        "flags": flags,
        "integrity_analysis": integrity_analysis,
        "recommendations": recommendations or ["No specific recommendations"],
        "analysis_timestamp": datetime.utcnow().isoformat(),
        "validator_count": len(set(v.get("validator_id") for v in validations if v.get("validator_id")))
    }

    logger.info(f"Comprehensive certification complete: {certification} "
               f"(score: {avg_score:.3f}, integrity: {integrity_analysis.get('overall_integrity_score', 'N/A')}, "
               f"validators: {result['validator_count']}, flags: {len(flags)})")

    return result

# Legacy compatibility function
def certify_validations(validations: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Legacy interface for basic validation certification.

    Args:
        validations: List of validation dictionaries

    Returns:
        Dict with basic certification results (maintains backward compatibility)
    """
    full_result = certify_validations_comprehensive(validations, enable_full_analysis=False)

    # Return simplified result for backward compatibility
    return {
        "certified_validations": full_result["certified_validations"],
        "consensus_score": full_result["consensus_score"],
        "recommended_certification": full_result["recommended_certification"],
        "flags": full_result["flags"]
    }

# Main interface function - use this for new implementations
def analyze_validation_integrity(validations: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Primary interface for complete validation integrity analysis.

    This is the main entry point for the unified validation pipeline.
    Provides comprehensive analysis including quality, diversity, reputation,
    temporal consistency, and coordination detection.

    Args:
        validations: List of validation dictionaries with fields:
                    - validator_id, score, confidence, signal_strength, note,
                    - timestamp, specialty, affiliation, hypothesis_id

    Returns:
        Dict with complete analysis results and actionable recommendations
    """
    return certify_validations_comprehensive(validations, enable_full_analysis=True)

# TODO v5.0:
# - Add machine learning models for advanced pattern detection
# - Implement real-time validation monitoring dashboard
# - Add integration with external reputation systems
# - Include semantic analysis using sentence embeddings
# - Add automated validator onboarding and training recommendations
