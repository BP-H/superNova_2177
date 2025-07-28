"""Lightweight router for UI callbacks."""

from __future__ import annotations

from typing import Any, Awaitable, Callable, Dict, Union

Handler = Callable[[Dict[str, Any]], Union[Dict[str, Any], Awaitable[Dict[str, Any]]]]

ROUTES: Dict[str, Handler] = {}


def register_route(name: str, func: Handler) -> None:
    """Register a handler for ``name`` events."""
    ROUTES[name] = func


async def dispatch_route(name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Dispatch ``payload`` to the registered handler."""
    if name not in ROUTES:
        raise KeyError(name)
    handler = ROUTES[name]
    result = handler(payload)
    if isinstance(result, Awaitable):
        result = await result
    return result

# Built-in hypothesis-related routes
from hypothesis.ui_hook import (
    rank_hypotheses_by_confidence_ui,
    detect_conflicting_hypotheses_ui,
)

register_route("rank_hypotheses_by_confidence", rank_hypotheses_by_confidence_ui)
register_route("detect_conflicting_hypotheses", detect_conflicting_hypotheses_ui)

# Prediction-related routes
from predictions.ui_hook import (
    store_prediction_ui,
    get_prediction_ui,
    update_prediction_status_ui,
)

register_route("store_prediction", store_prediction_ui)
register_route("get_prediction", get_prediction_ui)
register_route("update_prediction_status", update_prediction_status_ui)

# Protocol agent management routes
from protocols.api_bridge import (
    list_agents_api,
    launch_agents_api,
    step_agents_api,
)

register_route("list_agents", list_agents_api)
register_route("launch_agents", launch_agents_api)
register_route("step_agents", step_agents_api)
