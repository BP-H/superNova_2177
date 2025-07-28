"""Symbolic Trace Logger & Hypothesis Reference Engine (superNova_2177 v3.6)"""

import json
import uuid
from datetime import datetime
from typing import List, Dict, Optional, Any
import logging

from sqlalchemy.orm import Session

from causal_graph import InfluenceGraph
from db_models import SystemState, LogEntry

logger = logging.getLogger(__name__)
logger.propagate = False


from exceptions import DataParseError


def safe_json_loads(json_str: str, default=None, *, raise_on_error: bool = False):
    try:
        return json.loads(json_str) if json_str else (default or {})
    except (json.JSONDecodeError, TypeError) as exc:
        logger.exception(f"JSON decode failed: {json_str}")
        if raise_on_error:
            raise DataParseError(str(exc)) from exc
        return default or {}


def log_hypothesis_with_trace(
    hypothesis_text: str,
    causal_node_ids: List[str],
    db: Session,
    metadata: Optional[Dict[str, Any]] = None
) -> str:
    """
    Store a hypothesis log with its supporting causal node IDs and optional
    metadata. Returns the key used in SystemState.
    """
    payload = {
        "timestamp": datetime.utcnow().isoformat(),
        "hypothesis_text": hypothesis_text,
        "causal_node_ids": causal_node_ids,
        "metadata": metadata or {},
    }
    key = f"hypothesis_log_{uuid.uuid4().hex}"
    state = SystemState(key=key, value=json.dumps(payload))
    db.add(state)
    db.commit()
    return key


def export_causal_path(
    graph: InfluenceGraph,
    node_id: str,
    direction: str = "ancestors",
    depth: int = 3
) -> Dict[str, Any]:
    """
    Export a simplified causal trace path in either upstream or downstream
    direction.
    """
    if direction not in {"ancestors", "descendants"}:
        raise ValueError("direction must be 'ancestors' or 'descendants'")
    trace = (
        graph.trace_to_ancestors(node_id, max_depth=depth)
        if direction == "ancestors"
        else graph.trace_to_descendants(node_id, max_depth=depth)
    )

    path_nodes = []
    edge_list = []
    highlights = []

    for entry in trace:
        if not isinstance(entry, dict):
            logger.warning("Malformed trace entry (not a dict): %s", entry)
            continue

        node_id_val = entry.get("node_id")
        edge = entry.get("edge")

        if node_id_val is None or edge is None:
            logger.warning(
                "Malformed trace entry missing 'node_id' or 'edge': %s", entry
            )
            continue

        if not isinstance(edge, dict):
            logger.warning("Malformed trace entry edge not a dict: %s", entry)
            continue

        path_nodes.append(node_id_val)
        edge_list.append(
            (
                edge.get("source"),
                edge.get("target"),
                edge.get("edge_type", ""),
            )
        )

        node_data = entry.get("node_data", {})
        entropy = node_data.get("node_specific_entropy", 1.0)
        if entropy is None:
            entropy = 1.0
        if entropy < 0.25 or node_data.get("debug_payload"):
            highlights.append(node_id_val)
    return {
        "path_nodes": path_nodes,
        "edge_list": edge_list,
        "highlights": highlights,
    }


def attach_trace_to_logentry(
    log_id: int,
    causal_node_ids: List[str],
    db: Session,
    summary: Optional[str] = None
) -> None:
    """
    Attach causal node references and optional commentary to an existing
    LogEntry.
    """
    entry = db.query(LogEntry).filter(LogEntry.id == log_id).first()
    if not entry:
        raise ValueError(f"LogEntry {log_id} not found")

    _sentinel = object()
    existing = safe_json_loads(entry.payload or "{}", default=_sentinel)
    if existing is _sentinel:
        logger.warning("Failed to parse JSON payload for LogEntry %s", log_id)
        return

    existing["causal_node_ids"] = causal_node_ids
    if summary:
        existing["causal_commentary"] = summary

    entry.payload = json.dumps(existing)
    db.commit()


def generate_commentary_from_trace(trace: Dict[str, Any]) -> str:
    """
    Heuristic commentary generation based on node sequence and entropy.
    """
    # Safely pull the path information from the trace. ``get`` avoids raising
    # ``KeyError`` when the calling code provides incomplete data.
    path_nodes = trace.get("path_nodes") or []
    if not path_nodes:
        return "No significant causal chain found."

    chain = " → ".join(path_nodes)
    highlights = trace.get("highlights", [])
    highlight_text = (
        f" Notable nodes: {', '.join(highlights)}." if highlights else ""
    )

    return f"This trace follows the causal chain: {chain}.{highlight_text}"
