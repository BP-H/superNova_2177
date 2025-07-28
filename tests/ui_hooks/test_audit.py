import pytest

from protocols.utils.messaging import MessageHub
from audit.ui_hook import (
    log_hypothesis_ui,
    export_causal_path_ui,
)
from audit_bridge import export_causal_path
from causal_graph import InfluenceGraph
from db_models import SystemState


@pytest.mark.asyncio
async def test_log_hypothesis_ui_publishes_and_records(test_db, monkeypatch):
    hub = MessageHub()
    monkeypatch.setattr("audit.ui_hook.message_hub", hub, raising=False)

    payload = {"hypothesis_text": "foo", "causal_node_ids": ["a"]}
    key = await log_hypothesis_ui(payload, test_db)

    assert test_db.query(SystemState).filter(SystemState.key == key).first() is not None

    msgs = hub.get_messages("audit_log")
    assert len(msgs) == 1
    assert msgs[0].data == {"action": "log_hypothesis", "key": key}


@pytest.mark.asyncio
async def test_export_causal_path_ui_uses_bridge_and_publishes(monkeypatch):
    g = InfluenceGraph()
    g.add_causal_node("A")
    g.add_causal_node("B")
    g.add_edge("A", "B")

    hub = MessageHub()
    monkeypatch.setattr("audit.ui_hook.message_hub", hub, raising=False)

    payload = {"graph": g, "node_id": "B", "direction": "ancestors", "depth": 3}
    result = await export_causal_path_ui(payload)

    expected = export_causal_path(g, "B", direction="ancestors", depth=3)
    assert result == expected

    msgs = hub.get_messages("audit_log")
    assert len(msgs) == 1
    assert msgs[0].data == {
        "action": "export_causal_path",
        "node_id": "B",
        "direction": "ancestors",
    }


