"""
audit_bridge.py - Symbolic Trace Logger & Hypothesis Reference Engine (superNova_2177 v3.6)
"""

import json
import uuid
from datetime import datetime
from typing import List, Dict, Optional, Any

from sqlalchemy.orm import Session

from causal_graph import InfluenceGraph
from db_models import SystemState, LogEntry


def log_hypothesis_with_trace(
    hypothesis_text: str,
    causal_node_ids: List[str],
    db: Session,
    metadata: Optional[Dict[str, Any]] = None
) -> str:
    """
    Store a hypothesis log with its supporting causal node IDs and optional metadata.
    Returns the key used in SystemState.
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
    Export a simplified causal trace path in either upstream or downstream direction.
    """
    if direction not in {"ancestors", "descendants"}:
        raise ValueError("direction must be 'ancestors' or 'descendants'")
    trace = (
        graph.trace_to_ancestors(node_id, max_depth=depth)
        if direction == "ancestors"
        else graph.trace_to_descendants(node_id, max_depth=depth)
    )
    path_nodes = [entry["node_id"] for entry in trace]
    edge_list = [
        (entry["edge"]["source"], entry["edge"]["target"], entry["edge"].get("edge_type", ""))
        for entry in trace
    ]
    highlights = []
    for entry in trace:
        node_data = entry.get("node_data", {})
        entropy = node_data.get("node_specific_entropy", 1.0)
        if entropy is None:
            entropy = 1.0
        if entropy < 0.25 or node_data.get("debug_payload"):
            highlights.append(entry["node_id"])
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
    Attach causal node references and optional commentary to an existing LogEntry.
    """
    entry = db.query(LogEntry).filter(LogEntry.id == log_id).first()
    if not entry:
        raise ValueError(f"LogEntry {log_id} not found")

    existing = json.loads(entry.value or "{}")
    existing["causal_node_ids"] = causal_node_ids
    if summary:
        existing["causal_commentary"] = summary

    entry.value = json.dumps(existing)
    db.commit()


def generate_commentary_from_trace(trace: Dict[str, Any]) -> str:
    """
    Heuristic commentary generation based on node sequence and entropy.
    """
    if not trace["path_nodes"]:
        return "No significant causal chain found."

    chain = " → ".join(trace["path_nodes"])
    highlights = trace.get("highlights", [])
    highlight_text = f" Notable nodes: {', '.join(highlights)}." if highlights else ""

    return f"This trace follows the causal chain: {chain}.{highlight_text}"
