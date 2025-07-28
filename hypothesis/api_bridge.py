from __future__ import annotations

from typing import Any, Dict, List

from sqlalchemy.orm import Session

import hypothesis_tracker as ht
from hypothesis_reasoner import (
    rank_hypotheses_by_confidence,
    synthesize_consensus_hypothesis,
)


async def register_hypothesis_ui(payload: Dict[str, Any], db: Session) -> str:
    """Register a new hypothesis from a UI payload.

    Parameters
    ----------
    payload : dict
        Expected to contain ``"text"`` and optional ``"metadata"``.
    db : Session
        Active database session used to persist the hypothesis.

    Returns
    -------
    str
        Generated hypothesis ID.
    """
    text = payload.get("text") or payload.get("hypothesis_text")
    if not isinstance(text, str) or not text.strip():
        raise ValueError("'text' is required to register a hypothesis")

    metadata = payload.get("metadata")
    if metadata is not None and not isinstance(metadata, dict):
        raise ValueError("'metadata' must be a dictionary if provided")

    return ht.register_hypothesis(text.strip(), db, metadata=metadata)


async def rank_hypotheses_ui(payload: Dict[str, Any], db: Session) -> List[Dict[str, Any]]:
    """Return top ranked hypotheses in concise form."""
    top_k = payload.get("top_k", 5)
    try:
        top_k = int(top_k)
    except (TypeError, ValueError):
        top_k = 5

    if top_k <= 0:
        top_k = 5

    return rank_hypotheses_by_confidence(db, top_k=top_k)


async def synthesize_hypotheses_ui(payload: Dict[str, Any], db: Session) -> str:
    """Create a consensus hypothesis from ``hypothesis_ids``."""
    ids = payload.get("hypothesis_ids")
    if not isinstance(ids, list) or not ids or not all(isinstance(i, str) for i in ids):
        raise ValueError("'hypothesis_ids' must be a non-empty list of strings")

    return synthesize_consensus_hypothesis(ids, db)
