from __future__ import annotations

from typing import Any, Dict

from frontend_bridge import register_route
from hook_manager import HookManager
from optimization_engine import (
    tune_system_parameters,
    select_optimal_intervention,
)

# Exposed hook manager for external subscribers
ui_hook_manager = HookManager()


async def tune_parameters_ui(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Tune system parameters from a UI payload and emit an event."""
    metrics = payload.get("metrics", {})
    overrides = tune_system_parameters(metrics)
    await ui_hook_manager.trigger("parameters_tuned", overrides)
    return {"overrides": overrides}


async def select_intervention_ui(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Select an intervention from a UI payload and emit an event."""
    state = payload.get("state", {})
    action = select_optimal_intervention(state)
    await ui_hook_manager.trigger("intervention_selected", action)
    return {"action": action}


# Register routes with the frontend bridge
register_route("tune_parameters", tune_parameters_ui)
register_route("select_intervention", select_intervention_ui)
