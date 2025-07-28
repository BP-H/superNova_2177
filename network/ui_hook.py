from __future__ import annotations

import logging
from typing import Any, Dict

from frontend_bridge import register_route_once
from hook_manager import HookManager
from hooks import events
from protocols.core import JobQueueAgent

from .network_coordination_detector import analyze_coordination_patterns

# Exposed hook manager for external subscribers
ui_hook_manager = HookManager()

queue_agent = JobQueueAgent()

# Hook manager used for run_coordination_analysis
hook_manager = HookManager()


async def trigger_coordination_analysis_ui(
    payload: Dict[str, Any], **_: Any
) -> Dict[str, Any]:
    """Run coordination analysis from UI payload.

    Parameters
    ----------
    payload : dict
        JSON payload containing ``"validations"`` list.

    Returns
    -------
    dict
        Minimal result with ``overall_risk_score`` and ``graph``.
    """
    validations = payload.get("validations", [])
    result = analyze_coordination_patterns(validations)
    minimal = {
        "overall_risk_score": result.get("overall_risk_score", 0.0),
        "graph": result.get("graph", {}),
    }
    # Emit event for observers
    await ui_hook_manager.trigger(events.COORDINATION_ANALYSIS_RUN, minimal)
    return minimal


async def queue_coordination_analysis_ui(payload: Dict[str, Any]) -> Dict[str, str]:
    """Queue coordination analysis and return its job ID."""
    validations = payload.get("validations", [])

    async def job() -> Dict[str, Any]:
        result = analyze_coordination_patterns(validations)
        minimal = {
            "overall_risk_score": result.get("overall_risk_score", 0.0),
            "graph": result.get("graph", {}),
        }
        await ui_hook_manager.trigger("coordination_analysis_run", minimal)
        return minimal

    job_id = queue_agent.enqueue_job(job)
    return {"job_id": job_id}


async def poll_coordination_analysis_ui(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Return the status of a queued coordination analysis."""
    job_id = payload.get("job_id", "")
    return queue_agent.get_status(job_id)


# Register with the central frontend router
register_route_once(
    "coordination_analysis",
    trigger_coordination_analysis_ui,
    "Run network coordination analysis",
    "network",
)
register_route_once(
    "queue_coordination_analysis",
    queue_coordination_analysis_ui,
    "Queue coordination analysis job",
    "network",
)
register_route_once(
    "poll_coordination_analysis",
    poll_coordination_analysis_ui,
    "Poll status of a coordination job",
    "network",
)


async def run_coordination_analysis(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Run coordination analysis and emit a network_analysis hook."""
    if not isinstance(payload, dict):
        raise ValueError("payload must be a dict")

    validations = payload.get("validations")
    if not isinstance(validations, list):
        raise ValueError("payload['validations'] must be a list")

    result = analyze_coordination_patterns(validations)

    minimal = {
        "overall_risk_score": result.get("overall_risk_score", 0.0),
        "flags": result.get("flags", []),
        "clusters": result.get("coordination_clusters", []),
    }

    try:
        hook_manager.fire_hooks(events.NETWORK_ANALYSIS, minimal)
    except Exception:  # pragma: no cover - logging only
        logging.exception("Failed to fire network_analysis hook")

    return minimal
