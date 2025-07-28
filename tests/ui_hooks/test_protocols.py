import pytest

from frontend_bridge import dispatch_route
from protocols.ui import api_bridge
from protocols.ui import interface_server


class DummyAgent:
    def __init__(self):
        self.ticks = 0

    def tick(self):
        self.ticks += 1


@pytest.mark.asyncio
async def test_list_agents_via_router(monkeypatch):
    monkeypatch.setattr(interface_server, "available_agents", {"DummyAgent": DummyAgent}, raising=False)
    result = await dispatch_route("protocol_agents_list", {})
    assert result == ["DummyAgent"]


@pytest.mark.asyncio
async def test_launch_and_step_agents_via_router(monkeypatch):
    monkeypatch.setattr(interface_server, "available_agents", {"DummyAgent": DummyAgent}, raising=False)
    monkeypatch.setattr(interface_server, "active_agents", {}, raising=False)

    payload = {"provider": "test", "api_key": "k", "agents": ["DummyAgent"]}
    launch = await dispatch_route("protocol_agents_launch", payload)
    assert launch == {"launched": ["DummyAgent"], "provider": "test"}

    step = await dispatch_route("protocol_agents_step", {})
    assert step == {"stepped": ["DummyAgent"], "active_agents": ["DummyAgent"]}
    assert interface_server.active_agents["DummyAgent"].ticks == 1
