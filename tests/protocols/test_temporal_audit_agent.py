# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards
import importlib

import temporal_consistency_checker as tcc
import protocols.agents.temporal_audit_agent as ta_module
from protocols.agents.temporal_audit_agent import TemporalAuditAgent


def test_audit_batch_alert_on_large_gap(monkeypatch):
    returned = {"flags": ["large_time_gap"], "detail": "x"}

    def fake_analyze(vals):
        fake_analyze.calls = vals
        return returned

    monkeypatch.setattr(tcc, "analyze_temporal_consistency", fake_analyze)
    importlib.reload(ta_module)

    agent = ta_module.TemporalAuditAgent()
    payload = {"validations": [{"foo": "bar"}]}
    result = agent.audit_batch(payload)

    assert result == returned
    assert agent.inbox[-1]["topic"] == "TEMPORAL_ALERT"
    assert set(agent.inbox[-1]["payload"]["flags"]) == {"large_time_gap"}
    assert fake_analyze.calls == payload["validations"]


def test_audit_batch_alert_on_disorder(monkeypatch):
    returned = {"flags": ["chronological_disorder"], "detail": "x"}

    def fake_analyze(vals):
        fake_analyze.calls = vals
        return returned

    monkeypatch.setattr(tcc, "analyze_temporal_consistency", fake_analyze)
    importlib.reload(ta_module)

    agent = ta_module.TemporalAuditAgent()
    payload = {"validations": [{"foo": "bar"}]}
    result = agent.audit_batch(payload)

    assert result == returned
    assert agent.inbox[-1]["topic"] == "TEMPORAL_ALERT"
    assert "chronological_disorder" in agent.inbox[-1]["payload"]["flags"]
    assert fake_analyze.calls == payload["validations"]

