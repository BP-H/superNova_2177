from __future__ import annotations

from typing import Any, Dict, Optional

from hook_manager import HookManager
from prediction_manager import PredictionManager

# Exposed hook manager so external modules can listen for prediction events
ui_hook_manager = HookManager()

# Global manager instance. Real application should configure this on startup.
prediction_manager: Optional[PredictionManager] = None


async def store_prediction_ui(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Persist prediction data coming from the UI."""
    if prediction_manager is None:
        raise RuntimeError("prediction_manager not configured")

    prediction_data = payload.get("prediction", payload)
    prediction_id = prediction_manager.store_prediction(prediction_data)
    await ui_hook_manager.trigger("prediction_stored", {"prediction_id": prediction_id})
    return {"prediction_id": prediction_id}


async def get_prediction_ui(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Return prediction record identified by ``prediction_id``."""
    if prediction_manager is None:
        raise RuntimeError("prediction_manager not configured")

    prediction_id = payload["prediction_id"]
    record = prediction_manager.get_prediction(prediction_id)
    await ui_hook_manager.trigger("prediction_returned", record)
    return record or {}


async def update_prediction_status_ui(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Update prediction status based on UI request."""
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
