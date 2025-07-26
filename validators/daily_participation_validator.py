"""Daily Participation Validator (RFC 002).

Checks that each user performs at least one action per calendar day and
flags users who have been inactive for longer than a configurable
threshold.
"""

import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

logger = logging.getLogger("superNova_2177.daily")


class Config:
    """Default configuration values."""

    # Number of days a user can be inactive before triggering an alert
    INACTIVITY_THRESHOLD_DAYS = 3


def evaluate_daily_participation(
    activity_log: List[Dict[str, Any]],
    inactivity_days: Optional[int] = None,
    *,
    current_time: Optional[datetime] = None,
) -> Dict[str, Any]:
    """Analyze user activity and return users inactive past the threshold.

    Args:
        activity_log: Sequence of records with ``user_id`` and ``timestamp``.
        inactivity_days: Days of allowed inactivity before a user is flagged.
        current_time: Evaluation timestamp (defaults to ``datetime.utcnow()``).

    Returns:
        Dictionary with ``inactive_users`` and ``total_users`` counts.
    """

    if not activity_log:
        return {"inactive_users": [], "total_users": 0, "flags": ["no_activity_records"]}

    threshold = inactivity_days or Config.INACTIVITY_THRESHOLD_DAYS
    now = current_time or datetime.utcnow()

    last_seen: Dict[str, datetime] = {}
    for record in activity_log:
        user_id = record.get("user_id")
        ts_raw = record.get("timestamp")
        if not user_id or not ts_raw:
            continue
        try:
            ts = datetime.fromisoformat(ts_raw.replace("Z", "+00:00"))
        except Exception as e:  # pragma: no cover - log malformed timestamps
            logger.warning(f"Invalid timestamp for user {user_id}: {ts_raw} - {e}")
            continue
        prev = last_seen.get(user_id)
        if not prev or ts > prev:
            last_seen[user_id] = ts

    inactive_users = [
        uid
        for uid, ts in last_seen.items()
        if (now.date() - ts.date()).days > threshold
    ]

    logger.info(
        "Daily participation check: %d/%d inactive users", len(inactive_users), len(last_seen)
    )

    return {
        "inactive_users": inactive_users,
        "total_users": len(last_seen),
        "flags": ["inactive_users"] if inactive_users else [],
    }
