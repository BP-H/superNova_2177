# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards
import json
from protocols.core.internal_protocol import InternalAgentProtocol

class DummyAgent(InternalAgentProtocol):
    def __init__(self):
        super().__init__()
        self.receive("echo", lambda p: p)

def test_snapshot_round_trip(tmp_path):
    agent = DummyAgent()
    agent.memory["foo"] = 1
    agent.send("echo", {"x": 2})

    snap = tmp_path / "snap.json"
    agent.snapshot_memory(str(snap))

    new_agent = DummyAgent()
    new_agent.load_snapshot(snap)
    assert new_agent.memory == {"foo": 1}
    assert new_agent.inbox == [{"topic": "echo", "payload": {"x": 2}}]


def test_validate_event():
    agent = DummyAgent()
    assert not agent.validate_event("bad")
    assert not agent.validate_event({})
    assert agent.validate_event({"event": "echo"})
