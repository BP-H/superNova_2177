import pytest
from unittest.mock import MagicMock

from introspection.ui_hook import trigger_full_audit_ui


class DummyHookManager:
    def __init__(self):
        self.events = []

    async def trigger(self, name, *args, **kwargs):
        self.events.append((name, args, kwargs))


@pytest.mark.asyncio
async def test_full_audit_ui_runs_pipeline_and_emits_event(monkeypatch):
    dummy = DummyHookManager()
    monkeypatch.setattr("introspection.ui_hook.ui_hook_manager", dummy, raising=False)

    calls = {}

    def fake_run(hid, db):
        calls["run"] = (hid, db)
        return {"bundle": True}

    monkeypatch.setattr("introspection.ui_hook.run_full_audit", fake_run)

    db = MagicMock()
    payload = {"hypothesis_id": "H1"}
    result = await trigger_full_audit_ui(payload, db)

    assert result == {"bundle": True}
    assert calls["run"] == ("H1", db)
    assert dummy.events == [("full_audit_completed", ({"bundle": True},), {})]


@pytest.mark.asyncio
async def test_full_audit_ui_requires_id(monkeypatch):
    db = MagicMock()
    with pytest.raises(KeyError):
        await trigger_full_audit_ui({}, db)
