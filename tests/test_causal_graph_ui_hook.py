import pytest

from frontend_bridge import dispatch_route
from causal_graph import ui_hook
from causal_graph import InfluenceGraph


class DummyHookManager:
    def __init__(self):
        self.events = []

    async def trigger(self, name, *args, **kwargs):
        self.events.append((name, args, kwargs))


@pytest.mark.asyncio
async def test_build_graph_ui(monkeypatch):
    dummy = DummyHookManager()
    monkeypatch.setattr(ui_hook, "ui_hook_manager", dummy, raising=False)

    g = InfluenceGraph()
    g.add_edge("A", "B")

    def fake_build(db):
        assert db == "db"
        return g

    monkeypatch.setattr(ui_hook, "build_causal_graph", fake_build)

    result = await dispatch_route("build_causal_graph", {}, db="db")

    assert any(n["id"] == "A" for n in result["nodes"])
    assert any(e["source"] == "A" and e["target"] == "B" for e in result["edges"])
    assert dummy.events == [("graph_built", (result,), {})]


@pytest.mark.asyncio
async def test_simulate_entanglement_ui(monkeypatch):
    dummy = DummyHookManager()
    monkeypatch.setattr(ui_hook, "ui_hook_manager", dummy, raising=False)

    called = {}

    def fake_sim(db, u1, u2):
        called["args"] = (db, u1, u2)
        return {"source": u1, "target": u2, "probabilistic_influence": 0.5}

    monkeypatch.setattr(ui_hook, "simulate_social_entanglement", fake_sim)

    payload = {"user1_id": 1, "user2_id": 2}
    result = await dispatch_route("simulate_entanglement", payload, db="db")

    assert result == {"source": 1, "target": 2, "probabilistic_influence": 0.5}
    assert called["args"] == ("db", 1, 2)
    assert dummy.events == [("entanglement_simulated", (result,), {})]
