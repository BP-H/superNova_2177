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


# Register network UI hooks
from network.ui_hook import trigger_coordination_analysis


async def _coordination_wrapper(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Adapter to run coordination analysis from a standard payload."""
    return await trigger_coordination_analysis(payload.get("validations", []))


register_route("coordination_analysis", _coordination_wrapper)
