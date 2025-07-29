# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards
import json
import datetime
from causal_trigger import trigger_causal_audit
from db_models import LogEntry, SystemState
from causal_graph import InfluenceGraph


def test_trigger_causal_audit_uses_audit_ref(test_db):
    ref = "test_audit_ref"
    snapshot = {
        "trace": {
            "trace_detail": {
                "path_nodes_data": [
                    {"id": "n1"}
                ],
                "edge_list_data": []
            }
        }
    }
    test_db.add(SystemState(key=ref, value=json.dumps(snapshot)))
    test_db.commit()

    payload = json.dumps({"causal_audit_ref": ref})
    log = LogEntry(
        timestamp=datetime.datetime.utcnow(),
        event_type="test",
        payload=payload,
        previous_hash="p",
        current_hash="c",
    )
    test_db.add(log)
    test_db.commit()

    graph = InfluenceGraph()
    result = trigger_causal_audit(test_db, log.id, graph)
    chain = result.get("causal_chain")
    assert isinstance(chain, list)
    assert chain and chain[0].get("type") == "node_event"

