import logging
from typing import Any, Dict

from sqlalchemy.orm import Session

from audit_bridge import log_hypothesis_with_trace, attach_trace_to_logentry
from hook_manager import HookManager


logger = logging.getLogger(__name__)
logger.propagate = False

# Dedicated hook manager for emitting audit events
hook_manager = HookManager()


async def log_hypothesis_ui(payload: Dict[str, Any], db: Session) -> str:
    """Asynchronously log a hypothesis from the UI.

    Parameters
    ----------
    payload:
        Dictionary containing ``hypothesis_text`` and optional
        ``causal_node_ids`` and ``metadata``.
    db:
        Database session used to persist the log.

    Returns
    -------
    str
        Key under which the hypothesis was stored.
    """
    key = log_hypothesis_with_trace(
        payload.get("hypothesis_text", ""),
        payload.get("causal_node_ids", []),
        db,
        metadata=payload.get("metadata"),
    )
    await hook_manager.trigger(
        "audit_log",
        {"action": "log_hypothesis", "key": key},
    )
    return key


async def attach_trace_ui(payload: Dict[str, Any], db: Session) -> None:
    """Attach trace metadata to an existing log entry via the UI."""
    attach_trace_to_logentry(
        int(payload["log_id"]),
        payload.get("causal_node_ids", []),
        db,
        summary=payload.get("summary"),
    )
    await hook_manager.trigger(
        "audit_log",
        {"action": "attach_trace", "log_id": int(payload["log_id"])},
    )

