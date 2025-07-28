from __future__ import annotations

from typing import Any, Dict

from frontend_bridge import register_action
from hook_manager import HookManager

from .network_coordination_detector import analyze_coordination_patterns

# Exposed hook manager for external subscribers
ui_hook_manager = HookManager()


async def trigger_coordination_analysis_ui(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Run coordination analysis from UI payload.

    Parameters
    ----------
    payload : dict
        JSON payload containing ``"validations"`` list.

    Returns
    -------
    dict
        Minimal result with ``overall_risk_score`` and ``graph``.
    """
    validations = payload.get("validations", [])
    result = analyze_coordination_patterns(validations)
    minimal = {
        "overall_risk_score": result.get("overall_risk_score", 0.0),
        "graph": result.get("graph", {}),
    }
    # Emit event for observers
    await ui_hook_manager.trigger("coordination_analysis_run", minimal)
    return minimal


# Register with the central frontend router
register_action("network.run", trigger_coordination_analysis_ui)
