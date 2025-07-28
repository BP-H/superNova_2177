from __future__ import annotations

import logging
from typing import Any, Dict

from frontend_bridge import register_route_once
from hook_manager import HookManager
from hooks import events
from validator_reputation_tracker import update_validator_reputations
from diversity_analyzer import compute_diversity_score

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

    await ui_hook_manager.trigger(events.REPUTATION_ANALYSIS_RUN, minimal)
    return minimal


async def update_reputations_ui(
    payload: Dict[str, Any], db, **_: Any
) -> Dict[str, Any]:
    """Update validator reputations and emit an internal event."""

    validations = payload.get("validations", [])
    result = update_validator_reputations(validations, db=db)

    minimal = {
        "reputations": result.get("reputations", {}),
        "diversity": result.get("diversity", {}),
    }

    try:
        hook_manager.fire_hooks(events.VALIDATOR_REPUTATIONS, result)
        hook_manager.fire_hooks("reputations_updated", minimal)
    except Exception:  # pragma: no cover - logging only
        logging.exception("Failed to fire reputations_updated hook")

    return minimal


async def compute_diversity_ui(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Compute diversity score from a UI payload."""

    validations = payload.get("validations", [])
    result = compute_diversity_score(validations)

    minimal = {
        "diversity_score": result.get("diversity_score", 0.0),
        "flags": result.get("flags", []),
    }

    await ui_hook_manager.trigger("diversity_score_computed", minimal)
    return minimal


async def trigger_reputation_update_ui(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Update reputations from UI payload and notify listeners.

    Parameters
    ----------
    payload : dict
        Dictionary containing ``"validations"`` list.

    Returns
    -------
    dict
        Summary with ``reputations`` and ``diversity``.
    """
    validations = payload.get("validations", [])
    result = update_validator_reputations(validations)
    summary = {
        "reputations": result.get("reputations", {}),
        "diversity": result.get("diversity", {}),
    }

    await ui_hook_manager.trigger("reputation_update_run", summary)
    return summary


# Register with the central frontend router
register_route_once(
    "reputation_analysis",
    compute_reputation_ui,
    "Compute validator reputations",
    "validators",
)
register_route_once(
    "update_validator_reputations",
    update_reputations_ui,
    "Persist validator reputation updates",
    "validators",
)
register_route_once(
    "reputation_update",
    trigger_reputation_update_ui,
    "Update reputations from payload",
    "validators",
)
register_route_once(
    "compute_diversity",
    compute_diversity_ui,
    "Compute diversity metrics",
    "validators",
)
