import pytest

from frontend_bridge import dispatch_route
from validators import ui_hook

# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards


class DummyHookManager:
    def __init__(self):
        self.events = []
        self._hooks = {}

    def fire_hooks(self, name, *args, **kwargs):
        self.events.append((name, args, kwargs))

    async def trigger(self, name, *args, **kwargs):
        self.events.append((name, args, kwargs))
        for func in self._hooks.get(name, []):
            await func(*args, **kwargs)

    def register_hook(self, name, func):
        self._hooks.setdefault(name, []).append(func)


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


    assert result == {"reputations": {"v1": 0.5}, "diversity": {}}
    assert called["vals"] == payload["validations"]
    assert dummy.events == [("reputations_updated", (result,), {})]


@pytest.mark.asyncio
async def test_compute_diversity_ui_emits_event(monkeypatch):
    events = []

    async def listener(data):
        events.append(data)

    monkeypatch.setattr(ui_hook, "ui_hook_manager", DummyHookManager(), raising=False)
    ui_hook.ui_hook_manager.register_hook("diversity_score_computed", listener)

    def fake_compute(vals):
        return {"diversity_score": 0.6, "flags": []}

    monkeypatch.setattr(ui_hook, "compute_diversity_score", fake_compute)

    payload = {"validations": [{"validator_id": "v"}]}

    result = await ui_hook.compute_diversity_ui(payload)

    assert result == {"diversity_score": 0.6, "flags": []}
    assert events == [result]

