import datetime
import pytest
import json

from causal_graph import (
    InfluenceGraph,
    discover_causal_mechanisms,
    temporal_causality_analysis,
)

def test_discover_causal_mechanisms():
    """
    Validates that discover_causal_mechanisms correctly identifies a causal link
    following a logged intervention.
    """
    # 1. Setup
    g = InfluenceGraph()
    base_time = datetime.datetime.utcnow()

    # Log an intervention with a known change in a metric (delta).
    intervention_log = [
        {
            "timestamp": base_time,
            "target_entity": 1,
            "metric_delta": 10.0,
        }
    ]

    # Add an edge to the graph that occurs *after* the intervention.
    g.add_interaction(
        source=1,
        target=2,
        timestamp=base_time + datetime.timedelta(seconds=10),
        weight=0.8
    )

    # 2. Execution
    mechanisms = discover_causal_mechanisms(g, intervention_log)

    # 3. Assertion
    assert len(mechanisms) == 1
    mechanism = mechanisms[0]

    # The strength score should combine the metric delta with the time-weighted
    # strength of the edge that occurred after the intervention.
    # The time_weighted_weight function uses a decay_rate of 0.001.
    time_decayed_edge_strength = g.time_weighted_weight(1, 2, decay_rate=0.001)["value"]
    expected_strength = 10.0 + time_decayed_edge_strength

    assert mechanism["strength_score"] == pytest.approx(expected_strength)
    assert mechanism["cause_description"] == "Intervention on 1"

def test_temporal_causality_analysis():
    """
    Validates that temporal_causality_analysis can identify the longest
    time-ordered chain of events in the graph.
    """
    # 1. Setup
    g = InfluenceGraph()
    base_time = datetime.datetime.utcnow()

    # Create a clear, time-ordered sequence of events: A -> B -> C
    g.add_interaction('A', 'B', timestamp=base_time + datetime.timedelta(seconds=10), weight=0.7)
    g.add_interaction('B', 'C', timestamp=base_time + datetime.timedelta(seconds=20), weight=0.9)

    # Add another edge with a higher weight that is not part of the longest chain.
    g.add_interaction('X', 'Y', timestamp=base_time + datetime.timedelta(seconds=15), weight=0.95)

    # 2. Execution
    result = temporal_causality_analysis(g, time_periods=["last_hour"])
    analysis = result['analyses'][0]

    # 3. Assertion
    # Verify the longest sequential path is correctly identified.
    assert analysis['longest_causal_chain'] == ['A', 'B', 'C']

    # Verify the most impactful link is the one with the highest time-decayed weight.
    # Given the small time differences, this will be the edge with the highest initial weight.
    assert analysis['most_impactful_temporal_link']['edge'] == ('X', 'Y')
    assert analysis['most_impactful_temporal_link']['score'] == pytest.approx(
        g.time_weighted_weight('X', 'Y', decay_rate=0.001)["value"]
    )


def test_causal_graph_node_structure_and_metadata():
    g = InfluenceGraph()
    g.add_causal_node(
        "n1",
        source_module="tester",
        trigger_event="ADD",
        entity_type="Coin",
        entity_id="c1",
        system_entropy_at_creation=0.5,
        node_specific_entropy=0.1,
        debug_payload={"x": 1},
        inference_commentary="test node",
    )
    data = g.graph.nodes["n1"]
    assert data["source_module"] == "tester"
    assert data["trigger_event"] == "ADD"
    assert data["entity_type"] == "Coin"
    assert data["entity_id"] == "c1"
    assert data["system_entropy_at_creation"] == 0.5
    assert data["node_specific_entropy"] == 0.1
    assert data["debug_payload"]["x"] == 1
    assert data["inference_commentary"] == "test node"


def test_trace_to_ancestors_returns_correct_lineage():
    g = InfluenceGraph()
    g.add_causal_node("A")
    g.add_causal_node("B")
    g.add_causal_node("C")
    g.add_edge("A", "B")
    g.add_edge("B", "C")
    lineage = g.trace_to_ancestors("C")
    ids = [entry["node_id"] for entry in lineage]
    assert set(ids) == {"A", "B"}


def test_trace_to_descendants_returns_correct_lineage():
    g = InfluenceGraph()
    g.add_causal_node("A")
    g.add_causal_node("B")
    g.add_causal_node("C")
    g.add_edge("A", "B")
    g.add_edge("B", "C")
    lineage = g.trace_to_descendants("A")
    ids = [entry["node_id"] for entry in lineage]
    assert set(ids) == {"B", "C"}


def test_causal_graph_handles_empty_graph_and_queries():
    g = InfluenceGraph()
    assert g.trace_to_ancestors("X") == []
    assert g.trace_to_descendants("X") == []


def test_graph_snapshot_creates_valid_record(test_db):
    g = InfluenceGraph()
    g.add_causal_node("A")
    g.add_causal_node("B")
    g.add_edge("A", "B")
    key = g.snapshot_graph(test_db, key_prefix="snap_test")
    from db_models import SystemState

    row = test_db.query(SystemState).filter(SystemState.key == key).first()
    assert row is not None
    data = json.loads(row.value)
    assert any(n["id"] == "A" for n in data["nodes"])
    assert any(e["source"] == "A" and e["target"] == "B" for e in data["edges"])


def test_graph_snapshot_reconstructs_full_state(test_db):
    g = InfluenceGraph()
    g.add_causal_node("A")
    g.add_causal_node("B")
    g.add_edge("A", "B")
    key = g.snapshot_graph(test_db, key_prefix="snap_test")
    from db_models import SystemState

    row = test_db.query(SystemState).filter(SystemState.key == key).first()
    data = json.loads(row.value)
    g2 = InfluenceGraph()
    for n in data["nodes"]:
        g2.add_causal_node(n["id"])
    for e in data["edges"]:
        g2.add_edge(e["source"], e["target"])
    assert set(g2.graph.nodes()) == {"A", "B"}
    assert g2.graph.has_edge("A", "B")
