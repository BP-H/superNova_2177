from __future__ import annotations

from typing import Any, Dict, Optional

from frontend_bridge import register_route_once
from hook_manager import HookManager
from . import PredictionManager

ui_hook_manager = HookManager()

prediction_manager: Optional[PredictionManager] = None


async def store_prediction_ui(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Persist prediction data from the UI and return its identifier."""
    if prediction_manager is None:
        raise RuntimeError("prediction_manager not configured")

    prediction_data = payload.get("prediction", payload)
    prediction_id = prediction_manager.store_prediction(prediction_data)
    await ui_hook_manager.trigger("prediction_stored", {"prediction_id": prediction_id})
    return {"prediction_id": prediction_id}


async def get_prediction_ui(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Return minimal prediction info identified by ``prediction_id``."""
    if prediction_manager is None:
        raise RuntimeError("prediction_manager not configured")

    prediction_id = payload["prediction_id"]
    record = prediction_manager.get_prediction(prediction_id)
    status = record.get("status") if record else None
    await ui_hook_manager.trigger(
        "prediction_returned", {"prediction_id": prediction_id, "status": status}
    )
    return {"prediction_id": prediction_id, "status": status}


async def update_prediction_status_ui(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Update prediction status and emit minimal result."""
    if prediction_manager is None:
        raise RuntimeError("prediction_manager not configured")

    prediction_id = payload["prediction_id"]
    new_status = payload.get("status", "pending")
    outcome = payload.get("actual_outcome")
    prediction_manager.update_prediction_status(
        prediction_id, new_status, actual_outcome=outcome
    )
    await ui_hook_manager.trigger(
        "prediction_status_updated",
        {"prediction_id": prediction_id, "status": new_status},
    )
    return {"prediction_id": prediction_id, "status": new_status}


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
    "update_prediction_status",
    update_prediction_status_ui,
    "Update prediction status",
    "prediction",
)
