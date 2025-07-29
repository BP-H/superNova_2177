# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards
from __future__ import annotations

from typing import Any, Dict, TYPE_CHECKING

from sqlalchemy.orm import Session

from frontend_bridge import register_route_once

try:  # pragma: no cover - optional when running tests
    from superNova_2177 import follow_unfollow_user  # type: ignore
except Exception:  # pragma: no cover - fallback stub
    follow_unfollow_user = None  # type: ignore

if TYPE_CHECKING:  # pragma: no cover - for type hints only
    from db_models import Harmonizer


async def follow_user_ui(
    payload: Dict[str, Any], db: Session, current_user: "Harmonizer"
) -> Dict[str, str]:
    """Follow or unfollow ``payload['username']`` for ``current_user``."""
    username = payload["username"]
    if follow_unfollow_user is None:
        raise RuntimeError("follow_unfollow_user unavailable")
    return follow_unfollow_user(username, db=db, current_user=current_user)


register_route_once(
    "follow_user",
    follow_user_ui,
    "Follow or unfollow a user",
    "social",
)
