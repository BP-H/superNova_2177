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
import logging


# background task support
class BackgroundTask:
    """Wrapper indicating a coroutine should run in the background."""

    def __init__(self, coro: Awaitable[Dict[str, Any]]) -> None:
        self.coro = coro
        self.long_running = True


def long_running(coro: Awaitable[Dict[str, Any]]) -> BackgroundTask:
    """Mark ``coro`` to be executed in the background."""
    return BackgroundTask(coro)


# routes from main branch (DO NOT delete)
from hypothesis.ui_hook import (
    detect_conflicting_hypotheses_ui,
    rank_hypotheses_by_confidence_ui,
    register_hypothesis_ui,
    update_hypothesis_score_ui,
)
import predictions.ui_hook  # noqa: F401 - route registration

Handler = Callable[..., Union[Dict[str, Any], Awaitable[Dict[str, Any]]]]

ROUTES: Dict[str, Handler] = {}
ROUTE_INFO: Dict[str, Dict[str, str]] = {}


def register_route(
    name: str,
    func: Handler,
    description: str | None = None,
    category: str = "general",
) -> None:
    """Register a handler for ``name`` events. Warn on duplicates."""
    existing = ROUTES.get(name)
    if existing and existing is not func:
        logging.warning(
            "Route '%s' already registered to %s; ignoring %s",
            name,
            getattr(existing, "__name__", existing),
            getattr(func, "__name__", func),
        )
        return
    ROUTES[name] = func
    doc = (getattr(func, "__doc__", "") or "").strip()
    if description is None:
        description = doc.split("\n", 1)[0] if doc else ""
    ROUTE_INFO[name] = {"description": description, "doc": doc, "category": category}


def register_route_once(
    name: str,
    func: Handler,
    description: str | None = None,
    category: str = "general",
) -> None:
    """Register ``func`` under ``name`` only if it isn't already set."""
    if name not in ROUTES:
        register_route(name, func, description=description, category=category)
    else:
        logging.debug(
            "Route '%s' already registered; keeping existing handler",
            name,
        )


from protocols.core.job_queue_agent import JobQueueAgent

queue_agent = JobQueueAgent()


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
    """Return structured route information grouped by category."""
    categories: Dict[str, list[Dict[str, str]]] = {}
    for name, info in ROUTE_INFO.items():
        category = info.get("category", "general")
        categories.setdefault(category, []).append(
            {
                "name": name,
                "description": info.get("description", ""),
                "doc": info.get("doc", ""),
            }
        )
    for routes in categories.values():
        routes.sort(key=lambda r: r["name"])
    return {"categories": categories}


register_route_once(
    "list_routes",
    _list_routes,
    "Return the names of all registered routes.",
    "system",
)
register_route_once(
    "job_status",
    _job_status,
    "Return the status of a background job.",
    "system",
)
register_route_once(
    "help",
    _help,
    "Display available routes grouped by category.",
    "system",
)

from consensus.ui_hook import forecast_consensus_ui

# Built-in hypothesis-related routes
from hypothesis.ui_hook import (
    detect_conflicting_hypotheses_ui,
    rank_hypotheses_by_confidence_ui,
    rank_hypotheses_ui,
    register_hypothesis_ui,
    synthesize_consensus_ui,
    update_hypothesis_score_ui,
)
import hypothesis_meta_evaluator_ui_hook  # noqa: F401 - route registration
import hypothesis_reasoner_ui_hook  # noqa: F401 - route registration
import validation_certifier_ui_hook  # noqa: F401 - route registration
import validator_reputation_tracker_ui_hook  # noqa: F401 - route registration
from system_state_utils.ui_hook import log_event_ui  # noqa: F401 - route registration


def describe_routes(_: Dict[str, Any]) -> Dict[str, Any]:
    """Return each route name mapped to the handler's docstring."""
    descriptions = {
        name: (getattr(func, "__doc__", "") or "").strip()
        for name, func in ROUTES.items()
    }
    return {"routes": descriptions}


# Hypothesis related routes
register_route_once(
    "rank_hypotheses_by_confidence",
    rank_hypotheses_by_confidence_ui,
    "Rank hypotheses using confidence",
    "hypothesis",
)
register_route_once(
    "detect_conflicting_hypotheses",
    detect_conflicting_hypotheses_ui,
    "Detect conflicting hypotheses",
    "hypothesis",
)
register_route_once(
    "register_hypothesis",
    register_hypothesis_ui,
    "Register a new hypothesis",
    "hypothesis",
)
register_route_once(
    "update_hypothesis_score",
    update_hypothesis_score_ui,
    "Update a hypothesis score",
    "hypothesis",
)
register_route_once(
    "forecast_consensus_agent",
    forecast_consensus_ui,
    "Forecast consensus via agent",
    "hypothesis",
)


# Prediction-related routes
import prediction.ui_hook  # noqa: F401 - route registration
import prediction_manager.ui_hook  # noqa: F401 - route registration
import vote_registry.ui_hook  # noqa: F401 - route registration
import optimization.ui_hook  # noqa: F401 - route registration
import causal_graph.ui_hook  # noqa: F401 - route registration
import predictions.ui_hook  # noqa: F401 - route registration
import social.ui_hook  # noqa: F401 - route registration
import quantum_sim.ui_hook  # noqa: F401 - route registration
import virtual_diary.ui_hook  # noqa: F401 - route registration


# Protocol agent management routes
from protocols.api_bridge import launch_agents_api, list_agents_api, step_agents_api

register_route_once(
    "list_agents",
    list_agents_api,
    "List available protocol agents",
    "protocols",
)
register_route_once(
    "launch_agents",
    launch_agents_api,
    "Launch protocol agents",
    "protocols",
)
register_route_once(
    "step_agents",
    step_agents_api,
    "Advance running protocol agents",
    "protocols",
)


# Advanced operations

# Import additional UI hooks for side effects (route registration)
import network.ui_hook  # noqa: F401,E402 - registers network analysis routes
import consensus.ui_hook  # noqa: F401,E402 - registers consensus forecast routes
import validators.ui_hook  # noqa: F401,E402 - registers validator reputation routes
import audit.ui_hook  # noqa: F401,E402 - exposes audit utilities
import audit.explainer_ui_hook  # noqa: F401,E402 - audit explanation utilities
import introspection.ui_hook  # noqa: F401,E402 - registers introspection routes
import protocols.ui_hook  # noqa: F401,E402 - registers cross-universe bridge routes
import temporal.ui_hook  # noqa: F401,E402 - temporal consistency routes
import protocols.agents.guardian_ui_hook  # noqa: F401,E402 - guardian agent routes
import protocols.agents.harmony_ui_hook  # noqa: F401,E402 - harmony synth route
