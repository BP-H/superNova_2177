"""TemporalAuditAgent – monitors validation timestamps for anomalies."""

import logging
from typing import Any, Dict, List

from temporal_consistency_checker import analyze_temporal_consistency
from protocols.core.internal_protocol import InternalAgentProtocol

logger = logging.getLogger("TemporalAuditAgent")


class TemporalAuditAgent(InternalAgentProtocol):
    """Runs temporal analysis and emits alerts for suspicious timing."""

    def __init__(self) -> None:
        super().__init__()
        self.name = "TemporalAuditAgent"
        self.receive("NEW_VALIDATION_BATCH", self.audit_batch)

    def audit_batch(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        validations: List[Dict[str, Any]] = payload.get("validations", [])
        result = analyze_temporal_consistency(validations)
        flags = set(result.get("flags", []))
        if {"large_time_gap", "chronological_disorder"} & flags:
            self.send("TEMPORAL_ALERT", {"result": result, "flags": list(flags)})
        return result
