"""QuantumResonanceAgent - models symbolic resonance using quantum simulation utilities."""

from __future__ import annotations

import logging
from typing import Any, Dict, List

from quantum_sim import QuantumContext
from protocols.core.internal_protocol import InternalAgentProtocol

logger = logging.getLogger("QuantumResonanceAgent")


class QuantumResonanceAgent(InternalAgentProtocol):
    """Track interaction resonance and expose resonance metrics."""

    def __init__(self, llm_backend=None) -> None:
        super().__init__()
        self.name = "QuantumResonance"
        self.qc = QuantumContext(simulate=True)
        self.llm_backend = llm_backend
        self.receive("USER_INTERACTION", self.record_interaction)
        self.receive("QUERY_RESONANCE", self.query_resonance)
        self.receive("ADJUST_FOR_ENTROPY", self.adjust_for_entropy)

    # ------------------------------------------------------------------
    # Event handlers
    # ------------------------------------------------------------------
    def record_interaction(self, payload: Dict[str, Any]) -> Dict[str, str]:
        """Entangle ``source`` and ``target`` users."""
        src = payload.get("source")
        dst = payload.get("target")
        if src is None or dst is None:
            return {"error": "source and target required"}
        strength = float(payload.get("strength", 1.0))
        self.qc.entangle_entities(src, dst, influence_factor=strength)
        logger.debug("entangled %s <-> %s (%.2f)", src, dst, strength)
        return {"status": "ok"}

    def query_resonance(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Return resonance metrics for provided users."""
        users: List[Any] = payload.get("users", [])
        if not isinstance(users, list):
            users = [users]
        result = self.qc.quantum_prediction_engine(users)
        mean_prob = (
            sum(result["predicted_interactions"].values()) / len(users)
            if users
            else 0.0
        )
        resonance = self.qc.measure_superposition(mean_prob)
        response = {
            "resonance_level": resonance["value"],
            **result,
        }
        if self.llm_backend:
            note = self.llm_backend(f"Resonance summary: {response}")
            response["llm_note"] = note
        return response

    def adjust_for_entropy(self, payload: Dict[str, Any]) -> Dict[str, float]:
        """Adapt decoherence rate based on observed entropy."""
        entropy = float(payload.get("entropy", 0.0))
        rate = self.qc.adapt_decoherence_rate(entropy)
        return {"decoherence_rate": rate}
