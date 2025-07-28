import protocols.agents.temporal_audit_agent as ta_module
from protocols.agents.temporal_audit_agent import TemporalAuditAgent


def test_audit_batch_process_event_sends_alert(monkeypatch):
    returned = {"flags": ["large_time_gap"], "detail": "x"}

    def fake_analyze(vals):
        fake_analyze.calls = vals
        return returned

    monkeypatch.setattr(ta_module, "analyze_temporal_consistency", fake_analyze)

    agent = TemporalAuditAgent()
    payload = {"validations": [{"foo": "bar"}]}
    result = agent.process_event({"event": "NEW_VALIDATION_BATCH", "payload": payload})

    assert result == returned
    assert agent.inbox[-1]["topic"] == "TEMPORAL_ALERT"
    assert agent.inbox[-1]["payload"]["flags"] == ["large_time_gap"]
    assert fake_analyze.calls == payload["validations"]

