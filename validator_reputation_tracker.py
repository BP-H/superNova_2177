"""
validator_reputation_tracker.py — Validator Reputation Scoring System (v4.1+)

Tracks and updates trust scores for validators based on validation history,
consistency, and certification alignment. Used in consensus weighting, peer
review selection, and governance escalation in superNova_2177.
"""

import logging
from typing import List, Dict, Any
from datetime import datetime
from statistics import mean

logger = logging.getLogger("superNova_2177.reputation")


# --- Configuration ---
class Config:
    DEFAULT_REPUTATION = 0.5
    CONTRADICTION_PENALTY = 0.2
    CERTIFICATION_REWARD = {
        "strong": 0.15,
        "provisional": 0.1,
        "experimental": 0.05,
        "disputed": -0.1,
        "weak": -0.15,
    }
    MAX_REPUTATION = 1.0
    MIN_REPUTATION = 0.0
    DECAY_HALF_LIFE_DAYS = 90
    MIN_VALIDATIONS_FOR_SCORING = 2


# --- Main Function ---
def update_validator_reputations(
    validations: List[Dict[str, Any]],
) -> Dict[str, float]:
    """
    Updates validator reputations based on validation quality and
    certification.

    Args:
        validations: List of dicts with fields:
            - validator_id: str
            - score: float (0.0-1.0)
            - certification: str (e.g., "strong", "provisional")
            - timestamp: str (ISO format, optional)
            - note: str (optional)
            - specialty: str (optional)

    Returns:
        Dict[str, float]: Updated validator reputation map.
    """
    reputations: Dict[str, List[float]] = {}
    specialties: Dict[str, str] = {}

    for v in validations:
        validator_id = v.get("validator_id")
        score = float(v.get("score", 0.5))
        cert = v.get("certification", "experimental")
        timestamp_str = v.get("timestamp")
        specialty = v.get("specialty")

        # Validate ID
        if not validator_id or not isinstance(validator_id, str):
            continue

        # Store specialty for diversity analysis
        if specialty:
            specialties[validator_id] = specialty

        # Decay modifier based on timestamp
        decay_factor = 1.0
        if timestamp_str:
            try:
                timestamp = datetime.fromisoformat(timestamp_str)
                age_days = (datetime.utcnow() - timestamp).days
                half_life = Config.DECAY_HALF_LIFE_DAYS
                decay_factor = 0.5 ** (age_days / half_life)
            except Exception as e:
                logger.warning(
                    f"Invalid timestamp for validator {validator_id}: {e}"
                )

        # Reputation delta
        reward = Config.CERTIFICATION_REWARD.get(cert, 0.0)
        penalty = (
            -Config.CONTRADICTION_PENALTY
            if "contradict" in v.get("note", "").lower()
            else 0.0
        )
        delta = (score + reward + penalty) * decay_factor

        reputations.setdefault(validator_id, []).append(delta)

    # Aggregate scores
    final_scores = {}
    for vid, deltas in reputations.items():
        if len(deltas) >= Config.MIN_VALIDATIONS_FOR_SCORING:
            rep = min(
                Config.MAX_REPUTATION,
                max(
                    Config.MIN_REPUTATION,
                    mean(deltas) + Config.DEFAULT_REPUTATION,
                ),
            )
            final_scores[vid] = rep
            logger.info(
                f"Validator {vid} updated reputation: {rep:.3f} — "
                f"Specialty: {specialties.get(vid, 'N/A')}"
            )

    logger.info(f"Updated reputations for {len(final_scores)} validators")
    return final_scores


# --- Placeholder Persistence Functions ---
def save_reputations(reputations: Dict[str, float], db) -> None:
    """Persist reputation scores using the provided session."""

    try:
        from db_models import ValidatorReputation
    except Exception as e:  # pragma: no cover - fallback handling
        logger.error(f"DB models unavailable: {e}")
        return

    for vid, rep in reputations.items():
        row = (
            db.query(ValidatorReputation)
            .filter(ValidatorReputation.validator_id == vid)
            .first()
        )
        if row:
            row.reputation = float(rep)
        else:
            row = ValidatorReputation(validator_id=vid, reputation=float(rep))
            db.add(row)

    db.commit()


def load_reputations(db) -> Dict[str, float]:
    """Return all saved reputation scores."""

    try:
        from db_models import ValidatorReputation
    except Exception as e:  # pragma: no cover - fallback handling
        logger.error(f"DB models unavailable: {e}")
        return {}

    rows = db.query(ValidatorReputation).all()
    return {row.validator_id: float(row.reputation) for row in rows}


# TODO (v4.2):
# - Implement semantic_contradiction_resolver integration
# - Add specialty/affiliation diversity tracking
# - Replace placeholders with real DB persistence layer
