# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards
import pytest
from unittest.mock import MagicMock

from frontend_bridge import dispatch_route
import introspection.ui_hook as iuh
from hooks import events


class DummyHookManager:
    def __init__(self):
        self.events = []

    async def trigger(self, name, *args, **kwargs):
        self.events.append((name, args, kwargs))


@pytest.mark.asyncio
async def test_trigger_full_audit_route(monkeypatch):
    dummy = DummyHookManager()
    monkeypatch.setattr(iuh, "ui_hook_manager", dummy, raising=False)

    calls = {}

    def fake_run(hid, db):
        calls["run"] = (hid, db)
        return {"bundle": True}

    monkeypatch.setattr(iuh, "run_full_audit", fake_run)

    db = MagicMock()
    payload = {"hypothesis_id": "H1"}
    result = await dispatch_route("trigger_full_audit", payload, db=db)

    assert result == {"bundle": True}
    assert calls["run"] == ("H1", db)
    assert dummy.events == [(events.FULL_AUDIT_COMPLETED, ({"bundle": True},), {})]
