from __future__ import annotations

from typing import Any, Dict

from db_models import SessionLocal
from hook_manager import HookManager
from hypothesis_reasoner import (
    rank_hypotheses_by_confidence as _rank_hypotheses_by_confidence,
    detect_conflicting_hypotheses as _detect_conflicting_hypotheses,
)
from hypothesis_tracker import (
    register_hypothesis as _register_hypothesis,
    update_hypothesis_score as _update_hypothesis_score,
)

ui_hook_manager = HookManager()
hook_manager = HookManager()


async def rank_hypotheses_by_confidence_ui(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Rank hypotheses using the reasoning layer and emit an event."""
    top_k = int(payload.get("top_k", 5))
    db = SessionLocal()
    try:
        ranking = _rank_hypotheses_by_confidence(db, top_k=top_k)
    finally:
        db.close()
    await ui_hook_manager.trigger("hypothesis_ranking", ranking)
    return {"ranking": ranking}


async def detect_conflicting_hypotheses_ui(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Detect conflicting hypotheses and emit an event."""
    db = SessionLocal()
    try:
        conflicts = _detect_conflicting_hypotheses(db)
    finally:
        db.close()
    await ui_hook_manager.trigger("hypothesis_conflicts", conflicts)
    return {"conflicts": conflicts}


async def register_hypothesis_ui(payload: Dict[str, Any], db) -> str:
    """Register a hypothesis from UI input and emit an event."""
    text = payload.get("text") or payload.get("hypothesis_text")
    if not isinstance(text, str) or not text.strip():
        raise ValueError("'text' is required to register a hypothesis")

    metadata = payload.get("metadata")
    if metadata is not None and not isinstance(metadata, dict):
        raise ValueError("'metadata' must be a dict if provided")

    hypothesis_id = _register_hypothesis(text.strip(), db, metadata=metadata)

    await hook_manager.trigger("hypothesis_registered", {"hypothesis_id": hypothesis_id})
    return hypothesis_id


async def update_hypothesis_score_ui(payload: Dict[str, Any], db) -> bool:
    """Update hypothesis score from UI input and emit an event."""
    hypothesis_id = payload.get("hypothesis_id")
    if not isinstance(hypothesis_id, str) or not hypothesis_id:
        raise ValueError("'hypothesis_id' is required")

    score = payload.get("score")
    try:
        score = float(score)
    except (TypeError, ValueError):
        raise ValueError("'score' must be a number")

    status = payload.get("status")
    source_audit_id = payload.get("source_audit_id")
    reason = payload.get("reason")
    metadata_update = payload.get("metadata_update")
    if metadata_update is not None and not isinstance(metadata_update, dict):
        raise ValueError("'metadata_update' must be a dict if provided")

    result = _update_hypothesis_score(
        db,
        hypothesis_id,
        score,
        status=status,
        source_audit_id=source_audit_id,
        reason=reason,
        metadata_update=metadata_update,
    )

    await hook_manager.trigger(
        "hypothesis_score_updated",
        {"hypothesis_id": hypothesis_id, "score": score, "status": status},
    )
    return result
