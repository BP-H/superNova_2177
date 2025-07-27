"""Simple semantic contradiction resolver for validator notes."""
from __future__ import annotations

from typing import Iterable

# Basic set of terms indicating contradiction or disagreement.  This avoids
# heavy NLP dependencies so it works in constrained test environments.
CONTRADICTION_TERMS = {
    "contradict",
    "refute",
    "oppose",
    "disagree",
    "inconsistent",
    "conflict",
    "counter",
    "denies",
}


def semantic_contradiction_resolver(text: str | None) -> bool:
    """Return ``True`` if the text semantically indicates a contradiction."""
    if not text:
        return False
    lower = text.lower()
    return any(term in lower for term in CONTRADICTION_TERMS)


__all__ = ["semantic_contradiction_resolver"]
