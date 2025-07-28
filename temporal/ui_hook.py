from __future__ import annotations

from typing import Any, Dict

from frontend_bridge import register_route_once
from hook_manager import HookManager
from temporal_consistency_checker import analyze_temporal_consistency

# Exposed hook manager for observers
ui_hook_manager = HookManager()


async def analyze_temporal_ui(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Run temporal consistency analysis from a UI payload."""
    validations = payload.get("validations", [])
    reputations = payload.get("reputations")

    result = analyze_temporal_consistency(validations, reputations)
    minimal = {
        "avg_delay_hours": result.get("avg_delay_hours", 0.0),
        "consensus_volatility": result.get("consensus_volatility", 0.0),
        "flags": result.get("flags", []),
    }

    await ui_hook_manager.trigger("temporal_analysis_run", minimal)
    return minimal


register_route_once(
    "temporal_consistency",
    analyze_temporal_ui,
    "Analyze temporal consistency",
    "temporal",
)
