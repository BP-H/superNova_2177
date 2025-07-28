# UI Routes

This document lists the default routes registered with `frontend_bridge`.
Each route name is dispatched via `dispatch_route` and maps to a
backend handler.

| Route | Description |
|-------|-------------|
|`list_routes`|Return the names of all registered routes.|
|`help`|Return structured route details grouped by category.|
|`describe_routes`|Return each route name with its handler docstring.|
|`rank_hypotheses_by_confidence`|Rank hypotheses using the reasoning layer.|
|`detect_conflicting_hypotheses`|Detect contradictions between hypotheses.|
|`register_hypothesis`|Register a new hypothesis and emit an event.|
|`update_hypothesis_score`|Update a hypothesis score.|
|`store_prediction`|Persist prediction information.|
|`get_prediction`|Retrieve a stored prediction.|
|`update_prediction_status`|Modify prediction status and outcome.|
|`list_agents`|List available protocol agent instances.|
|`launch_agents`|Instantiate selected protocol agents.|
|`step_agents`|Run a single tick on active agents.|
|`temporal_consistency`|Analyze temporal consistency across validations.|
|`tune_parameters`|Tune system parameters from metrics.|
|`forecast_consensus`|Forecast consensus trend from validations.|
|`queue_consensus_forecast`|Start an asynchronous consensus forecast.|
|`poll_consensus_forecast`|Check the status of a forecast job.|
|`coordination_analysis`|Run a network coordination risk analysis.|
|`queue_coordination_analysis`|Queue coordination analysis as a job.|
|`poll_coordination_analysis`|Poll the status of a coordination job.|
|`reputation_analysis`|Compute validator reputations from data.|
|`update_validator_reputations`|Persist validator reputation updates.|
|`reputation_update`|Update reputations and return summary.|
|`compute_diversity`|Calculate network diversity metrics.|
|`cross_universe_register_bridge`|Register cross-universe provenance data.|
|`cross_universe_get_provenance`|Retrieve provenance information for a coin.|
|`inspect_suggestion`|Inspect a suggestion using the Guardian agent.|
|`propose_fix`|Propose a fix through the Guardian agent.|
|`generate_midi`|Generate a short MIDI snippet.|
|`protocol_agents_list`|Return names of available protocol agent classes.|
|`protocol_agents_launch`|Launch protocol agents with optional backend.|
|`protocol_agents_step`|Trigger a single step on running protocol agents.|
|`queue_full_audit`|Queue a full introspection audit job.|
|`poll_full_audit`|Poll the status of an introspection audit.|
|`explain_audit`|Create a textual explanation for an audit trace.|

These routes are provided for research purposes only. STRICTLY A SOCIAL MEDIA PLATFORM.
They incorporate Intellectual Property & Artistic Inspiration protections
and follow Legal & Ethical Safeguards for community use.
