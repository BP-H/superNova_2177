import pytest
from optimization_engine import (
    tune_system_parameters,
    select_optimal_intervention,
    settings,
)

def test_module_imports_cleanly():
    """
    Validates that the optimization_engine module and its settings can be
    imported without errors, ensuring the fallback config logic is sound.
    """
    assert hasattr(settings, "INFLUENCE_MULTIPLIER")
    assert hasattr(settings, "ENTROPY_REDUCTION_STEP")

def test_tune_system_parameters_low_accuracy():
    """
    Tests that when prediction accuracy is low, the system suggests
    reducing the influence multiplier to make the model less aggressive.
    """
    # Setup: Input metrics with low prediction accuracy
    performance_metrics = {
        "average_prediction_accuracy": 0.4,
        "current_system_entropy": 1000.0
    }
    
    # Execution
    overrides = tune_system_parameters(performance_metrics)
    
    # Assert: The output suggests reducing the INFLUENCE_MULTIPLIER
    assert "INFLUENCE_MULTIPLIER" in overrides
    assert overrides["INFLUENCE_MULTIPLIER"] == pytest.approx(settings.INFLUENCE_MULTIPLIER * 0.95)

def test_tune_system_parameters_high_entropy():
    """
    Tests that when system entropy is critically high, the system suggests
    increasing the strength of its corrective measures.
    """
    # Setup: Input metrics with entropy above the chaos threshold
    performance_metrics = {
        "average_prediction_accuracy": 0.9,
        "current_system_entropy": 2000.0  # Above the 1500.0 threshold
    }
    
    # Execution
    overrides = tune_system_parameters(performance_metrics)
    
    # Assert: The output suggests increasing the ENTROPY_REDUCTION_STEP
    assert "ENTROPY_REDUCTION_STEP" in overrides
    expected_step = float(settings.ENTROPY_REDUCTION_STEP) * 1.1
    assert overrides["ENTROPY_REDUCTION_STEP"] == pytest.approx(expected_step)

def test_tune_system_parameters_normal_state():
    """
    Tests that when system metrics are healthy, no parameter changes are suggested.
    """
    # Setup: Input metrics in a normal, healthy range
    performance_metrics = {
        "average_prediction_accuracy": 0.85,
        "current_system_entropy": 1100.0
    }
    
    # Execution
    overrides = tune_system_parameters(performance_metrics)
    
    # Assert: The output dictionary is empty
    assert not overrides

def test_select_optimal_intervention_high_entropy():
    """
    Tests that for dangerously high entropy, the 'emergency' intervention is selected.
    """
    # Setup: System state with entropy above the chaos threshold
    system_state = {"system_entropy": 1600.0}
    
    # Execution & Assertion
    assert select_optimal_intervention(system_state) == "trigger_emergency_harmonization"

def test_select_optimal_intervention_moderate_entropy():
    """
    Tests that for moderately high entropy, a standard intervention is selected.
    """
    # Setup: System state with entropy between the intervention and chaos thresholds
    system_state = {"system_entropy": 1300.0}
    
    # Execution & Assertion
    assert select_optimal_intervention(system_state) == "boost_novel_content"

def test_select_optimal_intervention_normal_entropy():
    """
    Tests that for normal entropy levels, the system maintains its current state.
    """
    # Setup: System state with entropy below the intervention threshold
    system_state = {"system_entropy": 1000.0}
    
    # Execution & Assertion
    assert select_optimal_intervention(system_state) == "maintain_equilibrium"
