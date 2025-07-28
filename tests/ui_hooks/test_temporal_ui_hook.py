import pytest

from frontend_bridge import dispatch_route
from temporal import ui_hook as temp_ui_hook


@pytest.mark.asyncio
async def test_analyze_temporal_ui_emits_event(monkeypatch):
    events = []

    async def listener(data):
        events.append(data)

    temp_ui_hook.ui_hook_manager.register_hook("temporal_analysis_run", listener)

    called = {}

    def fake_analyze(validations, reputations=None):
        called["validations"] = validations
        called["reputations"] = reputations
        return {"flags": ["ok"], "avg_delay_hours": 1.0}

    monkeypatch.setattr(temp_ui_hook, "analyze_temporal_consistency", fake_analyze)

    payload = {
        "validations": [{"validator_id": "v", "timestamp": "2025-01-01T00:00:00Z"}],
        "reputations": {"v": 0.8},
    }
    result = await temp_ui_hook.analyze_temporal_ui(payload)

    assert result == {"flags": ["ok"], "avg_delay_hours": 1.0}
    assert events == [result]
    assert called["validations"] == payload["validations"]
    assert called["reputations"] == payload["reputations"]


@pytest.mark.asyncio
async def test_temporal_consistency_route(monkeypatch):
    def fake_analyze(validations, reputations=None):
        return {"flags": []}

    monkeypatch.setattr(temp_ui_hook, "analyze_temporal_consistency", fake_analyze)

    result = await dispatch_route("temporal_consistency", {"validations": []})

    assert result == {"flags": []}

