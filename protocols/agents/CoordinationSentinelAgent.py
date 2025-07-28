"""CoordinationSentinelAgent - monitors validator submissions for suspicious coordination."""

from typing import List, Dict, Any

from protocols.core.internal_protocol import InternalAgentProtocol
from network.network_coordination_detector import analyze_coordination_patterns


class CoordinationSentinelAgent(InternalAgentProtocol):
    """Automates network coordination analysis and emits flags."""

    def __init__(self) -> None:
        super().__init__()
        self.name = "CoordinationSentinel"
        self.receive("VALIDATIONS", self.inspect_validations)

    def inspect_validations(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Run coordination analysis on provided validations."""
        validations: List[Dict[str, Any]] = payload.get("validations", [])
        result = analyze_coordination_patterns(validations)
        self.send(
            "COORDINATION_RESULT",
            {
                "flags": result.get("flags", []),
                "clusters": result.get("coordination_clusters", {}),
                "risk": result.get("overall_risk_score", 0.0),
            },
        )
        return result
