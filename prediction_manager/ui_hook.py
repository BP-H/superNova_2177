from __future__ import annotations

from typing import Any, Dict, Optional

from hook_manager import HookManager
from . import PredictionManager

# Hook manager to allow observers to listen for prediction events
ui_hook_manager = HookManager()

# Global PredictionManager instance, configured by the application
prediction_manager: Optional[PredictionManager] = None


async def save_prediction_ui(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Persist prediction data coming from the UI."""
    if prediction_manager is None:
        raise RuntimeError("prediction_manager not configured")

    data = payload.get("prediction", payload)
    prediction_id = prediction_manager.store_prediction(data)
    await ui_hook_manager.trigger("prediction_saved", {"prediction_id": prediction_id})
    return {"prediction_id": prediction_id}


async def get_prediction_ui(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Return prediction data previously stored."""
    if prediction_manager is None:
        raise RuntimeError("prediction_manager not configured")

    prediction_id = payload["prediction_id"]
    record = prediction_manager.get_prediction(prediction_id)
    await ui_hook_manager.trigger("prediction_loaded", record)
    return record or {}
