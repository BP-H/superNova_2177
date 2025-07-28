from __future__ import annotations

from typing import Any, Dict

from db_models import SessionLocal
from hook_manager import HookManager
from hypothesis_reasoner import (
    rank_hypotheses_by_confidence as _rank_hypotheses_by_confidence,
    detect_conflicting_hypotheses as _detect_conflicting_hypotheses,
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
