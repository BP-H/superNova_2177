from __future__ import annotations

from typing import Any, Dict

from frontend_bridge import register_route_once
from hook_manager import HookManager
from hooks import events
from protocols.core import JobQueueAgent
from consensus_forecaster_agent import forecast_consensus_trend

# Exposed hook manager for observers
ui_hook_manager = HookManager()
queue_agent = JobQueueAgent()


async def forecast_consensus_ui(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Forecast consensus trend from a UI payload."""
    validations = payload.get("validations", [])
    network_analysis = payload.get("network_analysis")

    result = forecast_consensus_trend(validations, network_analysis)
    minimal = {
        "forecast_score": result.get("forecast_score", 0.0),
        "trend": result.get("trend", "stable"),
    }
    if "risk_modifier" in result:
        minimal["risk_modifier"] = result["risk_modifier"]
    if "flags" in result:
        minimal["flags"] = result["flags"]

    await ui_hook_manager.trigger(events.CONSENSUS_FORECAST_RUN, minimal)
    return minimal


async def queue_consensus_forecast_ui(payload: Dict[str, Any]) -> Dict[str, str]:
    """Queue consensus forecast calculation and return its job ID."""
    validations = payload.get("validations", [])
    network_analysis = payload.get("network_analysis")

    async def job() -> Dict[str, Any]:
        result = forecast_consensus_trend(validations, network_analysis)
        minimal = {
            "forecast_score": result.get("forecast_score", 0.0),
            "trend": result.get("trend", "stable"),
        }
        if "risk_modifier" in result:
            minimal["risk_modifier"] = result["risk_modifier"]
        if "flags" in result:
            minimal["flags"] = result["flags"]
        await ui_hook_manager.trigger("consensus_forecast_run", minimal)
        return minimal

    job_id = queue_agent.enqueue_job(job)
    return {"job_id": job_id}


async def poll_consensus_forecast_ui(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Return the status of a queued consensus forecast."""
    job_id = payload.get("job_id", "")
    return queue_agent.get_status(job_id)


# Register route with the frontend bridge
register_route_once(
    "forecast_consensus",
    forecast_consensus_ui,
    "Forecast consensus trend",
    "consensus",
)
register_route_once(
    "queue_consensus_forecast",
    queue_consensus_forecast_ui,
    "Queue consensus forecast job",
    "consensus",
)
register_route_once(
    "poll_consensus_forecast",
    poll_consensus_forecast_ui,
    "Poll status of a consensus forecast job",
    "consensus",
)
