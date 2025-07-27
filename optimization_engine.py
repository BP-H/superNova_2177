"""
Core logic for system self-tuning and adaptive interventions.
This module contains the "brain" of the adaptive system, allowing it to
suggest parameter changes and select optimal actions based on performance metrics.
"""
from typing import Dict, List
from scientific_utils import ScientificModel

try:
    # Attempt to import the main Config for production values
    from config import Config
except (ImportError, ModuleNotFoundError):
    # Fallback for isolated testing or environments where the main app isn't available
    class Config:
        INFLUENCE_MULTIPLIER = 1.2
        ENTROPY_REDUCTION_STEP = 0.2
        ENTROPY_CHAOS_THRESHOLD = 1500.0
        ENTROPY_INTERVENTION_THRESHOLD = 1200.0


@ScientificModel(
    source="Control Theory Heuristics",
    model_type="ParameterTuning",
    approximation="heuristic"
)
def tune_system_parameters(performance_metrics: Dict) -> Dict:
    """
    Suggests adjustments to Config parameters based on performance metrics.

    This function uses simple heuristics to guide the system toward a more
    stable or accurate state by suggesting small, incremental changes to its
    core operational parameters.

    Parameters
    ----------
    performance_metrics : Dict
        A dictionary containing key metrics like 'average_prediction_accuracy'
        and 'current_system_entropy'.

    Returns
    -------
    Dict
        A dictionary of suggested parameter overrides, e.g., {'INFLUENCE_MULTIPLIER': 1.1}.
    """
    overrides = {}
    accuracy = performance_metrics.get("average_prediction_accuracy", 0.7)
    entropy = performance_metrics.get("current_system_entropy", 1000.0)

    influence_multiplier_setting = getattr(Config, "INFLUENCE_MULTIPLIER", 1.2)
    influence_multiplier = float(influence_multiplier_setting)

    chaos_threshold_setting = getattr(Config, "ENTROPY_CHAOS_THRESHOLD", 1500.0)
    chaos_threshold = float(chaos_threshold_setting)

    # Heuristic 1: If prediction accuracy is low, make the model less aggressive.
    if accuracy < 0.6:
        # Suggest a 5% reduction in the influence multiplier
        overrides["INFLUENCE_MULTIPLIER"] = influence_multiplier * 0.95

    # Heuristic 2: If system entropy is dangerously high, strengthen countermeasures.
    if entropy > chaos_threshold:
        # Suggest a 10% increase in the entropy reduction step
        step_setting = getattr(Config, "ENTROPY_REDUCTION_STEP", 0.2)
        step = float(step_setting)
        overrides["ENTROPY_REDUCTION_STEP"] = step * 1.1

    return overrides

@ScientificModel(
    source="System State Machine",
    model_type="InterventionSelection",
    approximation="heuristic"
)
def select_optimal_intervention(system_state: Dict) -> str:
    """
    Selects the best intervention action based on the current system state.

    This function acts as a simple decision engine, choosing a high-level
    strategy to apply based on thresholds defined in the system configuration.

    Parameters
    ----------
    system_state : Dict
        A dictionary containing key state variables, primarily 'system_entropy'.

    Returns
    -------
    str
        A string representing the recommended action.
    """
    entropy = system_state.get("system_entropy", 1000.0)

    chaos_threshold_setting = getattr(Config, "ENTROPY_CHAOS_THRESHOLD", 1500.0)
    chaos_threshold = float(chaos_threshold_setting)

    intervention_threshold_setting = getattr(
        Config, "ENTROPY_INTERVENTION_THRESHOLD", 1200.0
    )
    intervention_threshold = float(intervention_threshold_setting)

    if entropy > chaos_threshold:
        return "trigger_emergency_harmonization"
    elif entropy > intervention_threshold:
        return "boost_novel_content"
    else:
        return "maintain_equilibrium"

@ScientificModel(
    source="Metacognitive Audit Framework",
    model_type="EffectivenessEvaluation",
    approximation="heuristic",
)
def evaluate_optimization_effectiveness(
    past_metrics: List[Dict], intervention_history: List[str]
) -> float:
    """Return a simple effectiveness score from historic metrics and actions.

    The function compares the earliest and latest metric snapshots in
    ``past_metrics``. If ``average_prediction_accuracy`` increased and
    ``current_system_entropy`` decreased, the optimization is considered
    effective.

    The returned score is a weighted combination of accuracy improvement and
    normalized entropy reduction. A larger number of interventions slightly
    penalizes the final score.

    Parameters
    ----------
    past_metrics : List[Dict]
        Historical metric dictionaries containing ``average_prediction_accuracy``
        and ``current_system_entropy``.
    intervention_history : List[str]
        Ordered list of interventions that were applied.

    Returns
    -------
    float
        Effectiveness value between ``-1.0`` and ``1.0`` where positive values
        indicate an overall improvement.
    """

    if len(past_metrics) < 2:
        return 0.0

    start = past_metrics[0]
    end = past_metrics[-1]

    acc_start = float(start.get("average_prediction_accuracy", 0.0))
    acc_end = float(end.get("average_prediction_accuracy", acc_start))
    entropy_start = float(start.get("current_system_entropy", 0.0))
    entropy_end = float(end.get("current_system_entropy", entropy_start))

    acc_change = acc_end - acc_start
    entropy_change = entropy_start - entropy_end

    entropy_norm = entropy_start or 1.0
    score = 0.6 * acc_change + 0.4 * (entropy_change / entropy_norm)

    penalty = 1.0 / max(1, len(intervention_history))

    return score * penalty
