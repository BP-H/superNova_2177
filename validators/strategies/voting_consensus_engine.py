"""
voting_consensus_engine.py — Multi-Validator Consensus Framework (v4.5)

Aggregates multiple validator opinions into consensus decisions using weighted
voting, quorum requirements, and sophisticated tie-breaking mechanisms.
Integrates with reputation, diversity, and temporal analysis systems.

Used in superNova_2177 to formalize multi-validator decision making.
"""

import logging
from typing import List, Dict, Any, Optional
from collections import Counter, defaultdict
from statistics import mean
from math import sqrt
from enum import Enum
from datetime import datetime

logger = logging.getLogger("superNova_2177.voting")
logger.propagate = False


class VotingMethod(Enum):
    """Supported voting aggregation methods."""

    WEIGHTED_AVERAGE = "weighted_average"
    MAJORITY_RULE = "majority_rule"
    SUPERMAJORITY = "supermajority"
    CONSENSUS_THRESHOLD = "consensus_threshold"
    REPUTATION_WEIGHTED = "reputation_weighted"
    RANKED_CHOICE = "ranked_choice"
    QUADRATIC = "quadratic"


class Config:
    """Configuration for voting consensus engine."""

    # Quorum requirements
    MIN_VALIDATORS_FOR_CONSENSUS = 3
    MIN_DIVERSITY_SCORE = 0.3
    MIN_TEMPORAL_TRUST = 0.5

    # Consensus thresholds
    MAJORITY_THRESHOLD = 0.51
    SUPERMAJORITY_THRESHOLD = 0.67
    CONSENSUS_THRESHOLD = 0.80

    # Reputation weighting
    MIN_REPUTATION_FOR_VOTE = 0.2
    MAX_REPUTATION_WEIGHT = 3.0

    # Tie-breaking preferences
    DEFAULT_TIE_BREAK_METHOD = "median"
    ABSTENTION_PENALTY = 0.1

    # Time decay for votes
    VOTE_DECAY_HALF_LIFE_DAYS = 30


def aggregate_validator_votes(
    votes: List[Dict[str, Any]],
    method: VotingMethod = VotingMethod.REPUTATION_WEIGHTED,
    reputations: Optional[Dict[str, float]] = None,
    diversity_score: Optional[float] = None,
    temporal_trust: Optional[Dict[str, float]] = None,
    *,
    cross_validation_history: Optional[List[Dict[str, Any]]] = None,
    current_time: Optional[datetime] = None,
) -> Dict[str, Any]:
    """
    Aggregate multiple validator votes into a consensus decision.

    Args:
        votes: List of vote dicts with validator_id, score, confidence, decision
        method: Voting aggregation method to use
        reputations: Optional reputation scores per validator
        diversity_score: Optional overall diversity score for the validator pool
        temporal_trust: Optional temporal trust scores per validator
        cross_validation_history: Optional list tracking past consensus results
        current_time: Optional datetime for time-decay calculations

    Returns:
        Dict containing:
        - consensus_decision: str or float
        - consensus_confidence: float (0.0-1.0)
        - voting_method: str
        - vote_breakdown: Dict with detailed results
        - flags: List of issues or warnings
        - quorum_met: bool
        - cross_validation: Optional consistency report
    """
    if not votes:
        return _empty_consensus_result("no_votes")

    # Validate inputs
    reputations = reputations or {}
    temporal_trust = temporal_trust or {}
    diversity_score = diversity_score or 0.0
    current_time = current_time or datetime.utcnow()

    # Filter valid votes
    valid_votes = []
    for vote in votes:
        validator_id = vote.get("validator_id")
        if not validator_id:
            continue

        # Check minimum reputation threshold
        reputation = reputations.get(validator_id, 0.5)
        if reputation < Config.MIN_REPUTATION_FOR_VOTE:
            continue

        valid_votes.append(vote)

    if len(valid_votes) < Config.MIN_VALIDATORS_FOR_CONSENSUS:
        return _empty_consensus_result("insufficient_quorum")

    # Apply delegation before processing
    valid_votes, reputations = _apply_delegation(valid_votes, reputations)

    # Check diversity and temporal requirements
    flags = []
    if diversity_score < Config.MIN_DIVERSITY_SCORE:
        flags.append("low_diversity_warning")

    avg_temporal_trust = mean(
        temporal_trust.get(v.get("validator_id"), 0.5) for v in valid_votes
    )
    if avg_temporal_trust < Config.MIN_TEMPORAL_TRUST:
        flags.append("low_temporal_trust")

    # Route to appropriate aggregation method
    if method == VotingMethod.WEIGHTED_AVERAGE:
        result = _weighted_average_consensus(valid_votes, reputations, current_time=current_time)
    elif method == VotingMethod.MAJORITY_RULE:
        result = _majority_rule_consensus(valid_votes, reputations, current_time=current_time)
    elif method == VotingMethod.SUPERMAJORITY:
        result = _supermajority_consensus(valid_votes, reputations, current_time=current_time)
    elif method == VotingMethod.CONSENSUS_THRESHOLD:
        result = _consensus_threshold_vote(valid_votes, reputations, current_time=current_time)
    elif method == VotingMethod.RANKED_CHOICE:
        result = _ranked_choice_consensus(valid_votes, reputations, current_time=current_time)
    elif method == VotingMethod.QUADRATIC:
        result = _quadratic_voting_consensus(valid_votes, reputations, current_time=current_time)
    elif method == VotingMethod.REPUTATION_WEIGHTED:
        result = _reputation_weighted_consensus(
            valid_votes, reputations, temporal_trust, current_time=current_time
        )
    else:
        result = _reputation_weighted_consensus(
            valid_votes, reputations, temporal_trust, current_time=current_time
        )

    # Add metadata
    result.update(
        {
            "voting_method": method.value,
            "total_validators": len(votes),
            "valid_votes": len(valid_votes),
            "quorum_met": len(valid_votes)
            >= Config.MIN_VALIDATORS_FOR_CONSENSUS,
            "diversity_score": diversity_score,
            "flags": flags,
        }
    )

    if cross_validation_history is not None:
        result["cross_validation"] = _update_cross_validation_history(
            cross_validation_history, {
                "consensus_decision": result.get("consensus_decision"),
                "consensus_confidence": result.get("consensus_confidence"),
            }
        )

    logger.info(
        "Consensus via %s: %s (confidence: %.3f)",
        method.value,
        result["consensus_decision"],
        result["consensus_confidence"],
    )

    return result


def _weighted_average_consensus(
    votes: List[Dict[str, Any]],
    reputations: Dict[str, float],
    *,
    current_time: datetime,
) -> Dict[str, Any]:
    """Simple weighted average of numerical scores."""
    weighted_sum = 0.0
    total_weight = 0.0
    confidences = []

    for vote in votes:
        validator_id = vote.get("validator_id")
        score = float(vote.get("score", 0.5))
        confidence = float(vote.get("confidence", 0.5))

        weight = reputations.get(validator_id, 0.5)
        weight = min(
            weight * Config.MAX_REPUTATION_WEIGHT,
            Config.MAX_REPUTATION_WEIGHT,
        )
        weight *= _time_decay_factor(
            vote.get("timestamp"), current_time, Config.VOTE_DECAY_HALF_LIFE_DAYS
        )

        weighted_sum += score * weight
        total_weight += weight
        confidences.append(confidence * weight)

    consensus_score = weighted_sum / total_weight if total_weight > 0 else 0.0
    consensus_confidence = (
        sum(confidences) / total_weight if total_weight > 0 else 0.0
    )

    return {
        "consensus_decision": round(consensus_score, 3),
        "consensus_confidence": round(consensus_confidence, 3),
        "vote_breakdown": {
            "method": "weighted_average",
            "total_weight": round(total_weight, 3),
            "raw_average": round(
                mean([float(v.get("score", 0.5)) for v in votes]), 3
            ),
        },
    }


def _majority_rule_consensus(
    votes: List[Dict[str, Any]],
    reputations: Dict[str, float],
    *,
    current_time: datetime,
) -> Dict[str, Any]:
    """Majority rule with reputation-weighted vote counting."""
    decisions = []
    total_weight = 0.0

    for vote in votes:
        validator_id = vote.get("validator_id")
        decision = vote.get("decision", "abstain")
        weight = reputations.get(validator_id, 0.5)
        decay = _time_decay_factor(
            vote.get("timestamp"), current_time, Config.VOTE_DECAY_HALF_LIFE_DAYS
        )
        weight *= decay

        decisions.extend([decision] * max(1, int(weight * 10)))  # Weight by reputation
        total_weight += weight

    if not decisions:
        return _empty_consensus_result("no_valid_decisions")

    decision_counts = Counter(decisions)
    winning_decision = decision_counts.most_common(1)[0][0]
    winning_count = decision_counts[winning_decision]

    confidence = winning_count / len(decisions)
    meets_majority = confidence >= Config.MAJORITY_THRESHOLD

    return {
        "consensus_decision": (
            winning_decision if meets_majority else "no_consensus"
        ),
        "consensus_confidence": round(confidence, 3),
        "vote_breakdown": {
            "method": "majority_rule",
            "decision_counts": dict(decision_counts),
            "majority_threshold": Config.MAJORITY_THRESHOLD,
            "meets_threshold": meets_majority,
        },
    }


def _supermajority_consensus(
    votes: List[Dict[str, Any]],
    reputations: Dict[str, float],
    *,
    current_time: datetime,
) -> Dict[str, Any]:
    """Supermajority rule (2/3+) with reputation weighting."""
    result = _majority_rule_consensus(votes, reputations, current_time=current_time)

    confidence = result["consensus_confidence"]
    meets_supermajority = confidence >= Config.SUPERMAJORITY_THRESHOLD

    result.update(
        {
            "consensus_decision": (
                result["consensus_decision"]
                if meets_supermajority
                else "no_consensus"
            ),
            "vote_breakdown": {
                **result["vote_breakdown"],
                "method": "supermajority",
                "supermajority_threshold": Config.SUPERMAJORITY_THRESHOLD,
                "meets_threshold": meets_supermajority,
            },
        }
    )

    return result


def _consensus_threshold_vote(
    votes: List[Dict[str, Any]],
    reputations: Dict[str, float],
    *,
    current_time: datetime,
) -> Dict[str, Any]:
    """High consensus threshold (80%+) for critical decisions."""
    result = _majority_rule_consensus(votes, reputations, current_time=current_time)

    confidence = result["consensus_confidence"]
    meets_consensus = confidence >= Config.CONSENSUS_THRESHOLD

    result.update(
        {
            "consensus_decision": (
                result["consensus_decision"]
                if meets_consensus
                else "no_consensus"
            ),
            "vote_breakdown": {
                **result["vote_breakdown"],
                "method": "consensus_threshold",
                "consensus_threshold": Config.CONSENSUS_THRESHOLD,
                "meets_threshold": meets_consensus,
            },
        }
    )

    return result


def _reputation_weighted_consensus(
    votes: List[Dict[str, Any]],
    reputations: Dict[str, float],
    temporal_trust: Dict[str, float],
    *,
    current_time: datetime,
) -> Dict[str, Any]:
    """Advanced consensus using reputation and temporal trust weighting."""
    weighted_scores = []
    total_weight = 0.0
    decision_weights = defaultdict(float)

    for vote in votes:
        validator_id = vote.get("validator_id")
        score = float(vote.get("score", 0.5))
        decision = vote.get("decision", "abstain")
        confidence = float(vote.get("confidence", 0.5))

        # Combine reputation and temporal trust
        reputation = reputations.get(validator_id, 0.5)
        temporal = temporal_trust.get(validator_id, 0.5)
        decay = _time_decay_factor(
            vote.get("timestamp"), current_time, Config.VOTE_DECAY_HALF_LIFE_DAYS
        )
        combined_weight = (reputation * 0.7 + temporal * 0.3) * confidence * decay

        weighted_scores.append(score * combined_weight)
        decision_weights[decision] += combined_weight
        total_weight += combined_weight

    # Calculate consensus score
    consensus_score = (
        sum(weighted_scores) / total_weight if total_weight > 0 else 0.0
    )

    # Find consensus decision
    if decision_weights:
        consensus_decision = max(decision_weights, key=decision_weights.get)
        decision_confidence = (
            decision_weights[consensus_decision] / total_weight
        )
    else:
        consensus_decision = "no_decision"
        decision_confidence = 0.0

    return {
        "consensus_decision": round(consensus_score, 3),
        "consensus_confidence": round(decision_confidence, 3),
        "vote_breakdown": {
            "method": "reputation_weighted",
            "total_weight": round(total_weight, 3),
            "decision_weights": {
                k: round(v, 3) for k, v in decision_weights.items()
            },
            "top_decision": consensus_decision,
        },
    }


def _ranked_choice_consensus(
    votes: List[Dict[str, Any]],
    reputations: Dict[str, float],
    *,
    current_time: datetime,
) -> Dict[str, Any]:
    """Ranked choice voting using Borda count."""
    ranking_scores = defaultdict(float)
    total_points = 0.0
    for vote in votes:
        ranking = vote.get("ranking")
        validator_id = vote.get("validator_id")
        if not ranking or not isinstance(ranking, list):
            continue
        weight = reputations.get(validator_id, 0.5)
        weight *= _time_decay_factor(
            vote.get("timestamp"), current_time, Config.VOTE_DECAY_HALF_LIFE_DAYS
        )
        n = len(ranking)
        for i, choice in enumerate(ranking):
            points = n - i
            ranking_scores[choice] += points * weight
            total_points += points * weight

    if not ranking_scores:
        return _empty_consensus_result("no_valid_rankings")

    winner = max(ranking_scores, key=ranking_scores.get)
    confidence = ranking_scores[winner] / total_points if total_points else 0.0

    return {
        "consensus_decision": winner,
        "consensus_confidence": round(confidence, 3),
        "vote_breakdown": {
            "method": "ranked_choice",
            "ranking_scores": {k: round(v, 3) for k, v in ranking_scores.items()},
        },
    }


def _quadratic_voting_consensus(
    votes: List[Dict[str, Any]],
    reputations: Dict[str, float],
    *,
    current_time: datetime,
) -> Dict[str, Any]:
    """Quadratic voting where credits translate to sqrt-weighted votes."""
    decision_weights = defaultdict(float)
    total_weight = 0.0
    for vote in votes:
        validator_id = vote.get("validator_id")
        decision = vote.get("decision")
        credits = float(vote.get("credits", 1))
        if not decision:
            continue
        weight = reputations.get(validator_id, 0.5) * sqrt(max(0.0, credits))
        weight *= _time_decay_factor(
            vote.get("timestamp"), current_time, Config.VOTE_DECAY_HALF_LIFE_DAYS
        )
        decision_weights[decision] += weight
        total_weight += weight

    if not decision_weights:
        return _empty_consensus_result("no_valid_decisions")

    winner = max(decision_weights, key=decision_weights.get)
    confidence = decision_weights[winner] / total_weight if total_weight else 0.0
    meets_majority = confidence >= Config.MAJORITY_THRESHOLD

    return {
        "consensus_decision": winner if meets_majority else "no_consensus",
        "consensus_confidence": round(confidence, 3),
        "vote_breakdown": {
            "method": "quadratic",
            "decision_weights": {k: round(v, 3) for k, v in decision_weights.items()},
            "meets_threshold": meets_majority,
        },
    }


def _empty_consensus_result(reason: str) -> Dict[str, Any]:
    """Return empty consensus result with specified reason."""
    return {
        "consensus_decision": "no_consensus",
        "consensus_confidence": 0.0,
        "voting_method": "none",
        "vote_breakdown": {"reason": reason},
        "flags": [reason],
        "quorum_met": False,
    }


def _time_decay_factor(
    timestamp: Optional[str],
    current_time: datetime,
    half_life: int,
) -> float:
    """Return decay multiplier based on age of the vote."""
    if not timestamp:
        return 1.0
    try:
        ts = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        age_days = (current_time - ts).days
        return 0.5 ** (age_days / half_life)
    except Exception:
        return 1.0


def _apply_delegation(
    votes: List[Dict[str, Any]],
    reputations: Dict[str, float],
) -> (List[Dict[str, Any]], Dict[str, float]):
    """Aggregate delegate weights into delegatee reputations."""
    updated_reps = reputations.copy()
    filtered_votes = []
    for v in votes:
        delegate_to = v.get("delegate_to")
        vid = v.get("validator_id")
        if delegate_to:
            weight = reputations.get(vid, 0.5)
            updated_reps[delegate_to] = updated_reps.get(delegate_to, 0.5) + weight
        else:
            filtered_votes.append(v)
    return filtered_votes, updated_reps


def _update_cross_validation_history(
    history: List[Dict[str, Any]], result: Dict[str, Any]
) -> Dict[str, Any]:
    """Update history list and return consistency information."""
    history.append(result)
    decisions = [r.get("consensus_decision") for r in history]
    counts = Counter(decisions)
    top, top_count = counts.most_common(1)[0]
    consistency = top_count / len(history)
    return {
        "history_size": len(history),
        "top_decision": top,
        "consistency_score": round(consistency, 3),
    }


def validate_voting_integrity(
    votes: List[Dict[str, Any]], reputations: Dict[str, float]
) -> Dict[str, Any]:
    """
    Check for voting manipulation, coordination, or suspicious patterns.

    Returns:
        Dict with integrity flags and recommendations
    """
    flags = []

    # Check for duplicate validators
    validator_ids = [
        v.get("validator_id") for v in votes if v.get("validator_id")
    ]
    if len(validator_ids) != len(set(validator_ids)):
        flags.append("duplicate_validators")

    # Check for suspicious score clustering
    scores = [float(v.get("score", 0.5)) for v in votes]
    if len(scores) > 2:
        score_range = max(scores) - min(scores)
        if score_range < 0.1:  # Very tight clustering
            flags.append("suspicious_score_clustering")

    # Check reputation distribution
    validator_reputations = [
        reputations.get(v.get("validator_id"), 0.5) for v in votes
    ]
    high_rep_count = sum(1 for r in validator_reputations if r > 0.8)
    if high_rep_count / len(validator_reputations) > 0.8:
        flags.append("high_reputation_concentration")

    return {
        "integrity_flags": flags,
        "vote_count": len(votes),
        "unique_validators": len(set(validator_ids)),
        "avg_reputation": (
            round(mean(validator_reputations), 3)
            if validator_reputations
            else 0.0
        ),
    }


# TODO v4.6:
# - Add ranked choice voting support
# - Implement quadratic voting mechanisms
# - Add delegation/proxy voting
# - Include time-decay for stale votes
# - Add cross-validation consensus tracking
