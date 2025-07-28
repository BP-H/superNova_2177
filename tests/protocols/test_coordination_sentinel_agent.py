import protocols.agents.coordination_sentinel_agent as cs_agent_module
from protocols.agents.coordination_sentinel_agent import CoordinationSentinelAgent


def test_inspect_validations_emits_result(monkeypatch):
    sentinel = CoordinationSentinelAgent()
    expected = {
        "overall_risk_score": 0.42,
        "coordination_clusters": {"dummy": 1},
        "flags": ["flag1"],
    }
    monkeypatch.setattr(cs_agent_module, "analyze_coordination_patterns", lambda v: expected)

    result = sentinel.inspect_validations({"validations": [1]})

    assert result == expected
    assert sentinel.inbox[-1]["topic"] == "COORDINATION_RESULT"
    assert sentinel.inbox[-1]["payload"] == {
        "flags": expected["flags"],
        "clusters": expected["coordination_clusters"],
        "risk": expected["overall_risk_score"],
    }
