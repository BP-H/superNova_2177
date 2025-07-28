import pytest
from protocols.agents.coordination_sentinel_agent import CoordinationSentinelAgent


def build_validations():
    vals = []
    for i in range(3):
        ts = f"2025-01-01T00:0{i}:00Z"
        note = "the quick brown fox jumps over the lazy dog"
        vals.append({
            "validator_id": "v1",
            "hypothesis_id": f"h{i}",
            "score": 0.8,
            "timestamp": ts,
            "note": note,
        })
        vals.append({
            "validator_id": "v2",
            "hypothesis_id": f"h{i}",
            "score": 0.8,
            "timestamp": ts,
            "note": note,
        })
    return vals


def test_coordination_sentinel_detects_risk():
    agent = CoordinationSentinelAgent()
    result = agent.inspect_validations({"validations": build_validations()})
    assert result["risk_breakdown"]["temporal"] >= 1
    assert agent.inbox and agent.inbox[-1]["topic"] == "COORDINATION_RESULT"

