from __future__ import annotations

from typing import Any, Dict
from sqlalchemy.orm import Session

from frontend_bridge import register_route_once
from hook_manager import HookManager
from . import log_event

ui_hook_manager = HookManager()


async def log_event_ui(
    payload: Dict[str, Any], db: Session, **_: Any
) -> Dict[str, Any]:
    """Persist an event triggered via the UI and emit a hook."""
    category = payload.get("category")
    if not isinstance(category, str) or not category:
        raise ValueError("'category' must be provided")

    event_payload = payload.get("payload")
    if not isinstance(event_payload, dict):
        raise ValueError("'payload' must be a dictionary")

    log_event(db, category, event_payload)

    await ui_hook_manager.trigger(
        "system_state_event_logged", {"category": category, **event_payload}
    )

    return {"category": category, **event_payload}


register_route_once(
    "log_event",
    log_event_ui,
    "Log a system state event",
    "system",
)
