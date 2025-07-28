"""
reputation_influence_tracker.py — Validator Reputation Scoring (v4.4)

Calculates reputation scores for validators based on agreement with consensus, 
temporal behavior, and diversity contribution across multiple validations. 
Flags unusual influence patterns and helps stabilize scientific audits.

Used in superNova_2177 to weight validations and detect manipulation.
"""

import logging
from typing import List, Dict, Any, Optional
from collections import defaultdict
from statistics import mean, stdev
from datetime import datetime

logger = logging.getLogger("superNova_2177.reputation")
logger.propagate = False

class Config:
    DEFAULT_REPUTATION = 0.5
    MAX_REPUTATION = 1.0
    MIN_REPUTATION = 0.0

    # Reputation adjustment weights (must sum to 1.0)
    AGREEMENT_WEIGHT = 0.5
    TEMPORAL_TRUST_WEIGHT = 0.3
    DIVERSITY_BONUS_WEIGHT = 0.2

    # Validation requirements
    MIN_VALIDATIONS_REQUIRED = 3

    # Suspicious behavior thresholds
    HIGH_AGREEMENT_THRESHOLD = 0.9
    LOW_DIVERSITY_THRESHOLD = 0.1
    EXTREME_DEVIATION_THRESHOLD = 0.8

    # Reputation decay
    DECAY_HALF_LIFE_DAYS = 90

def compute_validator_reputations(
    all_validations: List[Dict[str, Any]],
    consensus_scores: Dict[str, float],
    temporal_trust: Optional[Dict[str, float]] = None,
    diversity_scores: Optional[Dict[str, float]] = None,
    *,
    current_time: Optional[datetime] = None,
    half_life_days: Optional[float] = None
) -> Dict[str, Any]:
    """
    Compute reputation scores for each validator based on their validation patterns.

    Args:
        all_validations: List of validations across multiple hypotheses
        consensus_scores: Average score per hypothesis_id
        temporal_trust: Optional trust factors for validators (0.0-1.0)
        diversity_scores: Optional diversity contributions per validator (0.0-1.0)
        current_time: Evaluation time for decay calculation (defaults to now)
        half_life_days: Half-life for decay factor in days

    Returns:
        Dict with:
        - validator_reputations: Dict[str, float]
        - flags: List of suspicious behavior patterns
        - stats: Summary statistics
    """
    if not all_validations:
        logger.warning("No validations provided for reputation computation")
        return {
            "validator_reputations": {},
            "flags": ["no_validations"],
            "stats": {"total_validators": 0, "avg_reputation": 0.0}
        }

    if not consensus_scores:
        logger.warning("No consensus scores provided")
        return {
            "validator_reputations": {},
            "flags": ["no_consensus_data"],
            "stats": {"total_validators": 0, "avg_reputation": 0.0}
        }

    temporal_trust = temporal_trust or {}
    diversity_scores = diversity_scores or {}
    current_time = current_time or datetime.utcnow()
    half_life = half_life_days or Config.DECAY_HALF_LIFE_DAYS
    if half_life <= 0:
        half_life = Config.DECAY_HALF_LIFE_DAYS

    validator_scores = defaultdict(list)
    validator_deviations = defaultdict(list)
    last_timestamps: Dict[str, datetime] = {}

    for v in all_validations:
        try:
            validator = v.get("validator_id")
            hypothesis = v.get("hypothesis_id")
            val_score = float(v.get("score", 0.5))
            timestamp_str = v.get("timestamp")

            if not validator or not hypothesis:
                continue

            consensus = consensus_scores.get(hypothesis)
            if consensus is None:
                continue

            deviation = abs(val_score - consensus)
            agreement_score = max(0.0, 1.0 - deviation)

            validator_scores[validator].append(agreement_score)
            validator_deviations[validator].append(deviation)
            if timestamp_str:
                try:
                    ts = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
                    prev = last_timestamps.get(validator)
                    if not prev or ts > prev:
                        last_timestamps[validator] = ts
                except Exception as e:
                    logger.warning(f"Invalid timestamp for validator {validator}: {e}")

        except (ValueError, TypeError) as e:
            logger.warning(f"Invalid validation data: {v} - {e}")
            continue

    reputations = {}
    flags = []

    for validator, agreements in validator_scores.items():
        try:
            if len(agreements) < Config.MIN_VALIDATIONS_REQUIRED:
                reputations[validator] = Config.DEFAULT_REPUTATION
                continue

            base_agreement = mean(agreements)
            temporal = max(0.0, min(1.0, temporal_trust.get(validator, 0.5)))
            diversity = max(0.0, min(1.0, diversity_scores.get(validator, 0.0)))

            reputation = (
                Config.AGREEMENT_WEIGHT * base_agreement +
                Config.TEMPORAL_TRUST_WEIGHT * temporal +
                Config.DIVERSITY_BONUS_WEIGHT * diversity
            )

            final_reputation = max(Config.MIN_REPUTATION, min(Config.MAX_REPUTATION, reputation))

            ts = last_timestamps.get(validator)
            if ts:
                age_days = (current_time - ts).days
                decay_factor = 0.5 ** (age_days / half_life)
                final_reputation *= decay_factor

            reputations[validator] = round(
                max(Config.MIN_REPUTATION, min(Config.MAX_REPUTATION, final_reputation)),
                3,
            )

            avg_deviation = mean(validator_deviations[validator])

            if base_agreement > Config.HIGH_AGREEMENT_THRESHOLD and diversity < Config.LOW_DIVERSITY_THRESHOLD:
                flags.append(f"validator_{validator}_suspicious_agreement_pattern")

            if avg_deviation > Config.EXTREME_DEVIATION_THRESHOLD:
                flags.append(f"validator_{validator}_extreme_deviation_pattern")

            if temporal < 0.2:
                flags.append(f"validator_{validator}_temporal_anomaly")

        except Exception as e:
            logger.error(f"Error computing reputation for validator {validator}: {e}")
            reputations[validator] = Config.DEFAULT_REPUTATION

    reputation_values = list(reputations.values())
    stats = {
        "total_validators": len(reputations),
        "avg_reputation": round(mean(reputation_values), 3) if reputation_values else 0.0,
        "reputation_std": round(stdev(reputation_values), 3) if len(reputation_values) > 1 else 0.0,
        "high_reputation_count": sum(1 for r in reputation_values if r > 0.8),
        "low_reputation_count": sum(1 for r in reputation_values if r < 0.3)
    }

    logger.info(f"Computed reputations for {len(reputations)} validators. "
                f"Avg: {stats['avg_reputation']}, Flags: {len(flags)}")

    return {
        "validator_reputations": reputations,
        "flags": flags,
        "stats": stats
    }

def get_reputation_weighted_score(
    validations: List[Dict[str, Any]],
    reputations: Dict[str, float]
) -> float:
    """
    Calculate a reputation-weighted consensus score for a set of validations.

    Args:
        validations: List of validation dicts with validator_id and score
        reputations: Dict mapping validator_id to reputation score

    Returns:
        float: Weighted consensus score (0.0-1.0)
    """
    if not validations:
        return 0.0

    weighted_sum = 0.0
    total_weight = 0.0

    for v in validations:
        try:
            validator_id = v.get("validator_id")
            score = float(v.get("score", 0.5))

            if validator_id:
                reputation = reputations.get(validator_id, Config.DEFAULT_REPUTATION)
                weighted_sum += score * reputation
                total_weight += reputation

        except (ValueError, TypeError):
            continue

    return round(weighted_sum / total_weight, 3) if total_weight > 0 else 0.0

# TODO v4.5:
# - Add cross-validation consistency tracking
# - Include network analysis for coordination detection
