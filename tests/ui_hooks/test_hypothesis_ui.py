import pytest

from frontend_bridge import dispatch_route
from hypothesis.ui_hook import ui_hook_manager


@pytest.mark.asyncio
async def test_create_hypothesis_via_router(monkeypatch):
    events = []

    async def listener(data):
        events.append(data)

    ui_hook_manager.register_hook("hypothesis_created", listener)

    captured = {}

    def fake_register(text, db, metadata=None):
        captured["args"] = (text, metadata)
        return "H1"

    class DummySession:
        def close(self):
            captured["closed"] = True

    monkeypatch.setattr("hypothesis.ui_hook.register_hypothesis", fake_register)
    monkeypatch.setattr("hypothesis.ui_hook.SessionLocal", lambda: DummySession())

    result = await dispatch_route("create_hypothesis", {"text": "foo", "metadata": {"a": 1}})

    assert result == {"hypothesis_id": "H1"}
    assert captured["args"] == ("foo", {"a": 1})
    assert captured.get("closed")
    assert events == [{"id": "H1"}]


@pytest.mark.asyncio
async def test_update_hypothesis_score_via_router(monkeypatch):
    events = []

    async def listener(data):
        events.append(data)

    ui_hook_manager.register_hook("hypothesis_score_updated", listener)

    captured = {}

    def fake_update(db, hid, score, *, status=None, source_audit_id=None, reason=None, metadata_update=None):
        captured["args"] = (hid, score, status, source_audit_id, reason, metadata_update)
        return True

    class DummySession:
        def close(self):
            captured["closed"] = True

    monkeypatch.setattr("hypothesis.ui_hook.update_hypothesis_score", fake_update)
    monkeypatch.setattr("hypothesis.ui_hook.SessionLocal", lambda: DummySession())

    payload = {"hypothesis_id": "H1", "new_score": 0.5, "status": "open", "reason": "r"}
    result = await dispatch_route("update_hypothesis_score", payload)

    assert result == {"success": True}
    assert captured["args"] == ("H1", 0.5, "open", None, "r", None)
    assert captured.get("closed")
    assert events == [{"id": "H1", "success": True}]
