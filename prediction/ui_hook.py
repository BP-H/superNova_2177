from __future__ import annotations

from typing import Any, Dict, Optional

from frontend_bridge import register_route_once
from hook_manager import HookManager
from prediction_manager import PredictionManager

# Hook manager to allow external listeners
ui_hook_manager = HookManager()

# Global PredictionManager instance injected at runtime
prediction_manager: Optional[PredictionManager] = None


async def store_prediction_ui(payload: Dict[str, Any], db: Any) -> Dict[str, Any]:
    """Persist prediction data coming from the UI."""
    _ = db  # unused placeholder for symmetry
    if prediction_manager is None:
        raise RuntimeError("prediction_manager not configured")

    prediction_data = payload.get("prediction", payload)
    prediction_id = prediction_manager.store_prediction(prediction_data)
    await ui_hook_manager.trigger("prediction_stored", {"prediction_id": prediction_id})
    return {"prediction_id": prediction_id}


async def get_prediction_ui(payload: Dict[str, Any], db: Any) -> Dict[str, Any]:
    """Return prediction record identified by ``prediction_id``."""
    _ = db
    if prediction_manager is None:
        raise RuntimeError("prediction_manager not configured")

    prediction_id = payload["prediction_id"]
    record = prediction_manager.get_prediction(prediction_id)
    await ui_hook_manager.trigger("prediction_returned", record)
    return record or {}


async def schedule_audit_proposal_ui(
    payload: Dict[str, Any], db: Any
) -> Dict[str, Any]:
    """Schedule an annual audit proposal via the PredictionManager."""
    _ = db
    if prediction_manager is None:
        raise RuntimeError("prediction_manager not configured")

    proposal_id = prediction_manager.schedule_annual_audit_proposal()
    await ui_hook_manager.trigger(
        "audit_proposal_scheduled", {"proposal_id": proposal_id}
    )
    return {"proposal_id": proposal_id}


# Register handlers with the frontend bridge
register_route_once(
    "store_prediction",
    store_prediction_ui,
    "Persist prediction data",
    "prediction",
)
register_route_once(
    "get_prediction",
    get_prediction_ui,
    "Retrieve a stored prediction",
    "prediction",
)
register_route_once(
    "schedule_audit_proposal",
    schedule_audit_proposal_ui,
    "Schedule an annual audit proposal",
    "prediction",
)
