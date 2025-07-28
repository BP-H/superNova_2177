import pytest

from frontend_bridge import dispatch_route, ROUTES
import protocols.api_bridge as api_bridge


class DummyAgent:
    def __init__(self) -> None:
        self.started = False
        self.ticks = 0

    def start(self) -> None:
        self.started = True

    def tick(self) -> None:
        self.ticks += 1


@pytest.mark.asyncio
async def test_api_bridge_routes(monkeypatch):
    import protocols._registry as reg
    monkeypatch.setattr(reg, "AGENT_REGISTRY", {"DummyAgent": {"class": DummyAgent}})
    api_bridge._reset()

    assert "list_agents" in ROUTES
    assert "launch_agents" in ROUTES
    assert "step_agents" in ROUTES

    listing = await dispatch_route("list_agents", {})
    assert listing == {"agents": ["DummyAgent"]}

    launch = await dispatch_route("launch_agents", {"agents": ["DummyAgent"]})
    assert launch == {"launched": ["DummyAgent"]}
    assert isinstance(api_bridge.ACTIVE_AGENTS.get("DummyAgent"), DummyAgent)
    assert api_bridge.ACTIVE_AGENTS["DummyAgent"].started is True

    stepped = await dispatch_route("step_agents", {})
    assert stepped["stepped"] == ["DummyAgent"]
    assert api_bridge.ACTIVE_AGENTS["DummyAgent"].ticks == 1
