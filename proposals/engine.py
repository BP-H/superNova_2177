"""Lightweight proposal generation engine."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

DEFAULT_PROPOSALS: List[Dict[str, str]] = [
    {
        "title": "Annual quantum audit",
        "description": "Auto-propose annual audits via quantum simulations.",
    },
    {
        "title": "Cross-universe remix bridge",
        "description": "Enable cross-universe content with provenance tracking.",
    },
    {
        "title": "Karma staking yields",
        "description": "Implement karma staking for passive yields.",
    },
]


class ProposalEngine:
    """Generate governance proposals based on context."""

    def __init__(
        self,
        min_karma: int = 0,
        requires_certification: bool = False,
        universe_metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.min_karma = min_karma
        self.requires_certification = requires_certification
        self.universe_metadata = universe_metadata or {}

    # ------------------------------------------------------------------
    def generate(
        self, user: Dict[str, Any], universe_state: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Return proposal suggestions for ``user`` given ``universe_state``."""

        if user.get("karma", 0) < self.min_karma:
            return []
        if self.requires_certification and not user.get("is_certified"):
            return []

        proposals: List[Dict[str, Any]] = []
        for base in DEFAULT_PROPOSALS:
            p = dict(base)
            entropy = universe_state.get("entropy", 0.0)
            popularity = universe_state.get("popularity", 0.5)
            p.update(
                {
                    "urgency": "high" if entropy > 1.0 else "low",
                    "popularity": popularity,
                    "entropy": entropy,
                }
            )
            if self.universe_metadata:
                p["universe"] = self.universe_metadata
            proposals.append(p)
        return proposals

    # ------------------------------------------------------------------
    def list_proposals(
        self, karma: int, universe_state: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Return proposals for a user ``karma`` in the given ``universe_state``.

        This is a convenience wrapper around :meth:`generate` that constructs
        a minimal user dictionary based on the provided karma value and passes
        it through to ``generate``.
        """

        user = {"karma": karma}
        return self.generate(user, universe_state)


# Convenience function -------------------------------------------------


def generate_proposals(
    user: Dict[str, Any],
    universe_state: Dict[str, Any],
    *,
    min_karma: int = 0,
    requires_certification: bool = False,
    universe_metadata: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """Generate proposals filtered by ``user`` attributes."""

    engine = ProposalEngine(
        min_karma=min_karma,
        requires_certification=requires_certification,
        universe_metadata=universe_metadata,
    )
    return engine.generate(user, universe_state)
