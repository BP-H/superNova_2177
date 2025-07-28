import pytest

from frontend_bridge import dispatch_route
from validators import ui_hook as val_ui_hook


@pytest.mark.asyncio
async def test_reputation_update_via_router():
    events = []

    async def listener(data):
        events.append(data)

    val_ui_hook.ui_hook_manager.register_hook("reputation_update_run", listener)

    payload = {
        "validations": [
            {"validator_id": "v1", "score": 0.8, "certification": "strong"},
            {"validator_id": "v1", "score": 0.9, "certification": "strong"},
            {"validator_id": "v2", "score": 0.4, "certification": "weak"},
            {"validator_id": "v2", "score": 0.5, "certification": "weak"},
        ]
    }

    result = await dispatch_route("reputation_update", payload)

    assert "reputations" in result
    assert "diversity" in result
    assert events == [result]


@pytest.mark.asyncio
async def test_trigger_reputation_update_ui(monkeypatch):
    events = []

    async def listener(data):
        events.append(data)

    val_ui_hook.ui_hook_manager.register_hook("reputation_update_run", listener)

    called = {}

    def fake_update(vals):
        called["validations"] = vals
        return {"reputations": {"v": 0.7}, "diversity": {"d": 1}}

    monkeypatch.setattr(val_ui_hook, "update_validator_reputations", fake_update)

    payload = {"validations": [{"validator_id": "v"}]}

    result = await val_ui_hook.trigger_reputation_update_ui(payload)

    assert result == {"reputations": {"v": 0.7}, "diversity": {"d": 1}}
    assert events == [result]
    assert called["validations"] == payload["validations"]
