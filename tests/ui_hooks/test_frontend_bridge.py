import importlib
import types

import pytest

import frontend_bridge


class DummyHookManager:
    def __init__(self):
        self.events = []

    async def trigger(self, name, *args, **kwargs):
        self.events.append((name, args, kwargs))

    def register_hook(self, name, func):
        self.events.append(("register", name, func))


@pytest.fixture(autouse=True)
def reload_bridge():
    """Reload ``frontend_bridge`` for isolation between tests."""
    importlib.reload(frontend_bridge)
    import network.ui_hook as nh
    importlib.reload(nh)
    yield


@pytest.mark.asyncio
async def test_register_and_dispatch_custom():
    calls = []

    async def handler(payload):
        calls.append(payload)
        return {"ok": True}

    frontend_bridge.register("custom", handler)

    result = await frontend_bridge.dispatch("custom", {"a": 1})
    assert result == {"ok": True}
    assert calls == [{"a": 1}]


@pytest.mark.asyncio
async def test_coordination_route_via_bridge(monkeypatch):
    import network.ui_hook as nh

    # Patch analysis function to avoid heavy work
    monkeypatch.setattr(
        nh,
        "analyze_coordination_patterns",
        lambda _v: {"overall_risk_score": 0.5, "graph": {}},
    )

    dummy = DummyHookManager()
    monkeypatch.setattr(nh, "ui_hook_manager", dummy, raising=False)

    payload = {
        "validations": [
            {
                "validator_id": "v1",
                "hypothesis_id": "h1",
                "score": 0.9,
                "timestamp": "2025-01-01T00:00:00Z",
            }
        ]
    }

    result = await frontend_bridge.dispatch("coordination_analysis", payload)

    assert result == {"overall_risk_score": 0.5, "graph": {}}
    assert dummy.events == [
        ("coordination_analysis_run", (result,), {})
    ]


@pytest.mark.asyncio
async def test_unknown_route_raises():
    with pytest.raises(KeyError):
        await frontend_bridge.dispatch("missing", {})

