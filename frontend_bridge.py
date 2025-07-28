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

from typing import Any, Awaitable, Callable, Dict, Union


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

Handler = Callable[..., Union[Dict[str, Any], Awaitable[Dict[str, Any]]]]

ROUTES: Dict[str, Handler] = {}
# Additional metadata for each registered route
ROUTE_DESCRIPTIONS: Dict[str, str] = {}
ROUTE_CATEGORIES: Dict[str, str] = {}

def register_route(
    name: str,
    func: Handler,
    description: str | None = None,
    category: str | None = None,
) -> None:
    """Register a handler for ``name`` events."""
    ROUTES[name] = func
    if description is None:
        description = (getattr(func, "__doc__", "") or "").strip().split("\n")[0]
    ROUTE_DESCRIPTIONS[name] = description or ""
    ROUTE_CATEGORIES[name] = category or "general"

def register_route_once(
    name: str,
    func: Handler,
    description: str | None = None,
    category: str | None = None,
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


def _help(_: Dict[str, Any]) -> Dict[str, Any]:
    """Return registered routes grouped by category with descriptions."""
    grouped: Dict[str, list[Dict[str, str]]] = {}
    for name in sorted(ROUTES.keys()):
        cat = ROUTE_CATEGORIES.get(name, "general")
        desc = ROUTE_DESCRIPTIONS.get(name, "")
        grouped.setdefault(cat, []).append({"name": name, "description": desc})
    for routes in grouped.values():
        routes.sort(key=lambda r: r["name"])
    return {"routes": grouped}


register_route("list_routes", _list_routes, "Return the names of all registered routes", "utility")
register_route("job_status", _job_status, "Check the status of a background job", "utility")
register_route("help", _help, "List routes grouped by category", "utility")

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
from system_state_utils.ui_hook import log_event_ui  # noqa: F401 - route registration


def describe_routes(_: Dict[str, Any]) -> Dict[str, Any]:
    """Return each route name mapped to the handler's docstring."""
    descriptions = {
        name: (getattr(func, "__doc__", "") or "").strip()
        for name, func in ROUTES.items()
    }
    return {"routes": descriptions}

# Hypothesis related routes
register_route(
    "rank_hypotheses_by_confidence",
    rank_hypotheses_by_confidence_ui,
    "Rank hypotheses using the reasoning layer",
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
register_route(
    "trigger_meta_evaluation",
    trigger_meta_evaluation_ui,
    "Run meta evaluation on hypotheses",
    "hypothesis",
)
register_route(
    "auto_flag_stale",
    auto_flag_stale_ui,
    "Automatically flag stale hypotheses",
    "hypothesis",
)
register_route(
    "run_integrity_analysis",
    run_integrity_analysis_ui,
    "Run validation integrity analysis",
    "hypothesis",
)
register_route(
    "update_reputations",
    update_reputations_ui,
    "Update validator reputations",
    "validators",
)
register_route(
    "forecast_consensus_agent",
    forecast_consensus_ui,
    "Forecast consensus trend",
    "consensus",
)

from optimization.ui_hook import tune_parameters_ui

# Prediction-related routes
from prediction.ui_hook import (
    get_prediction_ui,
    schedule_audit_proposal_ui,
    store_prediction_ui,
)
from vote_registry.ui_hook import record_vote_ui, load_votes_ui
from causal_graph.ui_hook import build_graph_ui, simulate_entanglement_ui as simulate_entanglement_causal_ui
from predictions.ui_hook import update_prediction_status_ui
from social.ui_hook import simulate_entanglement_ui as simulate_entanglement_social_ui
from quantum_sim.ui_hook import simulate_entanglement_ui as simulate_entanglement_quantum_ui, quantum_prediction_ui
from virtual_diary.ui_hook import fetch_entries_ui, add_entry_ui

register_route(
    "store_prediction",
    store_prediction_ui,
    "Persist prediction data",
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
    "Schedule an audit proposal",
    "prediction",
)
register_route(
    "update_prediction_status",
    update_prediction_status_ui,
    "Modify prediction status and outcome",
    "prediction",
)
register_route(
    "quantum_prediction",
    quantum_prediction_ui,
    "Generate quantum-based prediction",
    "quantum",
)
register_route(
    "record_vote",
    record_vote_ui,
    "Record a vote",
    "votes",
)
register_route(
    "load_votes",
    load_votes_ui,
    "Load recorded votes",
    "votes",
)
register_route(
    "fetch_diary_entries",
    fetch_entries_ui,
    "Fetch diary entries",
    "diary",
)
register_route(
    "add_diary_entry",
    add_entry_ui,
    "Add a diary entry",
    "diary",
)
register_route(
    "simulate_entanglement_causal",
    simulate_entanglement_causal_ui,
    "Simulate entanglement in causal graph",
    "causal_graph",
)
register_route(
    "simulate_entanglement_social",
    simulate_entanglement_social_ui,
    "Simulate social entanglement",
    "social",
)
register_route(
    "simulate_entanglement_quantum",
    simulate_entanglement_quantum_ui,
    "Simulate quantum entanglement",
    "quantum",
)


# Protocol agent management routes
from protocols.api_bridge import launch_agents_api, list_agents_api, step_agents_api

register_route(
    "list_agents",
    list_agents_api,
    "List available protocol agents",
    "protocols",
)
register_route(
    "launch_agents",
    launch_agents_api,
    "Launch selected protocol agents",
    "protocols",
)
register_route(
    "step_agents",
    step_agents_api,
    "Run one step on active agents",
    "protocols",
)

register_route_once(
    "temporal_consistency",
    analyze_temporal_ui,
    "Analyze temporal consistency",
    "temporal",
)

# Optimization route
register_route(
    "tune_parameters",
    tune_parameters_ui,
    "Tune system parameters",
    "optimization",
)

# Advanced operations
register_route(
    "trigger_meta_evaluation",
    trigger_meta_evaluation_ui,
    "Run meta evaluation on hypotheses",
    "advanced",
)
register_route(
    "auto_flag_stale",
    auto_flag_stale_ui,
    "Automatically flag stale hypotheses",
    "advanced",
)
register_route(
    "run_integrity_analysis",
    run_integrity_analysis_ui,
    "Run validation integrity analysis",
    "advanced",
)
register_route(
    "update_reputations",
    update_reputations_ui,
    "Update validator reputations",
    "advanced",
)
register_route(
    "forecast_consensus_agent",
    forecast_consensus_ui,
    "Forecast consensus trend",
    "advanced",
)

# Causal graph routes
register_route(
    "build_causal_graph",
    build_graph_ui,
    "Build a causal influence graph",
    "causal_graph",
)
register_route(
    "simulate_entanglement_causal",
    simulate_entanglement_causal_ui,
    "Simulate entanglement in causal graph",
    "causal_graph",
)

# Social simulation route
register_route(
    "simulate_entanglement_social",
    simulate_entanglement_social_ui,
    "Simulate social entanglement",
    "social",
)

# Quantum simulation route
register_route(
    "simulate_entanglement_quantum",
    simulate_entanglement_quantum_ui,
    "Simulate quantum entanglement",
    "quantum",
)

# Import additional UI hooks for side effects (route registration)
import network.ui_hook  # noqa: F401,E402 - registers network analysis routes
import consensus.ui_hook  # noqa: F401,E402 - registers consensus forecast routes
import validators.ui_hook  # noqa: F401,E402 - registers validator reputation routes
import audit.ui_hook  # noqa: F401,E402 - exposes audit utilities
import audit.explainer_ui_hook  # noqa: F401,E402 - audit explanation utilities
import introspection.ui_hook  # noqa: F401,E402 - registers introspection routes
import protocols.ui_hook  # noqa: F401,E402 - registers cross-universe bridge routes
import protocols.agents.guardian_ui_hook  # noqa: F401,E402 - guardian agent routes
import protocols.agents.harmony_ui_hook  # noqa: F401,E402 - harmony synth route

