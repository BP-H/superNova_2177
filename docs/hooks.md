# Hook Events

`hook_manager.py` enables loosely coupled extensions via hooks. Modules trigger
events using canonical string names defined in `hooks/events.py`. External
integrations should register callbacks using these constants to avoid typos.

Current public events:

- `events.NETWORK_ANALYSIS`
- `events.VALIDATOR_REPUTATIONS`
- `events.CONSENSUS_FORECAST_RUN`
- `events.REPUTATION_ANALYSIS_RUN`
- `events.COORDINATION_ANALYSIS_RUN`
- `events.BRIDGE_REGISTERED`
- `events.PROVENANCE_RETURNED`
- `events.SUGGESTION_INSPECTED`
- `events.FIX_PROPOSED`
- `events.MIDI_GENERATED`
- `events.HYPOTHESIS_RANKING`
- `events.HYPOTHESIS_CONFLICTS`
- `events.FULL_AUDIT_COMPLETED`
- `events.AUDIT_LOG`
- `events.CROSS_REMIX_CREATED`
- `events.CROSS_REMIX`
- `events.ENTROPY_DIVERGENCE`
