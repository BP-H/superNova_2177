import pytest

from protocols.agents.cross_universe_bridge_agent import CrossUniverseBridgeAgent


def test_register_and_get_provenance():
    agent = CrossUniverseBridgeAgent()
    payload = {
        "coin_id": "c123",
        "source_universe": "U1",
        "source_coin": "s456",
        "proof": "p789",
    }
    result = agent.register_bridge(payload)
    assert result == {"valid": True}

    provenance = agent.get_provenance({"coin_id": "c123"})
    assert provenance == [payload]


def test_llm_backend_called():
    calls = []

    def backend(prompt: str):
        calls.append(prompt)

    agent = CrossUniverseBridgeAgent(llm_backend=backend)
    payload = {
        "coin_id": "c42",
        "source_universe": "U2",
        "source_coin": "s42",
        "proof": "proof42",
    }
    agent.register_bridge(payload)

    assert calls == ["verify proof42"]


def test_process_event_register_and_fetch():
    agent = CrossUniverseBridgeAgent()
    payload = {
        "coin_id": "c1",
        "source_universe": "U",
        "source_coin": "s1",
        "proof": "p1",
    }
    result = agent.process_event({"event": "REGISTER_BRIDGE", "payload": payload})
    assert result == {"valid": True}
    prov = agent.process_event({"event": "GET_PROVENANCE", "payload": {"coin_id": "c1"}})
    assert prov == [payload]


def test_duplicate_registration_rejected():
    agent = CrossUniverseBridgeAgent()
    payload = {
        "coin_id": "dup",
        "source_universe": "U9",
        "source_coin": "s9",
        "proof": "p9",
    }

    first = agent.register_bridge(payload)
    assert first == {"valid": True}

    second = agent.register_bridge(payload)
    assert second == {"valid": False, "duplicate": True}

    # provenance should still only contain the original record
    prov = agent.get_provenance({"coin_id": "dup"})
    assert prov == [payload]

