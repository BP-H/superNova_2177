from protocols.agents.harmony_synthesizer_agent import HarmonySynthesizerAgent


def test_generate_uses_provider_when_no_metrics():
    calls = []

    def provider():
        calls.append(True)
        return {"h": 1.0}

    agent = HarmonySynthesizerAgent(metrics_provider=provider)
    midi = agent.handle_generate({})

    assert calls and isinstance(midi, bytes)
    assert agent.inbox[-1]["topic"] == "MIDI_CREATED"
    assert agent.inbox[-1]["payload"]["metrics"] == {"h": 1.0}


def test_generate_prefers_payload_metrics():
    calls = []

    def provider():
        calls.append(True)
        return {"x": 0}

    agent = HarmonySynthesizerAgent(metrics_provider=provider)
    midi = agent.handle_generate({"metrics": {"a": 2}})

    assert not calls
    assert isinstance(midi, bytes)
    assert agent.inbox[-1]["payload"]["metrics"] == {"a": 2}
