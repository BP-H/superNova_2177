from __future__ import annotations

from typing import Any, Dict

from sqlalchemy.orm import Session

from db_models import SessionLocal
from hook_manager import HookManager
from hypothesis_reasoner import (
    rank_hypotheses_by_confidence as _rank_hypotheses_by_confidence,
    detect_conflicting_hypotheses as _detect_conflicting_hypotheses,
    synthesize_consensus_hypothesis as _synthesize_consensus_hypothesis,
)

ui_hook_manager = HookManager()


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


async def rank_hypotheses_ui(payload: Dict[str, Any], db: Session) -> Dict[str, Any]:
    """Return ranked hypotheses using an existing session."""
    top_k = payload.get("top_k", 5)
    try:
        top_k = int(top_k)
    except (TypeError, ValueError):
        top_k = 5

    ranking = _rank_hypotheses_by_confidence(db, top_k=top_k)
    await ui_hook_manager.trigger("hypothesis_ranking", ranking)
    return {"ranking": ranking}


async def synthesize_consensus_ui(payload: Dict[str, Any], db: Session) -> Dict[str, Any]:
    """Create a consensus hypothesis from ``hypothesis_ids``."""
    ids = payload.get("hypothesis_ids")
    if not isinstance(ids, list) or not ids or not all(isinstance(i, str) for i in ids):
        raise ValueError("'hypothesis_ids' must be a non-empty list of strings")

    new_id = _synthesize_consensus_hypothesis(ids, db)
    await ui_hook_manager.trigger("consensus_synthesized", {"hypothesis_id": new_id})
    return {"hypothesis_id": new_id}


async def rank_hypotheses_route(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Route helper for :func:`rank_hypotheses_ui` using ``SessionLocal``."""
    db = SessionLocal()
    try:
        return await rank_hypotheses_ui(payload, db)
    finally:
        db.close()


async def synthesize_consensus_route(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Route helper for :func:`synthesize_consensus_ui` using ``SessionLocal``."""
    db = SessionLocal()
    try:
        return await synthesize_consensus_ui(payload, db)
    finally:
        db.close()
