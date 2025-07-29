# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards
import base64

import pytest

import protocols.agents.harmony_ui_hook as harmony_hook
from frontend_bridge import dispatch_route
from hooks import events


class DummyHookManager:
    def __init__(self):
        self.events = []

    async def trigger(self, name, *args, **kwargs):
        self.events.append((name, args, kwargs))


class DummyAgent:
    def __init__(self, midi: bytes):
        self.midi = midi
        self.calls: list[dict[str, object] | None] = []

    def handle_generate(self, payload=None):
        self.calls.append(payload)
        return self.midi


@pytest.mark.asyncio
async def test_generate_midi_route(monkeypatch):
    midi = b"demo"
    agent = DummyAgent(midi)
    hooks = DummyHookManager()
    monkeypatch.setattr(harmony_hook, "synth_agent", agent, raising=False)
    monkeypatch.setattr(harmony_hook, "ui_hook_manager", hooks, raising=False)

    payload = {"metrics": {"a": 1}}
    result = await dispatch_route("generate_midi", payload)

    assert result == {"midi_base64": base64.b64encode(midi).decode()}  # nosec B101
    assert agent.calls == [payload]  # nosec B101
    assert hooks.events == [(events.MIDI_GENERATED, (midi,), {})]  # nosec B101
