"""Lightweight router for UI callbacks."""

from __future__ import annotations

from typing import Any, Awaitable, Callable, Dict, Union

Handler = Callable[..., Union[Dict[str, Any], Awaitable[Dict[str, Any]]]]

ROUTES: Dict[str, Handler] = {}
# Optional metadata mapping route name to a high level category
_ROUTE_CATEGORY_HINTS: Dict[str, str] = {
    "rank_hypotheses_by_confidence": "Hypothesis",
    "detect_conflicting_hypotheses": "Hypothesis",
    "register_hypothesis": "Hypothesis",
    "update_hypothesis_score": "Hypothesis",
    "store_prediction": "Prediction",
    "get_prediction": "Prediction",
    "update_prediction_status": "Prediction",
    "list_agents": "Protocol",
    "launch_agents": "Protocol",
    "step_agents": "Protocol",
    "temporal_consistency": "Temporal",
    "tune_parameters": "Optimization",
}


def register_route(name: str, func: Handler) -> None:
    """Register a handler for ``name`` events."""
    ROUTES[name] = func


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
    """Return structured metadata about all registered routes."""
    info = []
    for name, handler in ROUTES.items():
        doc = (handler.__doc__ or "").strip()
        info.append(
            {
                "category": _ROUTE_CATEGORY_HINTS.get(name, "General"),
                "name": name,
                "doc": doc,
            }
        )
    info.sort(key=lambda r: r["name"])
    return {"routes": info}


register_route("list_routes", _list_routes)

# Built-in hypothesis-related routes
from hypothesis.ui_hook import (
    detect_conflicting_hypotheses_ui,
    rank_hypotheses_by_confidence_ui,
    rank_hypotheses_ui,
    register_hypothesis_ui,
    synthesize_consensus_ui,
    update_hypothesis_score_ui,
)

register_route("rank_hypotheses_by_confidence", rank_hypotheses_by_confidence_ui)
register_route("detect_conflicting_hypotheses", detect_conflicting_hypotheses_ui)
register_route("register_hypothesis", register_hypothesis_ui)
register_route("update_hypothesis_score", update_hypothesis_score_ui)

from optimization.ui_hook import tune_parameters_ui

# Prediction-related routes
from predictions.ui_hook import (
    get_prediction_ui,
    store_prediction_ui,
    update_prediction_status_ui,
)

register_route("store_prediction", store_prediction_ui)
register_route("get_prediction", get_prediction_ui)
register_route("update_prediction_status", update_prediction_status_ui)

# Protocol agent management routes
from protocols.api_bridge import launch_agents_api, list_agents_api, step_agents_api

register_route("list_agents", list_agents_api)
register_route("launch_agents", launch_agents_api)
register_route("step_agents", step_agents_api)
# Temporal analysis route
from temporal.ui_hook import analyze_temporal_ui

register_route("temporal_consistency", analyze_temporal_ui)

# Optimization-related route
register_route("tune_parameters", tune_parameters_ui)
