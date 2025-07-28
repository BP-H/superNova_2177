"""
# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards
"""

from __future__ import annotations

import uuid
from typing import Dict


class UniverseManager:
    """Simple in-memory universe tracking service."""

    _universes: Dict[int, str] = {}

    @classmethod
    def initialize_for_entity(cls, user_id: int, species: str) -> str:
        """Initialize a universe for ``user_id`` and return its identifier."""
        if user_id not in cls._universes:
            cls._universes[user_id] = uuid.uuid4().hex
        return cls._universes[user_id]
