from __future__ import annotations

from typing import Any, Dict

from frontend_bridge import register_route
from hook_manager import HookManager
from optimization_engine import tune_system_parameters

# Exposed hook manager for observers
ui_hook_manager = HookManager()


async def tune_parameters_ui(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Tune system parameters from UI-provided metrics.

    Parameters
    ----------
    payload : dict
        Dictionary containing ``"performance_metrics"``.

    Returns
    -------
    dict
        Suggested parameter overrides from :func:`tune_system_parameters`.
    """
    metrics = payload["performance_metrics"]
    overrides = tune_system_parameters(metrics)
    await ui_hook_manager.trigger("system_parameters_tuned", overrides)
    return overrides


# Register route with the frontend bridge
register_route("tune_parameters", tune_parameters_ui)
