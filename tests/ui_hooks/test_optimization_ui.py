import pytest

from frontend_bridge import dispatch_route


class DummyHookManager:
    def __init__(self):
        self.events = []

    async def trigger(self, name, *args, **kwargs):
        self.events.append((name, args, kwargs))


@pytest.mark.asyncio
async def test_tune_parameters_via_router(monkeypatch):
    dummy = DummyHookManager()
    monkeypatch.setattr("optimization.ui_hook.ui_hook_manager", dummy, raising=False)

    called = {}

    def fake_tune(metrics):
        called["metrics"] = metrics
        return {"INFLUENCE_MULTIPLIER": 1.1}

    monkeypatch.setattr("optimization.ui_hook.tune_system_parameters", fake_tune)

    payload = {"metrics": {"accuracy": 0.5}}
    result = await dispatch_route("tune_parameters", payload)

    assert result == {"overrides": {"INFLUENCE_MULTIPLIER": 1.1}}
    assert called["metrics"] == payload["metrics"]
    assert dummy.events == [("parameters_tuned", ({"INFLUENCE_MULTIPLIER": 1.1},), {})]


@pytest.mark.asyncio
async def test_select_intervention_via_router(monkeypatch):
    dummy = DummyHookManager()
    monkeypatch.setattr("optimization.ui_hook.ui_hook_manager", dummy, raising=False)

    called = {}

    def fake_select(state):
        called["state"] = state
        return "boost_novel_content"

    monkeypatch.setattr("optimization.ui_hook.select_optimal_intervention", fake_select)

    payload = {"state": {"system_entropy": 1300.0}}
    result = await dispatch_route("select_intervention", payload)

    assert result == {"action": "boost_novel_content"}
    assert called["state"] == payload["state"]
    assert dummy.events == [("intervention_selected", ("boost_novel_content",), {})]
