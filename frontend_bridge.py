"""Lightweight router for UI callbacks."""

from __future__ import annotations

from typing import Any, Awaitable, Callable, Dict, Union

from tank_registry import dispatch_route, register_route, registry

Handler = Callable[..., Union[Dict[str, Any], Awaitable[Dict[str, Any]]]]



def _list_routes(_: Dict[str, Any]) -> Dict[str, Any]:
    """Return the names of all registered routes."""
    return {"routes": registry.list_routes()}


register_route("list_routes", _list_routes)


def load_routes() -> None:
    """Register all built-in UI routes once."""

    # Hypothesis-related routes
    from hypothesis.ui_hook import (
        rank_hypotheses_by_confidence_ui,
        detect_conflicting_hypotheses_ui,
        register_hypothesis_ui,
        update_hypothesis_score_ui,
        rank_hypotheses_ui,
        synthesize_consensus_ui,
    )
    register_route("rank_hypotheses_by_confidence", rank_hypotheses_by_confidence_ui)
    register_route("detect_conflicting_hypotheses", detect_conflicting_hypotheses_ui)
    register_route("register_hypothesis", register_hypothesis_ui)
    register_route("update_hypothesis_score", update_hypothesis_score_ui)
    register_route("rank_hypotheses", rank_hypotheses_ui)
    register_route("synthesize_consensus", synthesize_consensus_ui)

    from hypothesis_meta_evaluator_ui_hook import trigger_meta_evaluation_ui
    from hypothesis_reasoner_ui_hook import auto_flag_stale_ui
    from validation_certifier_ui_hook import run_integrity_analysis_ui
    from validator_reputation_tracker_ui_hook import update_reputations_ui

    register_route("trigger_meta_evaluation", trigger_meta_evaluation_ui)
    register_route("auto_flag_stale", auto_flag_stale_ui)
    register_route("run_integrity_analysis", run_integrity_analysis_ui)
    register_route("update_reputations", update_reputations_ui)

    # Prediction-related routes
    from predictions.ui_hook import (
        store_prediction_ui,
        get_prediction_ui,
        update_prediction_status_ui,
    )
    register_route("store_prediction", store_prediction_ui)
    register_route("get_prediction", get_prediction_ui)
    register_route("update_prediction_status", update_prediction_status_ui)

    # Optimization
    from optimization.ui_hook import tune_parameters_ui
    register_route("tune_parameters", tune_parameters_ui)

    # Consensus forecast and network analysis
    from consensus.ui_hook import (
        forecast_consensus_ui,
        queue_consensus_forecast_ui,
        poll_consensus_forecast_ui,
    )
    register_route("forecast_consensus", forecast_consensus_ui)
    register_route("queue_consensus_forecast", queue_consensus_forecast_ui)
    register_route("poll_consensus_forecast", poll_consensus_forecast_ui)

    from network.ui_hook import (
        trigger_coordination_analysis_ui,
        queue_coordination_analysis_ui,
        poll_coordination_analysis_ui,
    )
    register_route("coordination_analysis", trigger_coordination_analysis_ui)
    register_route("queue_coordination_analysis", queue_coordination_analysis_ui)
    register_route("poll_coordination_analysis", poll_coordination_analysis_ui)

    # Introspection and audits
    from introspection.ui_hook import queue_full_audit_ui, poll_full_audit_ui
    register_route("queue_full_audit", queue_full_audit_ui)
    register_route("poll_full_audit", poll_full_audit_ui)

    from audit.explainer_ui_hook import _explain_audit_route
    register_route("explain_audit", _explain_audit_route)

    # Validator related
    from validators.ui_hook import (
        compute_reputation_ui,
        update_reputations_ui,
        trigger_reputation_update_ui,
        compute_diversity_ui,
    )
    register_route("reputation_analysis", compute_reputation_ui)
    register_route("update_validator_reputations", update_reputations_ui)
    register_route("reputation_update", trigger_reputation_update_ui)
    register_route("compute_diversity", compute_diversity_ui)

    # Diversity analyzer
    from diversity_analyzer.ui_hook import (
        compute_diversity_ui as diversity_score_ui,
        certify_validations_ui,
    )
    register_route("diversity_score", diversity_score_ui)
    register_route("certify_validations", certify_validations_ui)

    # Protocol agent management
    from protocols.ui.api_bridge import (
        list_agents_ui,
        launch_agents_ui,
        step_agents_ui,
    )
    register_route("list_agents", list_agents_ui)
    register_route("launch_agents", launch_agents_ui)
    register_route("step_agents", step_agents_ui)

    from protocols.ui_hook import register_bridge_ui, get_provenance_ui
    register_route("cross_universe_register_bridge", register_bridge_ui)
    register_route("cross_universe_get_provenance", get_provenance_ui)

    # Temporal analysis
    from temporal.ui_hook import analyze_temporal_ui
    register_route("temporal_consistency", analyze_temporal_ui)

    # Universe management
    from ui_hooks.universe_ui import (
        get_universe_overview,
        list_available_proposals,
        submit_universe_proposal,
    )
    register_route("get_universe_overview", get_universe_overview)
    register_route("list_available_proposals", list_available_proposals)
    register_route("submit_universe_proposal", submit_universe_proposal)


# Load routes immediately when this module is imported
load_routes()
