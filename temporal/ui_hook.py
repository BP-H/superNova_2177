from __future__ import annotations

from typing import Any, Dict, Optional

from frontend_bridge import register_route
from hook_manager import HookManager
from temporal_consistency_checker import analyze_temporal_consistency

# Exposed hook manager for observers
ui_hook_manager = HookManager()


async def analyze_temporal_ui(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Run temporal consistency analysis from a UI payload."""
    validations = payload.get("validations", [])
    reputations: Optional[Dict[str, float]] = payload.get("reputations")

    result = analyze_temporal_consistency(validations, reputations)
    await ui_hook_manager.trigger("temporal_analysis_run", result)
    return result


# Register with the central frontend router
register_route("temporal_consistency", analyze_temporal_ui)
