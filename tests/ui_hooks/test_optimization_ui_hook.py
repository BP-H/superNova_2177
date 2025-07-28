import pytest

from frontend_bridge import dispatch_route
from optimization import ui_hook


@pytest.mark.asyncio
async def test_tune_parameters_ui(monkeypatch):
    events = []

    async def listener(data):
        events.append(data)

    ui_hook.ui_hook_manager.register_hook("system_parameters_tuned", listener)

    called = {}

    def fake_tune(metrics):
        called["metrics"] = metrics
        return {"A": 1}

    monkeypatch.setattr(ui_hook, "tune_system_parameters", fake_tune)

    payload = {"performance_metrics": {"m": 0.5}}

    result = await ui_hook.tune_parameters_ui(payload)

    assert result == {"A": 1}
    assert events == [result]
    assert called["metrics"] == payload["performance_metrics"]


@pytest.mark.asyncio
async def test_tune_parameters_via_router(monkeypatch):
    events = []

    async def listener(data):
        events.append(data)

    ui_hook.ui_hook_manager.register_hook("system_parameters_tuned", listener)

    def fake_tune(metrics):
        return {"B": 2}

    monkeypatch.setattr(ui_hook, "tune_system_parameters", fake_tune)

    payload = {"performance_metrics": {"x": 0.1}}
    result = await dispatch_route("tune_parameters", payload)

    assert result == {"B": 2}
    assert events == [result]
