# protocols/cross_universe_bridge_agent.py

"""CrossUniverseBridgeAgent -- verify cross-universe remix provenance.

This agent implements the rule described in RFC 003 (Cross-Universe Bridge
Validator). It records provenance metadata whenever a remix crosses universe
boundaries and exposes retrieval hooks for audit tools.
"""

from __future__ import annotations

from typing import Any, Dict, List

from protocols.core.internal_protocol import InternalAgentProtocol


class CrossUniverseBridgeAgent(InternalAgentProtocol):
    """Validate and track cross-universe remix provenance."""

    def __init__(self, llm_backend=None) -> None:
        super().__init__()
        self.name = "CrossUniverseBridge"
        self.llm_backend = llm_backend
        self._records: List[Dict[str, Any]] = []
        self.receive("REGISTER_BRIDGE", self.register_bridge)
        self.receive("GET_PROVENANCE", self.get_provenance)

    # ------------------------------------------------------------------
    # Event handlers
    # ------------------------------------------------------------------
    def register_bridge(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and store provenance for a cross-universe remix."""

        coin_id = payload.get("coin_id")
        src_universe = payload.get("source_universe")
        src_coin = payload.get("source_coin")
        proof = payload.get("proof")

        missing = [k for k in ("coin_id", "source_universe", "source_coin", "proof") if not payload.get(k)]
        if missing:
            return {"valid": False, "missing": missing}

        if self.llm_backend:
            self.llm_backend(f"verify {proof}")

        # avoid duplicate records for the same coin_id
        if any(r["coin_id"] == coin_id for r in self._records):
            return {"valid": False, "duplicate": True}

        entry = {
            "coin_id": coin_id,
            "source_universe": src_universe,
            "source_coin": src_coin,
            "proof": proof,
        }
        self._records.append(entry)
        return {"valid": True}

    def get_provenance(self, payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Return provenance details for ``coin_id``."""

        coin_id = payload.get("coin_id")
        return [r for r in self._records if r["coin_id"] == coin_id]
