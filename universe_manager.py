# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards
"""Universe lifecycle management utilities."""

from __future__ import annotations
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class Universe:
    """Container for universe state."""

    id: str
    owner_id: str
    owner_type: str
    parent_id: Optional[str] = None
    agents: List[str] = field(default_factory=lambda: ["HarmonyAgent"])
    metrics: Dict[str, float] = field(
        default_factory=lambda: {"Harmony Score": 0.0, "Karma": 0.0}
    )
    children: List[str] = field(default_factory=list)


class UniverseManager:
    """Create and lookup universes for different entities."""

    _universes: Dict[str, Universe] = {}
    _entity_index: Dict[Tuple[str, str], str] = {}

    def __init__(self) -> None:
        pass

    # ------------------------------------------------------------------
    @classmethod
    def initialize_for_entity(cls, entity_id: str, entity_type: str) -> str:
        """Return a universe ID for ``entity_id`` creating one if needed."""

        key = (entity_id, entity_type)
        if key in cls._entity_index:
            return cls._entity_index[key]

        universe_id = uuid.uuid4().hex
        uni = Universe(id=universe_id, owner_id=entity_id, owner_type=entity_type)
        cls._universes[universe_id] = uni
        cls._entity_index[key] = universe_id
        return universe_id

    # ------------------------------------------------------------------
    def get_universe(self, universe_id: str) -> Optional[Universe]:
        """Return the :class:`Universe` for ``universe_id`` if it exists."""

        return self._universes.get(universe_id)

    def list_universes(self, owner_id: str) -> List[Universe]:
        """List universes belonging to ``owner_id``."""

        return [u for u in self._universes.values() if u.owner_id == owner_id]

    # ------------------------------------------------------------------
    def register_child(self, parent_id: str, child_id: str) -> None:
        """Record ``child_id`` as a sub-universe of ``parent_id``."""

        parent = self._universes.get(parent_id)
        child = self._universes.get(child_id)
        if parent and child:
            child.parent_id = parent_id
            parent.children.append(child_id)
