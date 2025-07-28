"""Lightweight router for UI callbacks.

This module exposes a simple registry mapping route names to callables.
Handlers register themselves with :func:`register_route` and can be
executed using :func:`dispatch_route`. The built-in handlers cover
hypothesis management, prediction storage and protocol operations.

The :data:`ROUTES` dictionary holds the active mapping. Debug helpers
``list_routes`` and ``describe_routes`` reveal the currently registered
names and their docstrings. See ``docs/routes.md`` for a reference table
of default routes.
"""

from __future__ import annotations

from typing import Any, Awaitable, Callable, Dict, Union, Optional


# background task support
class BackgroundTask:
    """Wrapper indicating a coroutine should run in the background."""
    def __init__(self, coro: Awaitable[Dict[str, Any]]) -> None:
        self.coro = coro
        self.long_running = True

def long_running(coro: Awaitable[Dict[str, Any]]) -> BackgroundTask:
    """Mark ``coro`` to be executed in the background."""
    return BackgroundTask(coro)

from protocols.core.job_queue_agent import JobQueueAgent
queue_agent = JobQueueAgent()

# routes from main branch (DO NOT delete)
from hypothesis.ui_hook import (
    detect_conflicting_hypotheses_ui,
    rank_hypotheses_by_confidence_ui,
    register_hypothesis_ui,
    update_hypothesis_score_ui,
)
from optimization.ui_hook import tune_parameters_ui
from predictions.ui_hook import (
    get_prediction_ui,
    store_prediction_ui,
    update_prediction_status_ui,
)
from protocols.api_bridge import (
    launch_agents_api,
    list_agents_api,
    step_agents_api,
)
from temporal.ui_hook import analyze_temporal_ui

Handler = Callable[..., Union[Dict[str, Any], Awaitable[Dict[str, Any]]]]

ROUTES: Dict[str, Handler] = {}
# metadata for descriptions and categories
ROUTE_INFO: Dict[str, Dict[str, str]] = {}

def _extract_summary(func: Handler) -> str:
    doc = getattr(func, "__doc__", "") or ""
    if doc:
        return doc.strip().splitlines()[0]
    return ""

def register_route(
    name: str,
    func: Handler,
    description: Optional[str] = None,
    category: str = "general",
) -> None:
    """Register a handler for ``name`` events."""
    ROUTES[name] = func
    if description is None:
        description = _extract_summary(func)
    ROUTE_INFO[name] = {"description": description, "category": category}

def register_route_once(
    name: str,
    func: Handler,
    description: Optional[str] = None,
    category: str = "general",
) -> None:
    """Register ``func`` under ``name`` only if it isn't already set."""
    if name not in ROUTES:
        register_route(name, func, description=description, category=category)


async def dispatch_route(
    name: str, payload: Dict[str, Any], **kwargs: Any
) -> Dict[str, Any]:
    """Dispatch ``payload`` to the registered handler."""
    if name not in ROUTES:
        raise KeyError(name)
    handler = ROUTES[name]
    result = handler(payload, **kwargs)
    if isinstance(result, BackgroundTask):
        async def job() -> Dict[str, Any]:
            return await result.coro
        job_id = queue_agent.enqueue_job(job)
        return {"job_id": job_id}
    if isinstance(result, Awaitable):
        result = await result
    return result

def _list_routes(_: Dict[str, Any]) -> Dict[str, Any]:
    """Return the names of all registered routes."""
    return {"routes": sorted(ROUTES.keys())}


def _job_status(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Return the status of a background job."""
    job_id = payload.get("job_id", "")
    return queue_agent.get_status(job_id)


register_route("list_routes", _list_routes, "List registered route names", "meta")
register_route("job_status", _job_status, "Background job status", "meta")
register_route("help", _help_routes, "Describe routes grouped by category", "meta")

from consensus_forecaster_agent_ui_hook import forecast_consensus_ui

# Built-in hypothesis-related routes
from hypothesis.ui_hook import (
    detect_conflicting_hypotheses_ui,
    rank_hypotheses_by_confidence_ui,
    rank_hypotheses_ui,
    register_hypothesis_ui,
    synthesize_consensus_ui,
    update_hypothesis_score_ui,
)
from hypothesis_meta_evaluator_ui_hook import trigger_meta_evaluation_ui
from hypothesis_reasoner_ui_hook import auto_flag_stale_ui
from validation_certifier_ui_hook import run_integrity_analysis_ui
from validator_reputation_tracker_ui_hook import update_reputations_ui

def describe_routes(_: Dict[str, Any]) -> Dict[str, Any]:
    """Return each route name mapped to the handler's docstring."""
    descriptions = {
        name: (getattr(func, "__doc__", "") or "").strip()
        for name, func in ROUTES.items()
    }
    return {"routes": descriptions}


def _help_routes(_: Dict[str, Any]) -> Dict[str, Any]:
    """Return route metadata grouped by category."""
    grouped: Dict[str, list] = {}
    for name, info in ROUTE_INFO.items():
        cat = info.get("category", "general")
        grouped.setdefault(cat, []).append({
            "name": name,
            "description": info.get("description", ""),
        })
    for routes in grouped.values():
        routes.sort(key=lambda r: r["name"])
    return {"routes": grouped}

# Hypothesis related routes
register_route(
    "rank_hypotheses_by_confidence",
    rank_hypotheses_by_confidence_ui,
    "Rank hypotheses using reasoning layer",
    "hypothesis",
)
register_route(
    "detect_conflicting_hypotheses",
    detect_conflicting_hypotheses_ui,
    "Detect contradictions between hypotheses",
    "hypothesis",
)
register_route(
    "register_hypothesis",
    register_hypothesis_ui,
    "Register a new hypothesis",
    "hypothesis",
)
register_route(
    "update_hypothesis_score",
    update_hypothesis_score_ui,
    "Update a hypothesis score",
    "hypothesis",
)

from optimization.ui_hook import tune_parameters_ui

# Prediction-related routes
from prediction.ui_hook import (
    get_prediction_ui,
    schedule_audit_proposal_ui,
    store_prediction_ui,
)
from vote_registry.ui_hook import record_vote_ui, load_votes_ui
from optimization.ui_hook import tune_parameters_ui
from predictions.ui_hook import update_prediction_status_ui


register_route(
    "store_prediction",
    store_prediction_ui,
    "Persist prediction information",
    "prediction",
)
register_route(
    "get_prediction",
    get_prediction_ui,
    "Retrieve a stored prediction",
    "prediction",
)
register_route(
    "schedule_audit_proposal",
    schedule_audit_proposal_ui,
    "Schedule annual audit proposal",
    "prediction",
)
register_route(
    "update_prediction_status",
    update_prediction_status_ui,
    "Modify prediction status and outcome",
    "prediction",
)
register_route("record_vote", record_vote_ui, "Record a validator vote", "prediction")
register_route("load_votes", load_votes_ui, "Load votes from storage", "prediction")

# Additional routes
from virtual_diary.ui_hook import fetch_entries_ui, add_entry_ui
from quantum_sim.ui_hook import simulate_entanglement_ui

# Protocol agent management routes
from protocols.api_bridge import launch_agents_api, list_agents_api, step_agents_api

register_route("list_agents", list_agents_api, "List protocol agent instances", "protocol")
register_route("launch_agents", launch_agents_api, "Instantiate protocol agents", "protocol")
register_route("step_agents", step_agents_api, "Run a single tick on agents", "protocol")


register_route_once(
    "temporal_consistency",
    analyze_temporal_ui,
    "Analyze temporal consistency",
    "analysis",
)

# Optimization route
register_route(
    "tune_parameters",
    tune_parameters_ui,
    "Tune system parameters from metrics",
    "optimization",
)

# Optimization-related route
register_route(
    "tune_parameters",
    tune_parameters_ui,
    "Tune system parameters from metrics",
    "optimization",
)

# Social simulation route
from social.ui_hook import simulate_entanglement_ui
register_route(
    "simulate_entanglement",
    simulate_entanglement_ui,
    "Run social entanglement simulation",
    "social",
)

# Import additional UI hooks for side effects (route registration)
import network.ui_hook  # noqa: F401,E402 - registers network analysis routes
import consensus.ui_hook  # noqa: F401,E402 - registers consensus forecast routes
import validators.ui_hook  # noqa: F401,E402 - registers validator reputation routes
import audit.ui_hook  # noqa: F401,E402 - exposes audit utilities
import introspection.ui_hook  # noqa: F401,E402 - registers introspection routes
import protocols.ui_hook  # noqa: F401,E402 - registers cross-universe bridge routes
import protocols.agents.guardian_ui_hook  # noqa: F401,E402 - guardian agent routes
import protocols.agents.harmony_ui_hook  # noqa: F401,E402 - harmony synth route

