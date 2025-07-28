import pytest

from validators.ui_hook import trigger_reputation_update_ui


class DummyHookManager:
    def __init__(self):
        self.events = []

    async def trigger(self, name, *args, **kwargs):
        self.events.append((name, args, kwargs))


@pytest.mark.asyncio
async def test_trigger_reputation_update_ui(monkeypatch):
    dummy = DummyHookManager()
    monkeypatch.setattr("validators.ui_hook.ui_hook_manager", dummy, raising=False)

    called = {}

    def fake_update(vals):
        called["validations"] = vals
        return {"reputations": {"v": 0.8}, "diversity": {"validator_count": 1}}

    monkeypatch.setattr("validators.ui_hook.update_validator_reputations", fake_update)

    payload = {"validations": [{"validator_id": "v", "score": 1.0}]}
    result = await trigger_reputation_update_ui(payload)

    assert result == {"reputations": {"v": 0.8}, "diversity": {"validator_count": 1}}
    assert called["validations"] == payload["validations"]
    assert dummy.events == [("reputation_update_run", (result,), {})]

