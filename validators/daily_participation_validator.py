"""Daily Participation Validator — detect prolonged user inactivity.

Implements the rule described in RFC 002. The validator checks user
activity logs and returns identifiers for participants who have not
been active for more than a configurable number of days.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger("superNova_2177.participation")
logger.propagate = False


class Config:
    """Configuration constants."""

    DEFAULT_THRESHOLD_DAYS = 7


def detect_inactive_users(
    activity_logs: List[Dict[str, Any]],
    *,
    threshold_days: int | None = None,
    current_time: Optional[datetime] = None,
) -> List[str]:
    """Return user IDs with no activity for more than ``threshold_days``.

    Parameters
    ----------
    activity_logs:
        Sequence of log dictionaries containing ``user_id`` and
        ``timestamp`` fields in ISO format.
    threshold_days:
        Days of inactivity required to flag a user. If omitted, the
        value from :class:`Config` is used.
    current_time:
        Reference ``datetime`` for computing inactivity. Defaults to
        ``datetime.utcnow``.
    """

    threshold_days = (
        threshold_days if threshold_days is not None else Config.DEFAULT_THRESHOLD_DAYS
    )
    now = current_time or datetime.utcnow()

    last_seen: Dict[str, datetime] = {}
    for entry in activity_logs:
        user = entry.get("user_id")
        ts_raw = entry.get("timestamp")
        if not user or not ts_raw:
            continue
        try:
            ts = datetime.fromisoformat(ts_raw.replace("Z", "+00:00"))
        except Exception:  # pragma: no cover - ignore malformed timestamps
            logger.debug("Invalid timestamp %s for user %s", ts_raw, user)
            continue
        if user not in last_seen or ts > last_seen[user]:
            last_seen[user] = ts

    inactive = []
    for user, ts in last_seen.items():
        if (now - ts).days > threshold_days:
            inactive.append(user)

    return sorted(inactive)
