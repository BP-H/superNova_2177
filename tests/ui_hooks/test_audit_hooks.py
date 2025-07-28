import json
import pytest

from audit.ui_hook import log_hypothesis_ui, attach_trace_ui
from db_models import LogEntry, SystemState
from hooks import events


class DummyHookManager:
    def __init__(self):
        self.events = []

    async def trigger(self, name, *args, **kwargs):
        self.events.append((name, args, kwargs))


@pytest.mark.asyncio
async def test_log_hypothesis_ui(test_db, monkeypatch):
    dummy = DummyHookManager()
    monkeypatch.setattr("audit.ui_hook.hook_manager", dummy, raising=False)

    payload = {"hypothesis_text": "foo", "causal_node_ids": ["a", "b"]}
    key = await log_hypothesis_ui(payload, test_db)

    state = test_db.query(SystemState).filter(SystemState.key == key).first()
    assert state is not None
    assert dummy.events == [
        (events.AUDIT_LOG, ({"action": "log_hypothesis", "key": key},), {})
    ]


@pytest.mark.asyncio
async def test_attach_trace_ui(test_db, monkeypatch):
    dummy = DummyHookManager()
    monkeypatch.setattr("audit.ui_hook.hook_manager", dummy, raising=False)

    log = LogEntry(
        timestamp=__import__("datetime").datetime.utcnow(),
        event_type="test",
        payload=json.dumps({"foo": "bar"}),
        previous_hash="p",
        current_hash="c",
    )
    test_db.add(log)
    test_db.commit()

    payload = {"log_id": log.id, "causal_node_ids": ["x"], "summary": "trace"}
    await attach_trace_ui(payload, test_db)

    refreshed = test_db.query(LogEntry).filter(LogEntry.id == log.id).first()
    data = json.loads(refreshed.payload)
    assert data["causal_node_ids"] == ["x"]
    assert data["causal_commentary"] == "trace"
    assert dummy.events == [
        (events.AUDIT_LOG, ({"action": "attach_trace", "log_id": log.id},), {})
    ]
