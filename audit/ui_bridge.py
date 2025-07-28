from __future__ import annotations

"""Bridge audit UI callbacks to the central frontend router."""

from typing import Any, Dict

from db_models import SessionLocal
from frontend_bridge import register_route

from .ui_hook import attach_trace_ui, log_hypothesis_ui


async def log_hypothesis_route(payload: Dict[str, Any]) -> str:
    """Route wrapper for :func:`log_hypothesis_ui` using a new DB session."""
    db = SessionLocal()
    try:
        return await log_hypothesis_ui(payload, db)
    finally:
        db.close()


async def attach_trace_route(payload: Dict[str, Any]) -> None:
    """Route wrapper for :func:`attach_trace_ui` using a new DB session."""
    db = SessionLocal()
    try:
        await attach_trace_ui(payload, db)
    finally:
        db.close()


# Register routes with the central dispatcher on import
register_route("log_hypothesis", log_hypothesis_route)
register_route("attach_trace", attach_trace_route)
