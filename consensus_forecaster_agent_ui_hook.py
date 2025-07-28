from __future__ import annotations

from typing import Any, Dict

from frontend_bridge import register_route
from hook_manager import HookManager
from consensus_forecaster_agent import forecast_consensus_trend

ui_hook_manager = HookManager()


async def forecast_consensus_ui(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Forecast consensus trend from a payload."""
    validations = payload.get("validations", [])
    network_analysis = payload.get("network_analysis")
    result = forecast_consensus_trend(validations, network_analysis)
    minimal = {
        "forecast_score": result.get("forecast_score", 0.0),
        "trend": result.get("trend", "stable"),
    }
    await ui_hook_manager.trigger("consensus_forecast_run", minimal)
    return minimal


