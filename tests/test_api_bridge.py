import pytest

from frontend_bridge import dispatch_route
import protocols.api_bridge as api_bridge


class DummyAgent:
    def __init__(self):
        self.started = False
        self.ticks = 0

    def start(self):
        self.started = True

    def tick(self):
        self.ticks += 1


@pytest.mark.asyncio
async def test_agent_lifecycle(monkeypatch):
    registry = {"DummyAgent": {"class": DummyAgent}}
    monkeypatch.setattr(api_bridge, "_registry", lambda: registry, raising=False)
    api_bridge.active_agents.clear()

    agents = await dispatch_route("list_agents", {})
    assert agents == {"agents": ["DummyAgent"]}

    launch_result = await dispatch_route(
        "launch_agents",
        {"agents": ["DummyAgent"], "provider": "p", "api_key": "k"},
    )
    assert launch_result["launched"] == ["DummyAgent"]
    assert "DummyAgent" in api_bridge.active_agents
    assert api_bridge.active_agents["DummyAgent"].started

    step_result = await dispatch_route("step_agents", {})
    assert step_result["stepped"] == ["DummyAgent"]
    assert api_bridge.active_agents["DummyAgent"].ticks == 1


@pytest.mark.asyncio
async def test_launch_unknown_agent(monkeypatch):
    monkeypatch.setattr(api_bridge, "_registry", lambda: {}, raising=False)
    api_bridge.active_agents.clear()

    with pytest.raises(ValueError):
        await dispatch_route(
            "launch_agents",
            {"agents": ["Missing"], "provider": "p", "api_key": "k"},
        )
