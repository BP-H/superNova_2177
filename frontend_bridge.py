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
from db_models import SessionLocal
from hypothesis.ui_hook import (
    rank_hypotheses_by_confidence_ui,
    detect_conflicting_hypotheses_ui,
    rank_hypotheses_ui,
    synthesize_consensus_ui,
)

register_route("rank_hypotheses_by_confidence", rank_hypotheses_by_confidence_ui)
register_route("detect_conflicting_hypotheses", detect_conflicting_hypotheses_ui)


async def _rank_hypotheses_route(payload: Dict[str, Any]) -> Dict[str, Any]:
    db = SessionLocal()
    try:
        return await rank_hypotheses_ui(payload, db)
    finally:
        db.close()


async def _synthesize_consensus_route(payload: Dict[str, Any]) -> Dict[str, Any]:
    db = SessionLocal()
    try:
        return await synthesize_consensus_ui(payload, db)
    finally:
        db.close()


register_route("rank_hypotheses", _rank_hypotheses_route)
register_route("synthesize_consensus", _synthesize_consensus_route)
