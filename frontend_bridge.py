"""Lightweight router for UI callbacks."""

from __future__ import annotations

from typing import Any, Awaitable, Callable, Dict, List, Tuple, Union

Handler = Callable[..., Union[Dict[str, Any], Awaitable[Dict[str, Any]]]]

# Flat lookup by route name
ROUTES: Dict[str, Handler] = {}
# Mapping of route name to docstring
ROUTE_DESCRIPTIONS: Dict[str, str] = {}
# Grouped mapping by category
ROUTES_BY_CATEGORY: Dict[str, List[Tuple[str, Handler]]] = {}


def register_route(name: str, func: Handler, category: str = "general") -> None:
    """Register a handler for ``name`` events."""

    ROUTES[name] = func
    ROUTE_DESCRIPTIONS[name] = (func.__doc__ or "").strip()
    ROUTES_BY_CATEGORY.setdefault(category, []).append((name, func))


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
    """Return registered routes grouped by category with descriptions."""

    grouped: Dict[str, List[Dict[str, str]]] = {}
    for category, entries in ROUTES_BY_CATEGORY.items():
        grouped[category] = [
            {
                "name": name,
                "description": ROUTE_DESCRIPTIONS.get(name, ""),
            }
            for name, _ in entries
        ]
    return {"routes": grouped}


register_route("list_routes", _list_routes, category="core")

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


register_route(
    "rank_hypotheses_by_confidence",
    rank_hypotheses_by_confidence_ui,
    category="hypothesis",
)
register_route(
    "detect_conflicting_hypotheses",
    detect_conflicting_hypotheses_ui,
    category="hypothesis",
)
register_route("register_hypothesis", register_hypothesis_ui, category="hypothesis")
register_route("update_hypothesis_score", update_hypothesis_score_ui, category="hypothesis")

# Prediction-related routes
from predictions.ui_hook import (
    store_prediction_ui,
    get_prediction_ui,
    update_prediction_status_ui,
)

from optimization.ui_hook import tune_parameters_ui

register_route("store_prediction", store_prediction_ui, category="prediction")
register_route("get_prediction", get_prediction_ui, category="prediction")
register_route("update_prediction_status", update_prediction_status_ui, category="prediction")

# Protocol agent management routes
from protocols.api_bridge import (
    list_agents_api,
    launch_agents_api,
    step_agents_api,
)

register_route("list_agents", list_agents_api, category="protocols")
register_route("launch_agents", launch_agents_api, category="protocols")
register_route("step_agents", step_agents_api, category="protocols")
# Temporal analysis route
from temporal.ui_hook import analyze_temporal_ui

register_route("temporal_consistency", analyze_temporal_ui, category="temporal")

# Optimization-related route
register_route("tune_parameters", tune_parameters_ui, category="optimization")
