from __future__ import annotations

from typing import Any, Dict

from sqlalchemy.orm import Session

from frontend_bridge import register_route_once
from hook_manager import HookManager
from . import explain_validation_reasoning

ui_hook_manager = HookManager()


async def explain_validation_ui(payload: Dict[str, Any], db: Session) -> Dict[str, Any]:
    """Run :func:`explain_validation_reasoning` with UI payload data."""
    hypothesis_id = payload.get("hypothesis_id")
    validation_id = payload.get("validation_id")
    result = explain_validation_reasoning(hypothesis_id, validation_id, db)
    await ui_hook_manager.trigger("validation_explained", result)
    return result


async def _explain_validation_route(
    payload: Dict[str, Any], db: Session
) -> Dict[str, Any]:
    return await explain_validation_ui(payload, db)


register_route_once(
    "explain_validation_reasoning",
    _explain_validation_route,
    "Explain validation reasoning",
    "audit",
)
