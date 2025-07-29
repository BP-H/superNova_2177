# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards
import json
import pytest
from protocols.utils.messaging import MessageHub
from frontend_bridge import dispatch_route
import audit.ui_hook as ui_hook
from audit_bridge import export_causal_path
from causal_graph import InfluenceGraph
from db_models import LogEntry, SystemState
from hooks import events


class DummyHookManager:
    def __init__(self):
        self.events = []

    async def trigger(self, name, *args, **kwargs):
        self.events.append((name, args, kwargs))


@pytest.mark.asyncio
async def test_log_hypothesis_route_dispatch(test_db, monkeypatch):
    hub = MessageHub()
    dummy = DummyHookManager()
    monkeypatch.setattr(ui_hook, "message_hub", hub, raising=False)
    monkeypatch.setattr(ui_hook, "hook_manager", dummy, raising=False)

    payload = {"hypothesis_text": "foo", "causal_node_ids": ["a"]}
    key = await dispatch_route("log_hypothesis", payload, db=test_db)

    assert test_db.query(SystemState).filter(SystemState.key == key).first() is not None
    msgs = hub.get_messages("audit_log")
    assert len(msgs) == 1
    assert msgs[0].data == {"action": "log_hypothesis", "key": key}
    assert dummy.events == [(events.AUDIT_LOG, ({"action": "log_hypothesis", "key": key},), {})]


@pytest.mark.asyncio
async def test_attach_trace_route_dispatch(test_db, monkeypatch):
    hub = MessageHub()
    dummy = DummyHookManager()
    monkeypatch.setattr(ui_hook, "message_hub", hub, raising=False)
    monkeypatch.setattr(ui_hook, "hook_manager", dummy, raising=False)

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
    await dispatch_route("attach_trace", payload, db=test_db)

    refreshed = test_db.query(LogEntry).filter(LogEntry.id == log.id).first()
    data = json.loads(refreshed.payload)
    assert data["causal_node_ids"] == ["x"]
    assert data["causal_commentary"] == "trace"

    msgs = hub.get_messages("audit_log")
    assert len(msgs) == 1
    assert msgs[0].data == {"action": "attach_trace", "log_id": log.id}
    assert dummy.events == [(events.AUDIT_LOG, ({"action": "attach_trace", "log_id": log.id},), {})]


@pytest.mark.asyncio
async def test_export_causal_path_route_dispatch(monkeypatch):
    g = InfluenceGraph()
    g.add_causal_node("A")
    g.add_causal_node("B")
    g.add_edge("A", "B")

    hub = MessageHub()
    monkeypatch.setattr(ui_hook, "message_hub", hub, raising=False)

    payload = {"graph": g, "node_id": "B", "direction": "ancestors", "depth": 3}
    result = await dispatch_route("export_causal_path", payload)

    expected = export_causal_path(g, "B", direction="ancestors", depth=3)
    assert result == expected

    msgs = hub.get_messages("audit_log")
    assert len(msgs) == 1
    assert msgs[0].data == {"action": "export_causal_path", "node_id": "B", "direction": "ancestors"}
