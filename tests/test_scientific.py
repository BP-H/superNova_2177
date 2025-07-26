import types
import sys
import logging
import math
import datetime
from decimal import Decimal
import pytest
from unittest.mock import MagicMock

# Import functions to be tested
from scientific_metrics import (
    calculate_influence_score,
    calculate_interaction_entropy,
    query_influence,
    build_causal_graph,
    generate_scientific_report,
    predict_user_interactions,
    validate_user_prediction,
    generate_system_predictions,
    design_validation_experiments,
    analyze_prediction_accuracy,
    detect_feedback_loops,
    estimate_lag_effects,
    measure_autonomous_reasoning,
    assess_meta_cognitive_awareness,
)
from quantum_sim import QuantumContext, approximate_trace_distance, pseudo_fidelity_score
from causal_graph import InfluenceGraph
from scientific_utils import (
    estimate_uncertainty,
    generate_hypotheses,
)

# Import the main module to be monkeypatched
import scientific_metrics as metrics

# Attempt to import networkx, but don't fail if it's not there
try:
    import networkx as nx
except ImportError:
    nx = None


# This test is now CORRECTED.
# It uses robust monkeypatching to isolate the function under test.
def test_generate_system_predictions_basic(monkeypatch):
    """Validate generate_system_predictions basic output structure."""
    if not nx:
        pytest.skip("networkx not installed")

    # 1. Setup Mock Data and Environment
    # Mock database object with a list of mock users
    mock_users = [types.SimpleNamespace(id=1), types.SimpleNamespace(id=2)]
    mock_db = MagicMock()
    mock_db.query.return_value.all.return_value = mock_users

    # Dictionary to track calls to mocked functions
    calls = {"build": [], "influence": [], "entropy": []}
    
    # Mock graph object that the build function will return
    mock_graph = types.SimpleNamespace(graph=nx.DiGraph())

    # 2. Define Mock Functions (Fakes)
    def fake_build_causal_graph(db_arg):
        calls["build"].append(db_arg)
        return mock_graph

    def fake_calculate_influence_score(graph_arg, uid, iterations=10):
        calls["influence"].append((graph_arg, uid))
        return {"value": 0.4}  # Return a consistent dummy value

    def fake_calculate_interaction_entropy(user_obj, db_arg, method="shannon", decay_rate=0.0):
        calls["entropy"].append((user_obj, db_arg))
        return {"value": 0.5}  # Return a consistent dummy value

    # 3. Apply Monkeypatches
    monkeypatch.setattr(metrics, "build_causal_graph", fake_build_causal_graph)
    monkeypatch.setattr(metrics, "calculate_influence_score", fake_calculate_influence_score)
    monkeypatch.setattr(metrics, "calculate_interaction_entropy", fake_calculate_interaction_entropy)

    # 4. Execute the Function to Test
    result = generate_system_predictions(mock_db, timeframe_hours=24)

    # 5. Assert the Results and Mock Calls
    # Assert the structure and values of the output
    assert "timeframe_hours" in result
    assert result["predicted_system_entropy"]["value"] == pytest.approx(0.5)
    assert result["predicted_content_diversity"]["value"] == pytest.approx(1.0 - 0.5)
    assert result["top_influencers_next_day"] == [1, 2] # Sorted by influence (all are 0.4, so order is stable)

    # Assert that our mocked dependencies were called correctly
    assert len(calls["build"]) == 1
    assert calls["build"][0] == mock_db
    assert len(calls["influence"]) == 2
    assert calls["influence"][0] == (mock_graph.graph, 1)
    assert calls["influence"][1] == (mock_graph.graph, 2)
    assert len(calls["entropy"]) == 2
    assert calls["entropy"][0] == (mock_users[0], mock_db)
    assert calls["entropy"][1] == (mock_users[1], mock_db)


# This test is now CORRECTED.
# The `entangled_pairs` setup now correctly reflects the bidirectional nature
# of the production code, and it only asserts against the raw float output.
def test_quantum_prediction_engine_basic(monkeypatch):
    """Validate quantum_prediction_engine interaction predictions."""
    monkeypatch.setattr(
        "quantum_sim.ENTANGLEMENT_NORMALIZATION_FACTOR", 1.0, raising=False
    )

    qc = QuantumContext()
    # CORRECTED: Setup now includes bidirectional pairs, mirroring the
    # behavior of the `entangle_entities` production function.
    qc.entangled_pairs = {
        (1, 2): 0.3, (2, 1): 0.3,
        (2, 3): 0.7, (3, 2): 0.7
    }

    result = qc.quantum_prediction_engine([1, 2, 3])

    # Assert structure
    assert {
        "predicted_interactions",
        "overall_quantum_coherence",
        "uncertainty_estimate",
    } <= set(result)

    # CORRECTED: Assertions now only check for the raw float, as per instructions.
    predicted_interactions = result["predicted_interactions"]
    assert isinstance(predicted_interactions, dict)
    
    # Check the actual values which are now correct due to the fixed setup
    assert predicted_interactions[1] == pytest.approx(0.3)
    # User 2 is in two pairs: (1,2) with weight 0.3 and (2,3) with weight 0.7. Sum = 1.0
    assert predicted_interactions[2] == pytest.approx(1.0)
    assert predicted_interactions[3] == pytest.approx(0.7)
    
    for uid, prob in predicted_interactions.items():
        assert uid in [1, 2, 3]
        assert isinstance(prob, float) # Verifies the value is a raw float
        assert 0.0 <= prob <= 1.0

    assert 0.0 <= result["overall_quantum_coherence"] <= 1.0
    assert 0.0 <= result["uncertainty_estimate"] <= 1.0

# No changes needed for the rest of the file...
def test_calculate_influence_score_simple():
    if not nx:
        pytest.skip("networkx not installed")
    g = nx.DiGraph()
    g.add_edge(1, 2)
    g.add_edge(2, 3)
    g.add_edge(1, 3)
    result = calculate_influence_score(g, 2)
    assert 0 <= result["value"] <= 1
    assert result["unit"] == "probability"

def test_interaction_entropy_zero():
    dummy = types.SimpleNamespace(
        vibenodes=[], comments=[], liked_vibenodes=[], following=[]
    )
    result = calculate_interaction_entropy(dummy, None)
    assert result["value"] == 0.0


def test_interaction_entropy_with_decay():
    """Non-zero decay should not raise and returns bounded entropy."""
    now = datetime.datetime.utcnow()
    dummy = types.SimpleNamespace(
        vibenodes=[types.SimpleNamespace(created_at=now)],
        comments=[types.SimpleNamespace(created_at=now - datetime.timedelta(seconds=30))],
        liked_vibenodes=[],
        following=[],
    )
    result = calculate_interaction_entropy(dummy, None, decay_rate=0.01)
    assert 0.0 <= result["value"] <= 1.0

def test_quantum_context_superposition():
    qc = QuantumContext(fuzzy_enabled=True, simulate=True)
    val = qc.measure_superposition(0.6)
    assert 0.0 <= val["value"] <= 1.0
    assert val["distribution"] is not None

def test_query_influence():
    if not nx:
        pytest.skip("networkx not installed")
    g = nx.DiGraph()
    g.add_edge(1, 2, weight=0.5)
    g.add_edge(2, 3, weight=0.5)
    result = query_influence(g, 1, 3, perturb_iterations=2)
    assert 0 <= result["value"] <= 1

def test_validate_user_prediction():
    mock_prediction = {
        "user_id": 1,
        "predictions": {
            "will_create_content": {"probability": 0.7},
            "will_like_posts": {"probability": 0.4},
        },
    }
    actual_actions = {"create_content": True, "like_posts": False}
    validation = validate_user_prediction(mock_prediction, actual_actions)
    assert "overall_accuracy" in validation
    assert validation["overall_accuracy"] == 1.0

# --- NEW TESTS FOR PROMPT 1 ---

def test_detect_feedback_loops():
    """
    Tests the detect_feedback_loops function by creating a graph with a known
    cyclic loop and an acyclic part.
    """
    if not nx:
        pytest.skip("networkx not installed")

    # 1. Setup: Create a graph with a clear 1->2->3->1 loop and an unrelated edge
    g = InfluenceGraph()
    g.add_interaction(1, 2, weight=0.8)
    g.add_interaction(2, 3, weight=0.7)
    g.add_interaction(3, 1, weight=0.9)
    g.add_interaction(4, 5, weight=0.5) # Unrelated edge

    # 2. Execution: Call the function under test
    loops = detect_feedback_loops(g)

    # 3. Assertions:
    # Ensure exactly one loop is found
    assert len(loops) == 1
    # Validate the nodes in the loop (order may vary, so use a set)
    assert set(loops[0]["nodes"]) == {1, 2, 3}
    # Confirm the calculated strength is the geometric mean of the weights
    expected_strength = (0.8 * 0.7 * 0.9) ** (1/3)
    assert loops[0]["strength"] == pytest.approx(expected_strength)

def test_estimate_lag_effects():
    """
    Tests the estimate_lag_effects function by simulating logs where a metric
    change occurs at a fixed delay after an intervention.
    """
    # 1. Setup: Create logs with a known 60-second lag
    base_time = datetime.datetime.utcnow()
    
    intervention_log = [
        {"timestamp": base_time, "metric_id": "engagement"},
        {"timestamp": base_time + datetime.timedelta(seconds=100), "metric_id": "engagement"}
    ]
    
    metric_log = [
        # Baseline values before each intervention
        {"timestamp": base_time - datetime.timedelta(seconds=1), "metric_id": "engagement", "value": 0.5},
        {"timestamp": base_time + datetime.timedelta(seconds=99), "metric_id": "engagement", "value": 0.5},
        # Metric changes exactly 60 seconds after each intervention
        {"timestamp": base_time + datetime.timedelta(seconds=60), "metric_id": "engagement", "value": 0.8},
        {"timestamp": base_time + datetime.timedelta(seconds=160), "metric_id": "engagement", "value": 0.9}
    ]

    # 2. Execution: Call the function under test
    result = estimate_lag_effects(intervention_log, metric_log)

    # 3. Assertions:
    # Verify the lag is calculated correctly
    assert result["lag_estimate_seconds"] == pytest.approx(60.0)
    # Verify the correlation is perfect in this deterministic test case
    assert result["correlation_strength"] == pytest.approx(1.0)


# --- NEW TESTS FOR PROMPT 9 ---

def test_measure_autonomous_reasoning_basic():
    """Verify reasoning metrics aggregate correctly with partial data."""
    from scientific_metrics import measure_autonomous_reasoning

    sample = [
        {"id": 1, "status": "active", "confidence": 0.8, "novelty_score": 0.6},
        {"id": 2, "status": "active", "confidence": 0.7, "novelty_score": 0.7},
        {"id": 3, "status": "falsified", "confidence": 0.4, "novelty_score": 0.9},
        {"id": 4, "status": "active", "confidence": 0.9},  # missing novelty
    ]

    result = measure_autonomous_reasoning(sample)

    assert result["total_hypotheses"] == 4
    assert result["falsified_count"] == 1
    assert 0.7 <= result["average_confidence"] <= 0.8
    assert 0.4 <= result["average_novelty"] <= 0.7


def test_assess_meta_cognitive_awareness_basic():
    """Ensure meta-cognition metrics handle missing accuracy gracefully."""
    from scientific_metrics import assess_meta_cognitive_awareness

    logs = [
        {"bias_detected": True, "accuracy_score": 0.85},
        {"bias_detected": False, "accuracy_score": 0.9},
        {"bias_detected": True},  # missing accuracy
        {"bias_detected": False, "accuracy_score": 0.95},
    ]

    result = assess_meta_cognitive_awareness(logs)

    assert result["total_validations"] == 4
    assert result["bias_correction_events"] == 2
    assert 0.5 <= result["average_accuracy"] <= 0.95


def test_entangle_entities_negative_factor_raises():
    """Negative influence factors should raise ``ValueError``."""
    qc = QuantumContext()
    pair = tuple(sorted(("a", "b")))
    with pytest.raises(ValueError):
        qc.entangle_entities("a", "b", influence_factor=-1.0)
    assert pair not in qc.entangled_pairs
