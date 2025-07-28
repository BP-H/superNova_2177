# Protocols Package

This package contains modular agents and supporting utilities used for automated code validation workflows.

## Agents
- **CI_PRProtectorAgent** – repairs CI/PR failures by proposing patches.
- **GuardianInterceptorAgent** – inspects LLM suggestions for risky content.
- **MetaValidatorAgent** – audits patches and adjusts trust scores.
- **ObserverAgent** – monitors agent outputs and suggests forks when needed.
- **HarmonySynthesizerAgent** – converts aggregated metrics into short MIDI snippets.

Utilities, core interfaces, and prebuilt profiles are organized under corresponding subfolders for easy extension.

```python
from protocols import GuardianInterceptorAgent, CI_PRProtectorAgent
```

See `protocols/_registry.py` for a programmatic listing of available agents.
