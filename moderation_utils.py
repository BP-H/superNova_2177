# RFC_V5_1_INIT
"""Moderation helper stubs."""

from typing import Any


def check_profanity(text: str) -> bool:
    """Return True if profanity detected (stub)."""
    banned = {"badword"}
    words = set(text.lower().split())
    return not banned.isdisjoint(words)


def has_active_consent(user: Any = None) -> bool:
    """Placeholder consent check."""
    return True
