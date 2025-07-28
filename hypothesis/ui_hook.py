from __future__ import annotations

from typing import Any, Dict

from frontend_bridge import register_route
from hook_manager import HookManager
from db_models import SessionLocal
from hypothesis_tracker import register_hypothesis, update_hypothesis_score

# Exposed hook manager for observers
ui_hook_manager = HookManager()


async def create_hypothesis_ui(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Create a hypothesis from a UI payload."""
    db = SessionLocal()
    try:
        hid = register_hypothesis(
            payload.get("text", ""),
            db,
            payload.get("metadata"),
        )
    finally:
        db.close()

    await ui_hook_manager.trigger("hypothesis_created", {"id": hid})
    return {"hypothesis_id": hid}


async def update_hypothesis_score_ui(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Update hypothesis score from UI payload."""
    db = SessionLocal()
    try:
        success = update_hypothesis_score(
            db,
            payload.get("hypothesis_id", ""),
            payload.get("new_score", 0.0),
            status=payload.get("status"),
            source_audit_id=payload.get("source_audit_id"),
            reason=payload.get("reason"),
            metadata_update=payload.get("metadata_update"),
        )
    finally:
        db.close()

    await ui_hook_manager.trigger(
        "hypothesis_score_updated", {"id": payload.get("hypothesis_id"), "success": success}
    )
    return {"success": success}


# Register with central frontend router
register_route("create_hypothesis", create_hypothesis_ui)
register_route("update_hypothesis_score", update_hypothesis_score_ui)
