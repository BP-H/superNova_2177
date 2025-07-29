import asyncio
import datetime as _dt
import logging
from typing import Any, Dict, Optional

from dateutil import parser

from .api import api_call

logger = logging.getLogger(__name__)

_USER_CACHE: Dict[int, Dict[str, Any]] = {}


async def get_user_cached(user_id: int) -> Optional[Dict[str, Any]]:
    """Return user data from cache or backend."""
    if user_id in _USER_CACHE:
        return _USER_CACHE[user_id]
    data = await api_call("GET", f"/users/{user_id}")
    if data:
        _USER_CACHE[user_id] = data
    return data


async def get_username(user_id: int) -> str:
    """Resolve ``user_id`` to a username using cache when possible."""
    user = await get_user_cached(user_id)
    if user and user.get("username"):
        return str(user["username"])
    return str(user_id)


def humanize_timestamp(ts: str | _dt.datetime) -> str:
    """Return a human readable relative time like ``"2m ago"``."""
    if isinstance(ts, str):
        try:
            dt = parser.isoparse(ts)
        except Exception:  # pragma: no cover - invalid timestamp
            return ts
    else:
        dt = ts
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=_dt.timezone.utc)
    now = _dt.datetime.now(tz=dt.tzinfo)
    diff = now - dt
    sec = int(diff.total_seconds())
    if sec < 60:
        return f"{sec}s ago"
    if sec < 3600:
        return f"{sec // 60}m ago"
    if sec < 86400:
        return f"{sec // 3600}h ago"
    return f"{sec // 86400}d ago"
