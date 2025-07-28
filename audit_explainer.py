# audit_explainer.py — Interpretable Narrative Generator for Causal & Validation Chains (v3.9)
"""
This module serves as the introspection layer for the scientific reasoning engine,
tasked with narrating the system’s own decision-making processes in plain,
structured language. It explains why hypotheses were validated or falsified,
reconstructs causal chains, and surfaces risk factors, acting as the AI’s
conscience and narrator.
"""

import json
import logging
from datetime import datetime
from typing import List, Dict, Optional, Any
import collections # For potential future use in more complex string analysis
import dateutil.parser # For robust datetime parsing

from sqlalchemy.orm import Session
from sqlalchemy import func

from db_models import SystemState, LogEntry # For accessing logs and hypothesis data
import hypothesis_tracker as ht # For getting hypothesis records

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


def safe_db_query(db, model, id_field, fallback=None):
    try:
        result = db.query(model).filter_by(**{id_field[0]: id_field[1]}).first()
        return result if result else fallback
    except Exception:
        logger.exception(f"DB query failed for {model}")
        return fallback
import causal_graph as cg # For tracing causal graph nodes

# --- Constants for consistent key usage ---
AUDIT_SNAPSHOT_TRACE_PATH = ["trace", "trace_detail"] # Unified path for detailed trace data within audit snapshots
BIAS_FLAGS_METADATA_KEY = "bias_flags_detected" # Consistent key for bias flags in hypothesis metadata

# --- Configuration Placeholder ---
# These would typically come from superNova_2177.Config
class TempConfig:
    # Thresholds for flagging. These should ideally match or align with
    # Config values in hypothesis_meta_evaluator.py for consistency.
    LOW_ENTROPY_DELTA_THRESHOLD = 0.1
    OVER_RELIANCE_THRESHOLD = 0.5 # e.g., if one source/node accounts for >50% of support

    # Example edge types (if not directly imported from a central enum/constant file)
    EDGE_TYPE_FOLLOW = "follow"
    EDGE_TYPE_LIKE = "like"
    EDGE_TYPE_REMIX = "remix"
    EDGE_TYPE_SUPPORT = "support" # Example for a causal support edge


try:
    from config import Config as SystemConfig
    CONFIG = SystemConfig
except ImportError:
    CONFIG = TempConfig


def _parse_datetime_safely(dt_str: str) -> Optional[datetime]:
    """Safely parse datetime string, returning None on error."""
    try:
        return dateutil.parser.parse(dt_str)
    except (ValueError, TypeError, AttributeError):
        return None


def _get_hypothesis_record_safe(db: Session, hypothesis_id: str) -> Optional[Dict[str, Any]]:
    """Helper to retrieve a hypothesis record, handling potential parsing errors."""
    try:
        return ht._get_hypothesis_record(db, hypothesis_id)
    except Exception:
        logger.exception("Failed to load hypothesis record")
        return None


def _get_causal_audit_snapshot(db: Session, audit_ref_key: str) -> Optional[Dict[str, Any]]:
    """Helper to retrieve a causal audit snapshot from SystemState."""
    audit_record = safe_db_query(db, SystemState, ("key", audit_ref_key))
    if audit_record and audit_record.value:
        return safe_json_loads(audit_record.value)
    return None


def _get_log_entry_by_id(db: Session, log_id: int) -> Optional[LogEntry]:
    """Helper to retrieve a LogEntry by its integer ID."""
    return safe_db_query(db, LogEntry, ("id", log_id))


def explain_validation_reasoning(
    hypothesis_id: str, validation_id: Optional[int], db: Session
) -> Dict[str, Any]:
    """
    Returns a plain-language, human-readable explanation of why this hypothesis was
    validated or falsified.

    Returns:
        Dict[str, Any]: Explanation dictionary with fields:
            - summary (str): One-line plain English summary.
            - reasoning (List[str]): List of evidence/reasoning fragments.
            - supporting_nodes (List[str]): Key node IDs or phrases.
            - risk_flags (List[str]): E.g., "low_entropy_delta", "bias_by_source_module".
            - suggested_review (bool): True if human review is recommended.
    """
    explanation_summary = "Explanation not available."
    reasoning_fragments = []
    supporting_nodes_list = []
    risk_flags_list = []

    hypothesis = _get_hypothesis_record_safe(db, hypothesis_id)
    if not hypothesis:
        return {
            "summary": "Hypothesis not found.",
            "reasoning": [],
            "supporting_nodes": [],
            "risk_flags": ["hypothesis_not_found"],
            "suggested_review": True,
        }

    hyp_status = hypothesis.get("status", "open")
    hyp_score = hypothesis.get("score", 0.0)
    hyp_text = hypothesis.get("text", "No description.").strip()
    hyp_history = hypothesis.get("history", [])

    # Filter history by validation_id if provided
    relevant_history_entries = []
    if validation_id is not None:
        for entry in hyp_history:
            if entry.get("source_audit_id"):
                # Retrieve the audit snapshot to check its log_id
                audit_snapshot = _get_causal_audit_snapshot(db, entry["source_audit_id"])
                if audit_snapshot and audit_snapshot.get("log_id") == validation_id:
                    relevant_history_entries.append(entry)
                    break # Found the specific validation event
        if not relevant_history_entries:
            reasoning_fragments.append(
                f"No specific validation event found for log_id {validation_id} in hypothesis history."
            )
            # Set suggested_review based on explicit check at the end

    else:
        # If no specific validation_id, consider the latest resolution (most recent history entry)
        if hyp_history:
            relevant_history_entries = sorted(
                hyp_history,
                key=lambda x: _parse_datetime_safely(x.get("t", "")) or datetime.min,
            )
            if relevant_history_entries:
                relevant_history_entries = [relevant_history_entries[-1]] # Take the latest resolution

    # Determine explanation based on final or relevant history status
    if hyp_status == "validated":
        explanation_summary = f"Hypothesis '{hyp_text[:50]}...' was **validated** (Score: {hyp_score:.2f})."
        reasoning_fragments.append("The hypothesis achieved a high score based on accumulating evidence.")
    elif hyp_status == "falsified":
        explanation_summary = f"Hypothesis '{hyp_text[:50]}...' was **falsified** (Score: {hyp_score:.2f})."
        reasoning_fragments.append("Evidence emerged that contradicted the hypothesis.")
    elif hyp_status == "merged":
        explanation_summary = f"Hypothesis '{hyp_text[:50]}...' was **merged** into a broader consensus."
        reasoning_fragments.append("Its core claims were incorporated into a new, more robust hypothesis.")
    elif hyp_status == "inconclusive":
        explanation_summary = f"Hypothesis '{hyp_text[:50]}...' is **inconclusive**."
        reasoning_fragments.append("Insufficient or conflicting evidence, or it became stale without resolution.")
    else: # status == "open"
        explanation_summary = f"Hypothesis '{hyp_text[:50]}...' is currently **open**."
        reasoning_fragments.append("It is awaiting further evidence or validation.")

    # Gather supporting evidence
    supporting_nodes_list.extend(hypothesis.get("supporting_nodes", []))
    if supporting_nodes_list:
        reasoning_fragments.append(
            "Supported by evidence from key causal nodes: "
            f"{', '.join(supporting_nodes_list[:5])}"
            f"{'...' if len(supporting_nodes_list) > 5 else ''}."
        )

    # Process relevant audit sources
    audit_sources_processed = set()
    for entry in relevant_history_entries:
        audit_source_key = entry.get("source_audit_id")
        if audit_source_key and audit_source_key not in audit_sources_processed:
            audit_snapshot = _get_causal_audit_snapshot(db, audit_source_key)
            if audit_snapshot:
                audit_log_id = audit_snapshot.get("log_id", "N/A")
                audit_commentary = audit_snapshot.get("commentary", "No specific commentary.")
                validation_res = audit_snapshot.get("validation_outcome")
                
                reasoning_fragments.append(
                    f"Audit log #{audit_log_id} ({audit_source_key}): {audit_commentary}"
                )

                if validation_res:
                    deviation = validation_res.get("deviation")
                    if deviation is not None:
                         reasoning_fragments.append(f"Validation showed deviation: {deviation:.2f}.")

                # Check for low entropy delta from audit's metadata (if passed and stored)
                audit_summary_payload = audit_snapshot.get("triggered_by_payload", {})
                audit_result_metadata = audit_summary_payload.get(
                    "metadata", {}
                )  # Metadata might be here if trigger_causal_audit adds it
                entropy_delta = audit_result_metadata.get("entropy_delta")
                if entropy_delta is not None and abs(entropy_delta) < CONFIG.LOW_ENTROPY_DELTA_THRESHOLD:
                    risk_flags_list.append(f"low_entropy_delta (delta={entropy_delta:.2f})")
                    reasoning_fragments.append(
                        "Note: This audit involved a low entropy change, which may warrant closer review."
                    )

            audit_sources_processed.add(audit_source_key)

    # Check for per-hypothesis bias flags (from hypothesis_reasoner/meta_evaluator)
    # These are stored in the hypothesis's own 'metadata' by the reasoner/meta-evaluator
    hyp_meta = hypothesis.get("metadata", {})
    if hyp_meta.get(BIAS_FLAGS_METADATA_KEY):
        for flag_detail in hyp_meta[BIAS_FLAGS_METADATA_KEY]:
            bias_type = flag_detail.get('bias_type', 'unknown_bias')
            risk_flags_list.append(f"bias_flag:{bias_type}")
            reasoning_fragments.append(f"Potential bias detected: {flag_detail.get('details', 'No details')}")
            

    # Final suggested review logic: consolidate conditions
    suggested_review = False
    if hyp_status in ["falsified", "inconclusive"]:
        suggested_review = True
    if risk_flags_list: # Any risk flag implies suggested review
        suggested_review = True
    # If a specific validation_id was requested but not found
    if not relevant_history_entries and validation_id is not None:
        suggested_review = True


    return {
        "summary": explanation_summary,
        "reasoning": reasoning_fragments,
        "supporting_nodes": supporting_nodes_list,
        "risk_flags": sorted(list(set(risk_flags_list))), # Remove duplicates and sort for consistency
        "suggested_review": suggested_review,
    }


def trace_causal_chain(audit_ref_key: str, db: Session) -> List[Dict[str, Any]]:
    """
    Loads the causal audit snapshot from SystemState and reconstructs
    the chronological causal path that led to a decision.

    Returns:
        List[Dict[str, Any]]: A chronological list of event dictionaries, each with:
            - type: "node_event" or "edge_event"
            - timestamp: datetime (or isoformat string)
            - node_id/source/target: Any
            - edge_type (if edge event)
            - weight (if edge event)
            - entity_type, trigger_event, entropy values (if node event)
            - inference_commentary, debug_payload (if node event)
    """
    audit_snapshot = _get_causal_audit_snapshot(db, audit_ref_key)
    if not audit_snapshot:
        return [{"error": f"Causal audit snapshot '{audit_ref_key}' not found."}]

    # Unified path to trace details within the audit snapshot
    detailed_trace = audit_snapshot
    for key_part in AUDIT_SNAPSHOT_TRACE_PATH:
        if key_part in detailed_trace:
            detailed_trace = detailed_trace[key_part]
        else:
            return [{"error": "Detailed trace data missing in audit snapshot."}]

    # Recreate a temporary InfluenceGraph to access node/edge data easily
    temp_graph = cg.InfluenceGraph()
    # Add nodes with their full data from the snapshot
    for node_data_raw in detailed_trace.get("path_nodes_data", []):
        node_id = node_data_raw.get("id")
        if node_id:
            temp_graph.add_node(node_id, **{k:v for k,v in node_data_raw.items() if k != 'id'})
    
    # Add edges with their full data from the snapshot
    for edge_data_raw in detailed_trace.get("edge_list_data", []): # This field now expected
        source = edge_data_raw.get("source")
        target = edge_data_raw.get("target")
        if source is not None and target is not None:
            # Assuming add_edge can take full data dict or individual params
            temp_graph.add_edge(
                source,
                target,
                **{k: v for k, v in edge_data_raw.items() if k not in ['source', 'target']},
            )


    events_in_chain = []

    # Collect Node Events
    for node_id in temp_graph.graph.nodes():
        node_attrs = temp_graph.graph.nodes.get(node_id, {})
        timestamp = _parse_datetime_safely(node_attrs.get("timestamp")) or datetime.min # Safe parse
        
        events_in_chain.append({
            "type": "node_event",
            "timestamp": timestamp,
            "node_id": node_id,
            "entity_type": node_attrs.get("entity_type"),
            "trigger_event": node_attrs.get("trigger_event"),
            "source_module": node_attrs.get("source_module"),
            "system_entropy_at_creation": node_attrs.get("system_entropy_at_creation"),
            "node_specific_entropy": node_attrs.get("node_specific_entropy"),
            "inference_commentary": node_attrs.get("inference_commentary"),
            "debug_payload": node_attrs.get("debug_payload"),
        })

    # Collect Edge Events
    for u, v in temp_graph.graph.edges():
        edge_attrs = temp_graph.graph.get_edge_data(u, v, {})
        timestamp = _parse_datetime_safely(edge_attrs.get("timestamp")) or datetime.min # Safe parse

        events_in_chain.append({
            "type": "edge_event",
            "timestamp": timestamp,
            "source": u,
            "target": v,
            "edge_type": edge_attrs.get("edge_type"),
            "weight": edge_attrs.get("weight"),
        })

    # Sort all events chronologically
    reconstructed_chain = sorted(events_in_chain, key=lambda x: x["timestamp"])
    
    # Convert datetime objects back to isoformat strings for JSON compatibility
    for event in reconstructed_chain:
        if isinstance(event["timestamp"], datetime):
            event["timestamp"] = event["timestamp"].isoformat()

    return reconstructed_chain


def summarize_bias_impact_on(hypothesis_id: str, db: Session) -> Dict[str, Any]:
    """
    If a bias flag exists for this hypothesis (e.g., from hypothesis_reasoner.py or
    hypothesis_meta_evaluator.py, stored in its metadata), explains it in natural language.
    Does not use the system-wide meta_eval_JUDGE_v1 blob for hypothesis-specific bias.

    Returns:
        Dict[str, Any]: Summary of bias impact with fields:
            - summary (str): Overall one-line summary of biases.
            - bias_details (List[Dict]): Detailed list of detected biases for this hypothesis.
    """
    hypothesis = _get_hypothesis_record_safe(db, hypothesis_id)
    if not hypothesis:
        return {"summary": "Hypothesis not found.", "bias_details": []}

    bias_details = []
    # Retrieve bias flags from the hypothesis's own metadata
    hyp_metadata = hypothesis.get("metadata", {})
    detected_biases = hyp_metadata.get(BIAS_FLAGS_METADATA_KEY, [])

    if not detected_biases:
        return {"summary": "No specific biases detected for this hypothesis.", "bias_details": []}

    summary_text = "Potential biases identified influencing this hypothesis's judgment: "
    for i, bias in enumerate(detected_biases):
        bias_type = bias.get("bias_type", "unknown bias")
        details = bias.get("details", "No specific details provided.")
        magnitude = bias.get("magnitude")
        severity = bias.get("severity_estimate", "unknown")

        bias_details.append({
            "type": bias_type,
            "magnitude": magnitude,
            "severity": severity,
            "explanation": details,
        })
        summary_text += f"'{bias_type}' (Severity: {severity}){'.' if i == len(detected_biases) - 1 else '; '}"
    
    return {
        "summary": summary_text.strip(),
        "bias_details": bias_details,
    }
