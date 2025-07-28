from __future__ import annotations

from typing import Any, Dict

from frontend_bridge import register_route
from hook_manager import HookManager
from validator_reputation_tracker import update_validator_reputations

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

    await ui_hook_manager.trigger("reputation_analysis_run", minimal)
    return minimal


# Register with the central frontend router
register_route("reputation_analysis", compute_reputation_ui)


async def trigger_reputation_update_ui(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Update validator reputations from UI-provided validations.

    Parameters
    ----------
    payload : dict
        Dictionary containing ``"validations"`` list.

    Returns
    -------
    dict
        Summary including ``reputations``, ``diversity`` and ``stats``.
    """
    validations = payload.get("validations", [])

    result = update_validator_reputations(validations)
    reputations = result.get("reputations", {})
    summary = {
        "reputations": reputations,
        "diversity": result.get("diversity", {}),
        "stats": {
            "validator_count": len(reputations),
            "avg_reputation": (
                round(sum(reputations.values()) / len(reputations), 3)
                if reputations
                else 0.0
            ),
        },
    }

    await ui_hook_manager.trigger("reputation_update_run", summary)
    return summary


# Register with the central frontend router
register_route("reputation_update", trigger_reputation_update_ui)
