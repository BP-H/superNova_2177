from __future__ import annotations

from typing import Any, Dict

from frontend_bridge import register_route_once
from hook_manager import HookManager
from optimization_engine import tune_system_parameters

# Exposed hook manager so external modules can subscribe to optimization events
ui_hook_manager = HookManager()


async def tune_parameters_ui(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Run parameter tuning based on performance metrics from the UI."""
    metrics = payload.get("metrics", payload)
    overrides = tune_system_parameters(metrics)
    await ui_hook_manager.trigger("system_parameters_tuned", overrides)
    return overrides


# Register with the central frontend router
register_route_once(
    "tune_parameters",
    tune_parameters_ui,
    "Tune system parameters",
    "optimization",
)
