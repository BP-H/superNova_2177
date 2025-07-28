import pytest

from frontend_bridge import dispatch_route
from validators import ui_hook

# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards


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

    result = await dispatch_route("update_validator_reputations", payload, db=object())

    assert result == {"reputations": {"v1": 0.5}, "diversity": {}}  # nosec B101
    assert called["vals"] == payload["validations"]  # nosec B101
    assert dummy.events == [("validator_reputations", (result,), {})]  # nosec B101
