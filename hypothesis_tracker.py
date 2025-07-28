# hypothesis_tracker.py — Scientific Hypothesis Lifecycle (superNova_2177 v3.7 - ORM Native)
"""
Module for structured tracking, validation, and scoring of scientific hypotheses
within the superNova_2177 system. This version has been refactored to use a
dedicated HypothesisRecord ORM model for persistence, replacing SystemState for
hypothesis storage.
"""

import json
import logging
from datetime import datetime
import uuid
from typing import List, Dict, Optional, Any
import math # For isfinite check

from sqlalchemy.orm import Session
from sqlalchemy import func

logger = logging.getLogger(__name__)
logger.propagate = False


from exceptions import DataParseError


def safe_json_loads(json_str: str, default=None, *, raise_on_error: bool = False):
    """Safely parse JSON and optionally raise ``DataParseError`` on failure."""
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

# Import the new HypothesisRecord ORM model directly
from db_models import HypothesisRecord #


def _load_hypothesis_record_from_db(db: Session, hypothesis_id: str) -> Optional[HypothesisRecord]:
    """
    Helper to retrieve a HypothesisRecord ORM object from the database.

    Args:
        db (Session): SQLAlchemy database session.
        hypothesis_id (str): The unique ID of the hypothesis.

    Returns:
        Optional[HypothesisRecord]: The HypothesisRecord ORM object if found, else None.
    """
    return safe_db_query(db, HypothesisRecord, ("id", hypothesis_id))


def _store_hypothesis_record_to_db(hypothesis: HypothesisRecord, db: Session) -> None:
    """
    Helper to save or update a HypothesisRecord ORM object in the database.

    Args:
        hypothesis (HypothesisRecord): The HypothesisRecord ORM object to save/update.
        db (Session): SQLAlchemy database session.
    """
    # db.merge handles both inserting new objects and updating existing ones
    db.merge(hypothesis)
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        logger.exception(f"Error saving hypothesis record {hypothesis.id}")
        raise RuntimeError(f"Failed to save hypothesis: {hypothesis.id}") from e


def _get_hypothesis_record(db: Session, hypothesis_id: str) -> Optional[Dict[str, Any]]:
    """Return a hypothesis record as a dictionary if present."""
    record = _load_hypothesis_record_from_db(db, hypothesis_id)
    if not record:
        return None

    return {
        "id": record.id,
        "text": record.description,
        "status": record.status,
        "score": record.score,
        "validation_log_ids": record.validation_log_ids or [],
        "metadata": record.metadata_json or {},
        "created_at": record.created_at.isoformat() if record.created_at else "",
        "history": record.history or [],
        "notes": record.notes,
        "audit_sources": record.audit_sources or [],
    }


def register_hypothesis(text: str, db: Session, metadata: Optional[Dict[str, Any]] = None) -> str:
    """
    Registers a new hypothesis, storing it using the HypothesisRecord ORM model.
    Initializes with status='open', score=0.0.
    Returns the generated hypothesis_id.

    Args:
        text (str): The proposed causal reasoning or scientific insight.
        db (Session): SQLAlchemy database session.
        metadata (Optional[Dict[str, Any]]): Optional metadata to store with the hypothesis.

    Returns:
        str: The generated hypothesis_id.
    """
    now_dt = datetime.utcnow()  # Get datetime object
    now_iso = now_dt.isoformat()  # Convert to ISO string for storage
    timestamp_for_id = int(now_dt.timestamp())  # Use timestamp from datetime object for ID
    unique_part = uuid.uuid4().hex[:8]
    hypothesis_id = f"HYP_{timestamp_for_id}_{unique_part}"  # Keep HYP_ prefix in the ID and add randomness

    new_hypothesis_record = HypothesisRecord(
        id=hypothesis_id,
        title=text[:255] if len(text) > 255 else text,  # Truncate for title field if too long
        description=text,
        created_at=now_dt,  # Store datetime object
        status="open",
        score=0.0,
        metadata_json=metadata or {},
    )

    # Ensure mutable JSON columns are initialized before use
    if new_hypothesis_record.history is None:
        new_hypothesis_record.history = []
    if new_hypothesis_record.notes is None:
        new_hypothesis_record.notes = ""

    new_hypothesis_record.history.append({
        "t": now_iso, # Use ISO string for history entry
        "score": 0.0,
        "status": "open",
        "event": "initial_registration"
    })
    new_hypothesis_record.notes = "Initial registration.\n" # Start notes as a string

    _store_hypothesis_record_to_db(new_hypothesis_record, db)
    return hypothesis_id


def update_hypothesis_score(
    db: Session,
    hypothesis_id: str,
    new_score: float,
    *,
    status: Optional[str] = None,
    source_audit_id: Optional[str] = None,
    reason: Optional[str] = None,
    metadata_update: Optional[Dict[str, Any]] = None, # Added to allow updating metadata
) -> bool:
    """
    Updates the score and optional status for an existing hypothesis.
    Stores traceability fields like `source_audit_id` (e.g., from `trigger_causal_audit`)
    and `reason` (e.g., 'matched observed data').
    Returns True if update successful, False if not found.

    Args:
        db (Session): SQLAlchemy database session.
        hypothesis_id (str): The ID of the hypothesis to update.
        new_score (float): The new score for the hypothesis.
        status (Optional[str]): Optional new status for the hypothesis.
        source_audit_id (Optional[str]): Reference to the causal audit that triggered the update.
        reason (Optional[str]): Brief reason for the score update.
        metadata_update (Optional[Dict[str, Any]]): Dictionary to merge into the hypothesis's metadata.

    Returns:
        bool: True if update successful, False if not found.
    """
    record = _load_hypothesis_record_from_db(db, hypothesis_id)
    if not record:
        return False

    if not math.isfinite(new_score):
        logger.warning(
            "Attempted to set non-finite score for hypothesis %s: %s",
            hypothesis_id,
            new_score,
        )
        return False

    record.score = new_score
    if status:
        record.status = status

    # Update metadata field (JSON column)
    if metadata_update:
        # Load existing JSON, update, then reassign to trigger ORM change detection
        current_metadata = record.metadata_json if isinstance(record.metadata_json, dict) else {}
        current_metadata.update(metadata_update)
        record.metadata_json = current_metadata

    history_entry = {
        "t": datetime.utcnow().isoformat(), # Use ISO string for history entry
        "score": new_score,
        "status": status if status else record.status,
        "event": "score_update"
    }
    if source_audit_id:
        history_entry["source_audit_id"] = source_audit_id
        # Append to audit_sources (JSON column, list)
        if not isinstance(record.audit_sources, list): record.audit_sources = [] # Defensive
        record.audit_sources.append(source_audit_id)
    if reason:
        history_entry["reason"] = reason
        record.notes = (record.notes or "") + f"[{datetime.utcnow().isoformat()}] Score updated ({reason}): {new_score}.\n"
    else:
        record.notes = (record.notes or "") + f"[{datetime.utcnow().isoformat()}] Score updated: {new_score}.\n"

    # Append to history (JSON column, list)
    if not isinstance(record.history, list): record.history = [] # Defensive
    record.history.append(history_entry)

    _store_hypothesis_record_to_db(record, db)
    return True


def attach_evidence_to_hypothesis(
    db: Session,
    hypothesis_id: str,
    node_ids: List[str],
    log_ids: List[int],
    *,
    summary_note: Optional[str] = None,
) -> bool:
    """
    Attaches causal node IDs and validation log IDs to an existing hypothesis.
    Optionally appends a human-readable `summary_note`.
    
    Args:
        db (Session): SQLAlchemy database session.
        hypothesis_id (str): The ID of the hypothesis to attach evidence to.
        node_ids (List[str]): List of causal node IDs providing supporting evidence.
        log_ids (List[int]): List of LogEntry IDs used in validations.
        summary_note (Optional[str]): A brief summary note about the evidence.

    Returns:
        bool: True if update successful, False if not found.
    """
    record = _load_hypothesis_record_from_db(db, hypothesis_id)
    if not record:
        return False

    # Append to validation_log_ids (JSON column, list)
    if not isinstance(record.validation_log_ids, list): record.validation_log_ids = [] # Defensive
    for log_id in log_ids:
        if log_id not in record.validation_log_ids: # Ensure uniqueness
            record.validation_log_ids.append(log_id)

    # Attach supporting_nodes information to metadata (JSON column, dict)
    current_metadata = record.metadata_json if isinstance(record.metadata_json, dict) else {}
    if 'supporting_nodes_history' not in current_metadata:
        current_metadata['supporting_nodes_history'] = []
    # Append new nodes, ensuring uniqueness within the history
    current_nodes_in_history = set(current_metadata['supporting_nodes_history'])
    current_metadata['supporting_nodes_history'].extend([n for n in node_ids if n not in current_nodes_in_history])
    record.metadata_json = current_metadata # Reassign to ensure ORM detects change

    note_text = f"Evidence attached: Nodes {node_ids}, Logs {log_ids}."
    if summary_note:
        note_text += f" Summary: {summary_note}"
    record.notes = (record.notes or "") + f"[{datetime.utcnow().isoformat()}] {note_text}\n"

    _store_hypothesis_record_to_db(record, db)
    return True


def evaluate_hypothesis_trajectory(
    db: Session,
    hypothesis_id: str
) -> Dict[str, Any]:
    """
    Analyzes the evolution of the hypothesis — changes in score, status,
    and validations over time. Returns a compact summary.
    
    Args:
        db (Session): SQLAlchemy database session.
        hypothesis_id (str): The ID of the hypothesis to evaluate.

    Returns:
        Dict[str, Any]: A compact summary of the hypothesis's trajectory.
    """
    record = _load_hypothesis_record_from_db(db, hypothesis_id)
    if not record:
        return {
            "error": "Hypothesis not found",
            "trend": "unknown",
            "recent_validations": 0,
            "last_status": "unknown",
            "current_score": 0.0,
            "hypothesis_id": hypothesis_id # Include ID for context
        }

    history = sorted(record.history or [], key=lambda x: x.get("t", ""))
    scores = [entry.get("score", 0.0) for entry in history]

    trend = "stable"
    if len(scores) >= 2:
        if scores[-1] > scores[0]:
            trend = "increasing"
        elif scores[-1] < scores[0]:
            trend = "declining"

    recent_validations = len(record.validation_log_ids or [])
    last_status = record.status or "unknown"
    current_score = record.score or 0.0

    return {
        "hypothesis_id": record.id,
        "text_preview": (record.description[:100] + "..." if record.description and len(record.description) > 100 else record.description) or "N/A",
        "trend": trend,
        "recent_validations": recent_validations,
        "last_status": last_status,
        "current_score": current_score,
        "total_history_entries": len(history),
        "created_at": record.created_at.isoformat() if record.created_at else "N/A",
        "last_updated_at": record.updated_at.isoformat() if record.updated_at else "N/A"
    }
