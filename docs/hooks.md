# Hook Events

The project uses a lightweight `HookManager` to allow different modules to notify
subscribers when certain actions occur. The following constants from
`hooks/events.py` define the canonical event names emitted across the codebase:

- `BRIDGE_REGISTERED` – a cross‑universe bridge was registered.
- `PROVENANCE_RETURNED` – provenance data was returned to the caller.
- `COORDINATION_ANALYSIS_RUN` – coordination analysis finished running.
- `NETWORK_ANALYSIS` – summary network metrics were produced.
- `FULL_AUDIT_COMPLETED` – a full introspection audit completed.
- `AUDIT_LOG` – an audit log entry was created or updated.
- `HYPOTHESIS_RANKING` – hypotheses were ranked by confidence.
- `HYPOTHESIS_CONFLICTS` – conflicting hypotheses were detected.
- `REPUTATION_ANALYSIS_RUN` – validator reputation analysis finished.
- `CROSS_REMIX_CREATED` – a cross‑remix coin was minted.
- `ENTROPY_DIVERGENCE` – interaction entropy exceeded the threshold.

Hook callbacks can be registered via `HookManager.register_hook` and will receive
the payload passed to `trigger()` or `fire_hooks()`.
