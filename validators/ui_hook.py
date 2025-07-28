from __future__ import annotations

import logging
from typing import Any, Dict

from frontend_bridge import register_route
from hook_manager import HookManager
from validator_reputation_tracker import update_validator_reputations

from .reputation_influence_tracker import compute_validator_reputations

# Exposed hook manager for observers
ui_hook_manager = HookManager()
# Internal hook manager for update_reputations_ui events
hook_manager = HookManager()


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


async def update_reputations_ui(
    payload: Dict[str, Any], db, **_: Any
) -> Dict[str, Any]:
    """Update validator reputations and emit an internal event."""

    validations = payload.get("validations", [])
    result = update_validator_reputations(validations, db=db)

    try:
        hook_manager.fire_hooks("validator_reputations", result)
    except Exception:  # pragma: no cover - logging only
        logging.exception("Failed to fire validator_reputations hook")

    return result


# Register with the central frontend router
register_route("reputation_analysis", compute_reputation_ui)
register_route("update_validator_reputations", update_reputations_ui)
