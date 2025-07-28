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
from hypothesis_meta_evaluator_ui_hook import trigger_meta_evaluation_ui
from hypothesis_reasoner_ui_hook import auto_flag_stale_ui
from validation_certifier_ui_hook import run_integrity_analysis_ui
from validator_reputation_tracker_ui_hook import update_reputations_ui
from consensus_forecaster_agent_ui_hook import forecast_consensus_ui

register_route("rank_hypotheses_by_confidence", rank_hypotheses_by_confidence_ui)
register_route("detect_conflicting_hypotheses", detect_conflicting_hypotheses_ui)
register_route("trigger_meta_evaluation", trigger_meta_evaluation_ui)
register_route("auto_flag_stale", auto_flag_stale_ui)
register_route("run_integrity_analysis", run_integrity_analysis_ui)
register_route("update_reputations", update_reputations_ui)
register_route("forecast_consensus_agent", forecast_consensus_ui)
