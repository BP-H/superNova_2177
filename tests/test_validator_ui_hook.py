import pytest

from validators import ui_hook
from hooks import events


class DummyHookManager:
    def __init__(self):
        self.events = []

    def fire_hooks(self, name, *args, **kwargs):
        self.events.append((name, args, kwargs))


@pytest.mark.asyncio
async def test_update_reputations_ui_emits_event(monkeypatch):
    dummy = DummyHookManager()
    monkeypatch.setattr(ui_hook, "hook_manager", dummy, raising=False)

    called = {}

    def fake_update(vals, db=None):
        called["vals"] = vals
        return {"reputations": {"v1": 0.5}, "diversity": {}}

    monkeypatch.setattr(ui_hook, "update_validator_reputations", fake_update)

    payload = {"validations": [{"validator_id": "v1", "score": 0.7}]}

    result = await ui_hook.update_reputations_ui(payload, object())

    assert result == {"reputations": {"v1": 0.5}, "diversity": {}}
    assert called["vals"] == payload["validations"]
    assert dummy.events == [(events.VALIDATOR_REPUTATIONS, (result,), {})]
