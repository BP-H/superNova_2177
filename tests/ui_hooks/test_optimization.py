import pytest

from frontend_bridge import dispatch_route
import optimization.ui_hook as opt_ui_hook


class DummyHookManager:
    def __init__(self):
        self.events = []

    async def trigger(self, name, *args, **kwargs):
        self.events.append((name, args, kwargs))


@pytest.mark.asyncio
async def test_tune_parameters_via_router(monkeypatch):
    dummy = DummyHookManager()
    monkeypatch.setattr(opt_ui_hook, "ui_hook_manager", dummy, raising=False)

    def fake_tune(metrics):
        assert metrics == {"accuracy": 0.8}
        return {"INFLUENCE_MULTIPLIER": 1.1}

    monkeypatch.setattr(opt_ui_hook, "tune_system_parameters", fake_tune)

    payload = {"metrics": {"accuracy": 0.8}}
    result = await dispatch_route("tune_parameters", payload)

    assert result == {"INFLUENCE_MULTIPLIER": 1.1}
    assert dummy.events == [("system_parameters_tuned", (result,), {})]


@pytest.mark.asyncio
async def test_tune_parameters_direct(monkeypatch):
    events = []

    async def listener(data):
        events.append(data)

    opt_ui_hook.ui_hook_manager.register_hook("system_parameters_tuned", listener)

    def fake_tune(metrics):
        return {"ENTROPY_REDUCTION_STEP": 0.3}

    monkeypatch.setattr(opt_ui_hook, "tune_system_parameters", fake_tune)

    result = await opt_ui_hook.tune_parameters_ui({"current_system_entropy": 1200})

    assert result == {"ENTROPY_REDUCTION_STEP": 0.3}
    assert events == [result]
