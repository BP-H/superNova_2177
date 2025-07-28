from __future__ import annotations

from typing import Any, Dict
from statistics import mean

from frontend_bridge import register_route
from hook_manager import HookManager
from validator_reputation_tracker import update_validator_reputations

# Dedicated hook manager for validator reputation events
ui_hook_manager = HookManager()


async def trigger_reputation_update_ui(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Update validator reputations using provided validations.

    Parameters
    ----------
    payload : dict
        JSON payload containing ``"validations"`` list.

    Returns
    -------
    dict
        Summary stats with ``validator_count`` and ``avg_reputation``.
    """
    validations = payload.get("validations", [])
    result = update_validator_reputations(validations)
    reputations = result.get("reputations", {})
    summary = {
        "validator_count": result.get("diversity", {}).get("validator_count", len(reputations)),
        "avg_reputation": round(mean(reputations.values()), 3) if reputations else 0.0,
    }
    # Emit event for observers
    await ui_hook_manager.trigger("validator_reputations_updated", summary)
    return summary


# Register with the central frontend router
register_route("reputation_update", trigger_reputation_update_ui)
