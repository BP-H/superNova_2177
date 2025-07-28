import protocols.agents.harmony_synthesizer_agent as hs_agent_module
from protocols.agents.harmony_synthesizer_agent import HarmonySynthesizerAgent


def test_handle_generate_with_provider(monkeypatch):
    midi = b"abc"
    monkeypatch.setattr(hs_agent_module, "generate_midi_from_metrics", lambda m: midi)

    provided_metrics = {"x": 1.0}

    def provider():
        return provided_metrics

    agent = HarmonySynthesizerAgent(metrics_provider=provider)
    result = agent.handle_generate()

    assert result == midi
    assert agent.inbox[-1]["topic"] == "MIDI_CREATED"
    assert agent.inbox[-1]["payload"] == {"midi": midi, "metrics": provided_metrics}


def test_handle_generate_payload_only(monkeypatch):
    midi = b"xyz"
    monkeypatch.setattr(hs_agent_module, "generate_midi_from_metrics", lambda m: midi)

    metrics = {"y": 2}
    agent = HarmonySynthesizerAgent()
    result = agent.handle_generate({"metrics": metrics})

    assert result == midi
    assert agent.inbox[-1]["topic"] == "MIDI_CREATED"
    assert agent.inbox[-1]["payload"] == {"midi": midi, "metrics": metrics}

def test_process_event_generate(monkeypatch):
    midi = b"evt"
    monkeypatch.setattr(hs_agent_module, "generate_midi_from_metrics", lambda m: midi)
    agent = HarmonySynthesizerAgent()
    result = agent.process_event({"event": "GENERATE_MIDI", "payload": {"metrics": {"a": 1}}})
    assert result == midi
    assert agent.inbox[-1]["topic"] == "MIDI_CREATED"
    assert agent.inbox[-1]["payload"]["midi"] == midi

