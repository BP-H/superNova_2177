import protocols.agents.coordination_sentinel_agent as cs_module
from protocols.agents.coordination_sentinel_agent import CoordinationSentinelAgent


def test_inspect_validations_process_event(monkeypatch):
    result_obj = {"flags": ["coordination"], "coordination_clusters": {"t": []}, "overall_risk_score": 0.5}

    def fake_analyze(vals):
        fake_analyze.calls = vals
        return result_obj

    monkeypatch.setattr(cs_module, "analyze_coordination_patterns", fake_analyze)

    agent = CoordinationSentinelAgent()
    payload = {"validations": [{"v": 1}]}
    res = agent.process_event({"event": "VALIDATIONS", "payload": payload})

    assert res == result_obj
    assert agent.inbox[-1]["topic"] == "COORDINATION_RESULT"
    assert agent.inbox[-1]["payload"]["flags"] == ["coordination"]
    assert fake_analyze.calls == payload["validations"]

