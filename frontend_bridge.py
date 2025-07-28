"""Lightweight router for UI callbacks."""

from __future__ import annotations

from typing import Any, Awaitable, Callable, Dict, Union

Handler = Callable[..., Union[Dict[str, Any], Awaitable[Dict[str, Any]]]]

ROUTES: Dict[str, Handler] = {}


def register_route(name: str, func: Handler) -> None:
    """Register a handler for ``name`` events."""
    ROUTES[name] = func


def register_route_once(name: str, func: Handler) -> None:
    """Register ``func`` under ``name`` only if it isn't already set."""
    if name not in ROUTES:
        register_route(name, func)


async def dispatch_route(
    name: str, payload: Dict[str, Any], **kwargs: Any
) -> Dict[str, Any]:
    """Dispatch ``payload`` to the registered handler.

    Additional keyword arguments are forwarded to the handler. This allows
    callers to provide context objects like database sessions.
    """
    if name not in ROUTES:
        raise KeyError(name)
    handler = ROUTES[name]
    result = handler(payload, **kwargs)
    if isinstance(result, Awaitable):
        result = await result
    return result



def _list_routes(_: Dict[str, Any]) -> Dict[str, Any]:
    """Return the names of all registered routes."""
    return {"routes": sorted(ROUTES.keys())}


register_route("list_routes", _list_routes)

# Built-in hypothesis-related routes
from hypothesis.ui_hook import (
    rank_hypotheses_by_confidence_ui,
    detect_conflicting_hypotheses_ui,
    register_hypothesis_ui,
    update_hypothesis_score_ui,
    rank_hypotheses_ui,
    synthesize_consensus_ui,
)
from hypothesis_meta_evaluator_ui_hook import trigger_meta_evaluation_ui
from hypothesis_reasoner_ui_hook import auto_flag_stale_ui
from validation_certifier_ui_hook import run_integrity_analysis_ui
from validator_reputation_tracker_ui_hook import update_reputations_ui
from consensus_forecaster_agent_ui_hook import forecast_consensus_ui


register_route("rank_hypotheses_by_confidence", rank_hypotheses_by_confidence_ui)
register_route("detect_conflicting_hypotheses", detect_conflicting_hypotheses_ui)
register_route("register_hypothesis", register_hypothesis_ui)
register_route("update_hypothesis_score", update_hypothesis_score_ui)

# Prediction-related routes
from predictions.ui_hook import (
    store_prediction_ui,
    get_prediction_ui,
    update_prediction_status_ui,
)

from optimization.ui_hook import tune_parameters_ui
from quantum_sim.ui_hook import simulate_entanglement_ui

register_route_once("store_prediction", store_prediction_ui)
register_route_once("get_prediction", get_prediction_ui)
register_route_once("update_prediction_status", update_prediction_status_ui)

# Protocol agent management routes
from protocols.api_bridge import (
    list_agents_api,
    launch_agents_api,
    step_agents_api,
)

register_route("list_agents", list_agents_api)
register_route("launch_agents", launch_agents_api)
register_route("step_agents", step_agents_api)
# Temporal analysis route
from temporal.ui_hook import analyze_temporal_ui

register_route_once("temporal_consistency", analyze_temporal_ui)

# Optimization-related route
register_route("tune_parameters", tune_parameters_ui)
register_route("simulate_entanglement", simulate_entanglement_ui)

# Universe UI routes
from ui_hooks.universe_ui import (
    get_universe_overview,
    list_available_proposals,
    submit_universe_proposal,
)

register_route("get_universe_overview", get_universe_overview)
register_route("list_available_proposals", list_available_proposals)
register_route("submit_universe_proposal", submit_universe_proposal)
