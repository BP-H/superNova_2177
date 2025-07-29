from __future__ import annotations

import logging
from importlib import import_module
from typing import Any, Dict

from frontend_bridge import register_route_once
from hook_manager import HookManager
from hooks import events

from . import quantum_prediction_engine

# Shared hook manager for external modules
ui_hook_manager = HookManager()
logger = logging.getLogger(__name__)
logger.propagate = False


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


async def simulate_entanglement_ui(
    payload: Dict[str, Any],
    db,
    **_: Any,
) -> Dict[str, Any]:
    """Run social entanglement simulation between two users."""
    user1_id = payload["user1_id"]
    user2_id = payload["user2_id"]

    try:
        module = import_module("superNova_2177")
        simulate_social_entanglement = getattr(module, "simulate_social_entanglement")
    except (ImportError, AttributeError) as exc:  # pragma: no cover - logging only
        logger.error("Entanglement simulation unavailable: %s", exc)
        return {"error": "entanglement simulation unavailable"}

    result = simulate_social_entanglement(db, user1_id, user2_id)

    await ui_hook_manager.trigger(events.ENTANGLEMENT_SIMULATION_RUN, result)
    return result


# Register routes with frontend
register_route_once(
    "quantum_prediction",
    quantum_prediction_ui,
    "Run a quantum prediction",
    "quantum",
)
register_route_once(
    "simulate_entanglement",
    simulate_entanglement_ui,
    "Simulate quantum entanglement",
    "quantum",
)
