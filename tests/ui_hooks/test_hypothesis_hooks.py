# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards
import pytest

import hypothesis.ui_hook as ui_hook


class DummyHookManager:
    def __init__(self):
        self.events = []

    async def trigger(self, name, *args, **kwargs):
        self.events.append((name, args, kwargs))


@pytest.mark.asyncio
async def test_register_hypothesis_ui(monkeypatch):
    hooks = DummyHookManager()
    monkeypatch.setattr(ui_hook, "ui_hook_manager", hooks, raising=False)

    called = {}

    def fake_register(text, db, metadata=None):
        called["text"] = text
        called["metadata"] = metadata
        called["db"] = db
        return "HYP_TEST"

    monkeypatch.setattr(ui_hook, "ht", type("obj", (), {"register_hypothesis": fake_register}))

    result = await ui_hook.register_hypothesis_ui({"text": "foo"}, object())

    assert result == {"hypothesis_id": "HYP_TEST"}
    assert called["text"] == "foo"
    assert hooks.events == [("hypothesis_registered", ({"hypothesis_id": "HYP_TEST"},), {})]


@pytest.mark.asyncio
async def test_update_hypothesis_score_ui(monkeypatch):
    hooks = DummyHookManager()
    monkeypatch.setattr(ui_hook, "ui_hook_manager", hooks, raising=False)

    called = {}

    def fake_update(db, hypothesis_id, new_score, **kwargs):
        called.update({"id": hypothesis_id, "score": new_score, "kwargs": kwargs, "db": db})
        return True

    monkeypatch.setattr(ui_hook, "ht", type("obj", (), {"update_hypothesis_score": fake_update}))

    payload = {"hypothesis_id": "HYP_TEST", "new_score": 0.7}
    result = await ui_hook.update_hypothesis_score_ui(payload, object())

    assert result == {"success": True}
    assert called["id"] == "HYP_TEST"
    assert called["score"] == 0.7
    assert hooks.events == [("hypothesis_score_updated", ({"hypothesis_id": "HYP_TEST", "success": True},), {})]
