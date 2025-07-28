# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards
# introspection_pipeline.py — End-to-End Self-Audit Orchestrator (v3.9+)
# isort:skip_file
"""
A unifying layer that connects trigger_causal_audit, explain_validation_reasoning,
bias analysis, causal trace, and report formatter. It orchestrates a complete
introspection audit on a given hypothesis and outputs a bundled report.
"""

import json  # For parsing LogEntry.value
import logging
from typing import Any, Dict, List, Optional, cast

from sqlalchemy.orm import Session

import hypothesis_tracker as ht  # hypothesis_tracker is now ORM-based internally, but its public methods return dicts

# Imports from previous modules
from audit_explainer import (
    explain_validation_reasoning,
    summarize_bias_impact_on,
    trace_causal_chain,
)
from auditor_report_formatter import render_markdown_report  # noqa: F401
from auditor_report_formatter import generate_structured_audit_bundle

# DB Models
from db_models import (
    LogEntry,
)  # LogEntry is still needed here for querying validation logs
from exceptions import DataParseError

logger = logging.getLogger(__name__)
logger.propagate = False


def safe_json_loads(json_str: str, default=None, *, raise_on_error: bool = False):
    """Safely parse a JSON string.

    Args:
        json_str (str): The JSON-formatted string to decode.
        default (Any, optional): Value returned if decoding fails or ``json_str`` is empty.

    Returns:
        Any: The decoded JSON object or ``default``/empty ``dict`` on failure.
    """
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


def run_full_audit(hypothesis_id: str, db: Session) -> Dict[str, Any]:
    """
    Performs a full introspection audit for a given hypothesis and returns a structured report bundle.

    Args:
        hypothesis_id (str): The unique identifier of the hypothesis to audit.
        db (Session): SQLAlchemy database session.

    Returns:
        Dict[str, Any]: A structured dictionary containing the full audit report,
                        or an error message if the hypothesis/logs are not found.
    """
    # 1. Load the hypothesis using hypothesis_tracker's compatible dict-returning method
    # hypothesis_tracker internally uses HypothesisRecord ORM but returns data as a dict for compatibility.
    try:
        hypothesis_data = ht._get_hypothesis_record(db, hypothesis_id)
    except Exception:
        logger.exception("Failed to load hypothesis record")
        return {"error": f"Hypothesis '{hypothesis_id}' not found."}

    if not hypothesis_data:
        return {"error": f"Hypothesis '{hypothesis_id}' not found."}

    # Extract hypothesis text preview for the formatter (assuming 'text' key is provided by hypothesis_tracker's dict output)  # noqa: E501
    hypothesis_text_preview = hypothesis_data.get("text", "N/A description")[:120]

    # 2. Determine the latest validation log entry associated with this hypothesis
    validation_log_ids: List[int] = hypothesis_data.get("validation_log_ids", [])
    latest_validation_log_id: Optional[int] = None
    latest_causal_audit_ref: Optional[str] = None

    if validation_log_ids:
        # Query LogEntry using the IDs and order by timestamp to get the latest
        # LogEntry's payload is a TEXT column storing JSON
        try:
            query = db.query(LogEntry)
            try:
                query = query.filter(LogEntry.id.in_(validation_log_ids))
            except Exception:
                query = query.filter(None)  # no-op for stubbed query objects
            log_entries_for_hyp = query.all()
        except Exception:
            logger.exception("DB query failed for LogEntry")
            log_entries_for_hyp = []

        parsed_logs: List[Dict[str, Any]] = []
        for log_entry in log_entries_for_hyp:
            if not getattr(log_entry, "payload", None):
                logger.warning(
                    "Skipping log entry %s with missing payload",
                    getattr(log_entry, "id", "<unknown>"),
                )
                continue

            try:
                log_value_payload = safe_json_loads(
                    cast(str, log_entry.payload), raise_on_error=True
                )
                parsed_logs.append(
                    {
                        "id": log_entry.id,
                        "timestamp": log_entry.timestamp,
                        "causal_audit_ref": log_value_payload.get("causal_audit_ref"),
                    }
                )
            except DataParseError:
                logger.warning(
                    "Skipping malformed log entry %s: %s",
                    getattr(log_entry, "id", "<unknown>"),
                    getattr(log_entry, "payload", "<no payload>"),
                )

        if parsed_logs:
            # Sort by timestamp (or ID if timestamps are identical) to find the 'latest'
            latest_parsed_log = sorted(
                parsed_logs, key=lambda x: x["timestamp"], reverse=True
            )[0]
            latest_validation_log_id = latest_parsed_log["id"]
            latest_causal_audit_ref = latest_parsed_log["causal_audit_ref"]

    if not latest_validation_log_id or not latest_causal_audit_ref:
        return {
            "error": f"No valid causal audit reference found for hypothesis '{hypothesis_id}' via validation logs."
        }

    # 3. Run Explanation Engine (audit_explainer.py)
    # Pass the specific validation_id to explain_validation_reasoning
    explanation_output = explain_validation_reasoning(
        hypothesis_id, latest_validation_log_id, db
    )

    # 4. Summarize Bias (audit_explainer.py)
    bias_data_output = summarize_bias_impact_on(hypothesis_id, db)

    # 5. Causal Trace (audit_explainer.py)
    # Use the retrieved causal_audit_ref directly
    causal_chain_output = trace_causal_chain(latest_causal_audit_ref, db)

    # 6. Bundle into reports (auditor_report_formatter.py)
    audit_bundle = generate_structured_audit_bundle(
        explainer_output=explanation_output,
        bias_data=bias_data_output,
        causal_chain_data=causal_chain_output,
        hypothesis_id=hypothesis_id,
        hypothesis_text_preview=hypothesis_text_preview,
        validation_id=latest_validation_log_id,
    )

    return audit_bundle
