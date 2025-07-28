"""Lightweight router for UI callbacks."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Dict, List, Union

Handler = Callable[..., Union[Dict[str, Any], Awaitable[Dict[str, Any]]]]


@dataclass
class RouteInfo:
    handler: Handler
    description: str = ""
    category: str = "general"


ROUTES: Dict[str, RouteInfo] = {}


def register_route(
    name: str,
    func: Handler,
    description: str | None = None,
    category: str = "general",
) -> None:
    """Register a handler for ``name`` events."""
    ROUTES[name] = RouteInfo(func, description or "", category)


async def dispatch_route(
    name: str, payload: Dict[str, Any], **kwargs: Any
) -> Dict[str, Any]:
    """Dispatch ``payload`` to the registered handler.

    Additional keyword arguments are forwarded to the handler. This allows
    callers to provide context objects like database sessions.
    """
    if name not in ROUTES:
        raise KeyError(name)
    handler = ROUTES[name].handler
    result = handler(payload, **kwargs)
    if isinstance(result, Awaitable):
        result = await result
    return result


def _list_routes(_: Dict[str, Any]) -> Dict[str, Any]:
    """Return registered routes grouped by category."""
    grouped: Dict[str, List[Dict[str, str]]] = {}
    for name, info in ROUTES.items():
        entry = {
            "name": name,
            "description": info.description or (info.handler.__doc__ or ""),
        }
        grouped.setdefault(info.category, []).append(entry)

    for routes in grouped.values():
        routes.sort(key=lambda r: r["name"])

    return {"routes": grouped}


register_route(
    "list_routes",
    _list_routes,
    description="List available routes",
    category="meta",
)
register_route(
    "help",
    _list_routes,
    description="List available routes",
    category="meta",
)

from consensus_forecaster_agent_ui_hook import forecast_consensus_ui
# Built-in hypothesis-related routes
from hypothesis.ui_hook import (detect_conflicting_hypotheses_ui,
                                rank_hypotheses_by_confidence_ui,
                                rank_hypotheses_ui, register_hypothesis_ui,
                                synthesize_consensus_ui,
                                update_hypothesis_score_ui)
from hypothesis_meta_evaluator_ui_hook import trigger_meta_evaluation_ui
from hypothesis_reasoner_ui_hook import auto_flag_stale_ui
from validation_certifier_ui_hook import run_integrity_analysis_ui
from validator_reputation_tracker_ui_hook import update_reputations_ui

register_route(
    "rank_hypotheses_by_confidence",
    rank_hypotheses_by_confidence_ui,
    description="Rank hypotheses by confidence",
    category="hypothesis",
)
register_route(
    "detect_conflicting_hypotheses",
    detect_conflicting_hypotheses_ui,
    description="Find conflicting hypotheses",
    category="hypothesis",
)
register_route(
    "register_hypothesis",
    register_hypothesis_ui,
    description="Register a new hypothesis",
    category="hypothesis",
)
register_route(
    "update_hypothesis_score",
    update_hypothesis_score_ui,
    description="Update hypothesis score",
    category="hypothesis",
)

from optimization.ui_hook import tune_parameters_ui
# Prediction-related routes
from predictions.ui_hook import (get_prediction_ui, store_prediction_ui,
                                 update_prediction_status_ui)

register_route(
    "store_prediction",
    store_prediction_ui,
    description="Persist prediction data",
    category="prediction",
)
register_route(
    "get_prediction",
    get_prediction_ui,
    description="Fetch a prediction record",
    category="prediction",
)
register_route(
    "update_prediction_status",
    update_prediction_status_ui,
    description="Update prediction status",
    category="prediction",
)

# Protocol agent management routes
from protocols.api_bridge import (launch_agents_api, list_agents_api,
                                  step_agents_api)

register_route(
    "list_agents",
    list_agents_api,
    description="Return available agent classes",
    category="agents",
)
register_route(
    "launch_agents",
    launch_agents_api,
    description="Instantiate and start agents",
    category="agents",
)
register_route(
    "step_agents",
    step_agents_api,
    description="Trigger one tick on active agents",
    category="agents",
)
# Temporal analysis route
from temporal.ui_hook import analyze_temporal_ui

register_route(
    "temporal_consistency",
    analyze_temporal_ui,
    description="Analyze temporal consistency",
    category="temporal",
)

# Optimization-related route
register_route(
    "tune_parameters",
    tune_parameters_ui,
    description="Tune system parameters",
    category="optimization",
)
