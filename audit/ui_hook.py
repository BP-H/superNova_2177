import logging
from typing import Any, Dict

from sqlalchemy.orm import Session
from frontend_bridge import register_route_once

# isort: off
from audit_bridge import (
    attach_trace_to_logentry,
    export_causal_path,
    log_hypothesis_with_trace,
)

# isort: on
from causal_graph import InfluenceGraph
from causal_trigger import trigger_causal_audit
from hook_manager import HookManager
from hooks import events
from protocols.utils.messaging import MessageHub

logger = logging.getLogger(__name__)
logger.propagate = False

# Dedicated hook manager for emitting audit events
hook_manager = HookManager()
# Public message hub for audit-related events
message_hub = MessageHub()


async def log_hypothesis_ui(payload: Dict[str, Any], db: Session, **_: Any) -> str:
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
        events.AUDIT_LOG,
        {"action": "log_hypothesis", "key": key},
    )
    message_hub.publish("audit_log", {"action": "log_hypothesis", "key": key})
    return key


async def attach_trace_ui(payload: Dict[str, Any], db: Session, **_: Any) -> None:
    """Attach trace metadata to an existing log entry via the UI."""
    attach_trace_to_logentry(
        int(payload["log_id"]),
        payload.get("causal_node_ids", []),
        db,
        summary=payload.get("summary"),
    )
    await hook_manager.trigger(
        events.AUDIT_LOG,
        {"action": "attach_trace", "log_id": int(payload["log_id"])},
    )

    message_hub.publish(
        "audit_log", {"action": "attach_trace", "log_id": int(payload["log_id"])}
    )


async def export_causal_path_ui(payload: Dict[str, Any], **_: Any) -> Dict[str, Any]:
    """Run :func:`export_causal_path` with params from the UI payload."""
    graph: InfluenceGraph = payload["graph"]
    node_id = payload.get("node_id")
    direction = payload.get("direction", "ancestors")
    depth = payload.get("depth", 3)

    result = export_causal_path(graph, node_id, direction=direction, depth=depth)
    message_hub.publish(
        "audit_log",
        {
            "action": "export_causal_path",
            "node_id": node_id,
            "direction": direction,
        },
    )
    return result


# Register causal audit route
async def causal_audit_ui(
    payload: Dict[str, Any], db: Session, **_: Any
) -> Dict[str, Any]:
    """Run :func:`trigger_causal_audit` from UI payload.

    Parameters
    ----------
    payload : dict
        Dictionary containing ``"log_id"`` and ``"graph"`` keys. Optional
        ``"hypothesis_id"`` may associate the audit with a hypothesis.
    db : Session
        Active database session used during the audit.

    Returns
    -------
    dict
        Minimal audit summary with ``causal_chain``, ``governance_review`` and
        ``commentary``.
    """
    log_id = payload["log_id"]
    graph: InfluenceGraph = payload["graph"]

    audit_result = trigger_causal_audit(
        db,
        log_id,
        graph,
        hypothesis_id=payload.get("hypothesis_id"),
        skip_commentary=payload.get("skip_commentary", False),
        skip_validation=payload.get("skip_validation", False),
    )

    minimal = {
        "causal_chain": audit_result.get("causal_chain"),
        "governance_review": audit_result.get("governance_review"),
        "commentary": audit_result.get("commentary"),
    }

    await hook_manager.trigger(
        events.AUDIT_LOG, {"action": "causal_audit", "log_id": log_id}
    )
    message_hub.publish("audit_log", {"action": "causal_audit", "log_id": log_id})
    return minimal


# Register routes with the frontend bridge
register_route_once(
    "causal_audit",
    causal_audit_ui,
    "Run a causal audit",
    "audit",
)
register_route_once(
    "log_hypothesis",
    log_hypothesis_ui,
    "Log a hypothesis for auditing",
    "audit",
)
register_route_once(
    "attach_trace",
    attach_trace_ui,
    "Attach audit trace data",
    "audit",
)
register_route_once(
    "export_causal_path",
    export_causal_path_ui,
    "Export causal path information",
    "audit",
)
