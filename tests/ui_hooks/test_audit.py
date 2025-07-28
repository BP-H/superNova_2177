import json

import pytest

# Import the bridge module so routes are registered
import audit.ui_bridge  # noqa: F401
from db_models import LogEntry, SystemState
from frontend_bridge import dispatch_route


class DummyHookManager:
    def __init__(self):
        self.events = []

    async def trigger(self, name, *args, **kwargs):
        self.events.append((name, args, kwargs))


@pytest.mark.asyncio
async def test_log_hypothesis_via_router(test_db, monkeypatch):
    dummy = DummyHookManager()
    monkeypatch.setattr("audit.ui_hook.hook_manager", dummy, raising=False)

    payload = {"hypothesis_text": "foo", "causal_node_ids": ["a", "b"]}
    key = await dispatch_route("log_hypothesis", payload)

    state = test_db.query(SystemState).filter(SystemState.key == key).first()
    assert state is not None  # nosec B101

    assert dummy.events == [  # nosec B101
        ("audit_log", ({"action": "log_hypothesis", "key": key},), {})
    ]


@pytest.mark.asyncio
async def test_attach_trace_via_router(test_db, monkeypatch):
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

    payload = {
        "log_id": log.id,
        "causal_node_ids": ["x"],
        "summary": "trace",
    }
    await dispatch_route("attach_trace", payload)

    refreshed = test_db.query(LogEntry).filter(LogEntry.id == log.id).first()
    data = json.loads(refreshed.payload)
    assert data["causal_node_ids"] == ["x"]  # nosec B101
    assert data["causal_commentary"] == "trace"  # nosec B101

    assert dummy.events == [  # nosec B101
        ("audit_log", ({"action": "attach_trace", "log_id": log.id},), {})
    ]
