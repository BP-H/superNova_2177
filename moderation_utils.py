# RFC_V5_1_INIT
"""Moderation helper stubs."""

from typing import Any
import re


def check_profanity(text: str) -> bool:
    """Return True if profanity detected (stub)."""
    banned = {"badword"}
    words = set(text.lower().split())
    return not banned.isdisjoint(words)


def has_active_consent(user: Any = None) -> bool:
    """Placeholder consent check."""
    return True


class Vaccine:
    """Simple text vaccine using regex-based filtering."""

    def __init__(self, config: Any):
        """Compile patterns from ``config.VAX_PATTERNS['block']``."""
        block = config.VAX_PATTERNS.get("block", [])
        self.patterns = [re.compile(p, re.IGNORECASE) for p in block]

    def scan(self, text: str) -> bool:
        """Return ``True`` if content passes vaccine checks."""
        lower = text.lower()
        for pat in self.patterns:
            if pat.search(lower):
                return False
        if check_profanity(text):
            return False
        return True
