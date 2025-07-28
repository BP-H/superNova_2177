import pytest
from protocols.agents.HarmonySynthesizerAgent import HarmonySynthesizerAgent


def test_handle_generate_uses_provider_and_emits_event(monkeypatch):
    sentinel = b"notes"
    dummy_metrics = {"val": 1.0}

    def dummy_provider():
        return dummy_metrics

    def fake_generate(metrics):
        assert metrics is dummy_metrics
        return sentinel

    monkeypatch.setattr(
        "protocols.agents.HarmonySynthesizerAgent.generate_midi_from_metrics",
        fake_generate,
    )

    agent = HarmonySynthesizerAgent(metrics_provider=dummy_provider)

    result = agent.handle_generate()

    assert result == sentinel
    assert agent.inbox[-1] == {
        "topic": "MIDI_CREATED",
        "payload": {"midi": sentinel, "metrics": dummy_metrics},
    }

