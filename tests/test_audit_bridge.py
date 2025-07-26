import json
import time
from decimal import Decimal
import datetime

# Import the functions to be tested
import pytest
from scientific_metrics import log_metric_change, get_metric_history
from audit_bridge import export_causal_path
from causal_graph import InfluenceGraph

# Import DB models and the test fixture
from db_models import SystemState
from conftest import test_db


def test_log_metric_change_and_get_history(test_db):
    """
    Validates the end-to-end flow of logging metric changes and retrieving
    the history for a specific metric, including timestamp and order checks.
    """
    # 1. Log several changes for two different metrics
    log_metric_change(
        db=test_db,
        metric_name="system_entropy",
        old_value=1100.0,
        new_value=1150.0,
        source_module="test_module",
    )
    # Introduce a small delay to ensure timestamps are distinct
    time.sleep(0.01)
    log_metric_change(
        db=test_db,
        metric_name="prediction_accuracy",
        old_value=0.7,
        new_value=0.75,
        source_module="test_module",
    )
    time.sleep(0.01)
    log_metric_change(
        db=test_db,
        metric_name="system_entropy",
        old_value=1150.0,
        new_value=1120.0,
        source_module="test_module",
    )

    # 2. Retrieve the history for "system_entropy"
    history = get_metric_history(test_db, "system_entropy")

    # 3. Assert that only the relevant entries are returned
    assert len(history) == 2
    # Use a more robust check for the metric name
    assert all(entry["metric_name"] == "system_entropy" for entry in history)

    # 4. Add timestamp and order checks
    assert "timestamp" in history[0]
    assert "timestamp" in history[1]
    assert history[0]["timestamp"] < history[1]["timestamp"]

    # 5. Retrieve history for a metric that was never logged
    empty_history = get_metric_history(test_db, "non_existent_metric")
    assert len(empty_history) == 0


def test_log_trimming_at_1000_entries(test_db):
    """
    Ensures that the audit log is correctly trimmed to a maximum of 1000 entries
    to prevent it from growing indefinitely.
    """
    # 1. Log more than 1000 metric changes
    for i in range(1005):
        log_metric_change(
            db=test_db,
            metric_name="stress_test",
            old_value=i,
            new_value=i + 1,
            source_module="trim_test",
        )

    # 2. Fetch the raw log from the database
    state = test_db.query(SystemState).filter(SystemState.key == "metric_audit_log").first()
    assert state is not None
    log = json.loads(state.value)

    # 3. Assert that the log has been trimmed to exactly 1000 entries
    assert len(log) == 1000
    # Check that the last entry is the one we expect
    assert log[-1]["new_value"] == 1005


def test_delta_computation_and_type_robustness(test_db):
    """
    Validates that the delta is correctly computed for various numeric types
    and handled gracefully for non-numeric or mixed types.
    """
    # Test with int and float
    log_metric_change(
        db=test_db,
        metric_name="numeric_delta_test",
        old_value=100,
        new_value=125.5,
        source_module="delta_test",
    )
    history_numeric = get_metric_history(test_db, "numeric_delta_test")
    assert history_numeric[0]["delta"] == 25.5

    # Test with Decimal type
    log_metric_change(
        db=test_db,
        metric_name="decimal_test",
        old_value=Decimal("10.5"),
        new_value=Decimal("15.5"),
        source_module="delta_test",
    )
    history_decimal = get_metric_history(test_db, "decimal_test")
    assert history_decimal[0]["delta"] == 5.0

    # Test with non-numeric values
    log_metric_change(
        db=test_db,
        metric_name="non_numeric_delta_test",
        old_value="state_A",
        new_value="state_B",
        source_module="delta_test",
    )
    history_non_numeric = get_metric_history(test_db, "non_numeric_delta_test")
    assert history_non_numeric[0]["delta"] is None


def test_metric_name_robustness(test_db):
    """
    Tests that the log retrieval works correctly with metric names that
    contain spaces and special characters.
    """
    weird_name = "metric:with spaces & symbols!"
    log_metric_change(
        db=test_db,
        metric_name=weird_name,
        old_value=1,
        new_value=2,
        source_module="robustness_test",
    )
    history = get_metric_history(test_db, weird_name)
    assert len(history) == 1
    assert history[0]["metric_name"] == weird_name


def test_export_causal_path_valid_directions():
    """Ensure export_causal_path returns expected nodes for each direction."""
    g = InfluenceGraph()
    g.add_causal_node("A")
    g.add_causal_node("B")
    g.add_causal_node("C")
    g.add_edge("A", "B")
    g.add_edge("B", "C")

    upstream = export_causal_path(g, "C", direction="ancestors", depth=3)
    downstream = export_causal_path(g, "A", direction="descendants", depth=3)

    assert set(upstream["path_nodes"]) == {"A", "B"}
    assert set(downstream["path_nodes"]) == {"B", "C"}


def test_export_causal_path_invalid_direction():
    """Invalid direction should raise ``ValueError``."""
    g = InfluenceGraph()
    g.add_causal_node("A")
    with pytest.raises(ValueError):
        export_causal_path(g, "A", direction="sideways")


def test_attach_trace_to_logentry_updates_payload(test_db):
    """attach_trace_to_logentry should persist causal node ids in payload."""
    from audit_bridge import attach_trace_to_logentry
    from db_models import LogEntry

    log = LogEntry(
        timestamp=datetime.datetime.utcnow(),
        event_type="test",
        payload=json.dumps({"foo": "bar"}),
        previous_hash="p",
        current_hash="c",
    )
    test_db.add(log)
    test_db.commit()

    attach_trace_to_logentry(log.id, ["x", "y"], test_db, summary="trace")

    refreshed = test_db.query(LogEntry).filter(LogEntry.id == log.id).first()
    data = json.loads(refreshed.payload)
    assert data["causal_node_ids"] == ["x", "y"]
    assert data["causal_commentary"] == "trace"


def test_attach_trace_to_logentry_invalid_json_does_not_modify(test_db, caplog):
    """Invalid JSON payload should leave entry unchanged and log a warning."""
    from audit_bridge import attach_trace_to_logentry
    from db_models import LogEntry
    import logging

    bad_payload = "{invalid json]"
    log = LogEntry(
        timestamp=datetime.datetime.utcnow(),
        event_type="test",
        payload=bad_payload,
        previous_hash="p",
        current_hash="c",
    )
    test_db.add(log)
    test_db.commit()

    with caplog.at_level(logging.WARNING):
        attach_trace_to_logentry(log.id, ["x"], test_db, summary="trace")
    refreshed = test_db.query(LogEntry).filter(LogEntry.id == log.id).first()
    assert refreshed.payload == bad_payload
    assert any("Failed to parse JSON payload" in rec.message for rec in caplog.records)
