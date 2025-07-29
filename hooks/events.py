"""Canonical event names used by :class:`HookManager`.

Import these constants when registering or triggering hooks to avoid
string mismatches.
"""

# Events emitted from network analysis modules
NETWORK_ANALYSIS = "network_analysis"
VALIDATOR_REPUTATIONS = "reputations_updated"
CONSENSUS_FORECAST_RUN = "consensus_forecast_run"
REPUTATION_ANALYSIS_RUN = "reputation_analysis_run"
COORDINATION_ANALYSIS_RUN = "coordination_analysis_run"
ENTANGLEMENT_SIMULATION_RUN = "entanglement_simulation_run"

# Events from protocol agents and utilities
BRIDGE_REGISTERED = "bridge_registered"
PROVENANCE_RETURNED = "provenance_returned"
SUGGESTION_INSPECTED = "suggestion_inspected"
FIX_PROPOSED = "fix_proposed"
MIDI_GENERATED = "midi_generated"

# Events from hypothesis and introspection modules
HYPOTHESIS_RANKING = "hypothesis_ranking"
HYPOTHESIS_CONFLICTS = "hypothesis_conflicts"
FULL_AUDIT_COMPLETED = "full_audit_completed"
AUDIT_LOG = "audit_log"

# Core protocol events
CROSS_REMIX_CREATED = "cross_remix_created"
CROSS_REMIX = "cross_remix"
ENTROPY_DIVERGENCE = "entropy_divergence"

__all__ = [name for name in globals() if name.isupper()]
