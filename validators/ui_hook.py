from __future__ import annotations

from typing import Any, Dict

from frontend_bridge import register_route
from hook_manager import HookManager
from hooks import events

from .reputation_influence_tracker import compute_validator_reputations

# Exposed hook manager for observers
ui_hook_manager = HookManager()


async def compute_reputation_ui(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Compute validator reputations from a UI payload.

    Parameters
    ----------
    payload : dict
        Input dictionary containing ``"validations"`` and ``"consensus_scores"``.

    Returns
    -------
    dict
        Minimal result with ``validator_reputations`` and ``stats``.
    """
    validations = payload.get("validations", [])
    consensus_scores = payload.get("consensus_scores", {})

    result = compute_validator_reputations(validations, consensus_scores)
    minimal = {
        "validator_reputations": result.get("validator_reputations", {}),
        "stats": result.get("stats", {}),
    }

    await ui_hook_manager.trigger(events.REPUTATION_ANALYSIS_RUN, minimal)
    return minimal


# Register with the central frontend router
register_route("reputation_analysis", compute_reputation_ui)
