# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards
import json
import pytest

from audit.ui_hook import log_hypothesis_ui, attach_trace_ui, causal_audit_ui
from frontend_bridge import dispatch_route
from causal_graph import InfluenceGraph
from db_models import LogEntry, SystemState
from hooks import events


class DummyHookManager:
    def __init__(self):
        self.events = []

    async def trigger(self, name, *args, **kwargs):
        self.events.append((name, args, kwargs))


@pytest.mark.asyncio
async def test_log_hypothesis_ui_records_state_and_emits_event(test_db, monkeypatch):
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
async def test_attach_trace_ui_updates_log_and_emits_event(test_db, monkeypatch):
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
    await attach_trace_ui(payload, test_db)

    refreshed = test_db.query(LogEntry).filter(LogEntry.id == log.id).first()
    data = json.loads(refreshed.payload)
    assert data["causal_node_ids"] == ["x"]
    assert data["causal_commentary"] == "trace"

    assert dummy.events == [
        (events.AUDIT_LOG, ({"action": "attach_trace", "log_id": log.id},), {})
    ]


@pytest.mark.asyncio
async def test_causal_audit_ui_runs_trigger_and_emits_event(test_db, monkeypatch):
    dummy = DummyHookManager()
    monkeypatch.setattr("audit.ui_hook.hook_manager", dummy, raising=False)

    captured = {}

    def fake_trigger(db, log_id, graph, hypothesis_id=None, skip_commentary=False, skip_validation=False):
        captured["args"] = (db, log_id, graph, hypothesis_id, skip_commentary, skip_validation)
        return {
            "causal_chain": ["n1"],
            "governance_review": {"score": 0.1},
            "commentary": "ok",
            "extra": True,
        }

    monkeypatch.setattr("audit.ui_hook.trigger_causal_audit", fake_trigger)

    graph = InfluenceGraph()
    payload = {"log_id": 1, "graph": graph, "hypothesis_id": "H"}
    result = await causal_audit_ui(payload, test_db)

    assert result == {
        "causal_chain": ["n1"],
        "governance_review": {"score": 0.1},
        "commentary": "ok",
    }
    assert captured["args"] == (test_db, 1, graph, "H", False, False)
    assert dummy.events == [
        (events.AUDIT_LOG, ({"action": "causal_audit", "log_id": 1},), {})
    ]


@pytest.mark.asyncio
async def test_causal_audit_ui_requires_keys(test_db):
    graph = InfluenceGraph()
    with pytest.raises(KeyError):
        await causal_audit_ui({"graph": graph}, test_db)
    with pytest.raises(KeyError):
        await causal_audit_ui({"log_id": 1}, test_db)


@pytest.mark.asyncio
async def test_causal_audit_route_dispatch(monkeypatch):
    called = {}

    async def fake_ui(payload, db=None):
        called["args"] = (payload, db)
        return {"done": True}

    monkeypatch.setattr("audit.ui_hook.causal_audit_ui", fake_ui)
    from frontend_bridge import ROUTES
    ROUTES["causal_audit"] = fake_ui

    payload = {"log_id": 2, "graph": InfluenceGraph()}
    result = await dispatch_route("causal_audit", payload, db="db")

    assert result == {"done": True}
    assert called["args"] == (payload, "db")
