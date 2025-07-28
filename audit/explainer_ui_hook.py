from __future__ import annotations

from typing import Any, Dict

from sqlalchemy.orm import Session

from audit_bridge import generate_commentary_from_trace
from frontend_bridge import register_route_once
from hook_manager import HookManager

# Exposed hook manager so external listeners can react to commentary events
ui_hook_manager = HookManager()


async def explain_audit_ui(payload: Dict[str, Any], db: Session) -> str:
    """Generate a human readable summary for an audit trace.

    Parameters
    ----------
    payload : dict
        Dictionary containing a ``"trace"`` key with the trace data.
    db : Session
        Unused database session placeholder for symmetry with other UI hooks.

    Returns
    -------
    str
        Commentary string describing the provided trace.
    """
    trace = payload.get("trace", {})
    summary = generate_commentary_from_trace(trace)
    await ui_hook_manager.trigger("audit_explained", summary)
    return summary


# Adapter for the frontend router which only supplies a payload argument
async def _explain_audit_route(payload: Dict[str, Any]) -> str:
    return await explain_audit_ui(payload, db=None)


# Register route with the central frontend bridge
register_route_once(
    "explain_audit",
    _explain_audit_route,
    "Explain an audit trace",
    "audit",
)
