from __future__ import annotations

from typing import Any, Dict

from frontend_bridge import register_route
from hook_manager import HookManager
from . import quantum_prediction_engine

# Exposed hook manager so external modules can listen for prediction events
ui_hook_manager = HookManager()


async def quantum_prediction_ui(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Run quantum_prediction_engine on user_ids from payload."""
    user_ids = payload.get("user_ids", [])
    result = quantum_prediction_engine(user_ids)
    minimal = {
        "predicted_interactions": result.get("predicted_interactions", {}),
        "overall_quantum_coherence": result.get("overall_quantum_coherence", 0.0),
        "uncertainty_estimate": result.get("uncertainty_estimate", 0.0),
    }
    await ui_hook_manager.trigger("quantum_prediction_run", minimal)
    return minimal


# Register with the central frontend router
register_route("quantum_prediction", quantum_prediction_ui)
