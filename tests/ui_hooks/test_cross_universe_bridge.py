# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards
import pytest

from frontend_bridge import dispatch_route
from protocols.agents.cross_universe_bridge_agent import CrossUniverseBridgeAgent

import protocols.ui_hook as ui_hook
from hooks import events


class DummyHookManager:
    def __init__(self):
        self.events = []

    async def trigger(self, name, *args, **kwargs):
        self.events.append((name, args, kwargs))


@pytest.mark.asyncio
async def test_cross_universe_routes(monkeypatch):
    dummy = DummyHookManager()
    agent = CrossUniverseBridgeAgent()
    monkeypatch.setattr(ui_hook, "bridge_hook_manager", dummy, raising=False)
    monkeypatch.setattr(ui_hook, "bridge_agent", agent, raising=False)

    payload = {
        "coin_id": "c123",
        "source_universe": "U1",
        "source_coin": "s456",
        "proof": "p789",
    }
    result = await dispatch_route("cross_universe_register_bridge", payload)
    assert result == {"valid": True}
    assert agent.get_provenance({"coin_id": "c123"}) == [payload]
    assert dummy.events == [(events.BRIDGE_REGISTERED, ({"valid": True},), {})]

    result2 = await dispatch_route("cross_universe_get_provenance", {"coin_id": "c123"})
    assert result2 == [payload]
    assert dummy.events[-1] == (events.PROVENANCE_RETURNED, ([payload],), {})
