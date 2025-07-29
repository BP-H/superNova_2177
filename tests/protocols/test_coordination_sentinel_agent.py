# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards
import importlib

import network.network_coordination_detector as detector
import protocols.agents.coordination_sentinel_agent as cs_module
from protocols.agents.coordination_sentinel_agent import CoordinationSentinelAgent


def test_inspect_validations_sends_result(monkeypatch):
    result_obj = {
        "flags": ["coordination"],
        "coordination_clusters": {"t": []},
        "overall_risk_score": 0.5,
    }

    def fake_analyze(vals):
        fake_analyze.calls = vals
        return result_obj

    monkeypatch.setattr(detector, "analyze_coordination_patterns", fake_analyze)
    importlib.reload(cs_module)

    agent = cs_module.CoordinationSentinelAgent()
    payload = {"validations": [{"v": 1}]}
    res = agent.inspect_validations(payload)

    assert res == result_obj
    assert agent.inbox[-1]["topic"] == "COORDINATION_RESULT"
    assert agent.inbox[-1]["payload"]["flags"] == ["coordination"]
    assert fake_analyze.calls == payload["validations"]

