from __future__ import annotations

from typing import Any, Dict

from diversity_analyzer import certify_validations
from frontend_bridge import register_route_once
from hook_manager import HookManager

ui_hook_manager = HookManager()


async def diversity_analysis_ui(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Certify validations and emit a diversity event."""
    if not isinstance(payload, dict):
        raise ValueError("payload must be a dict")

    validations = payload.get("validations")
    if not isinstance(validations, list):
        raise ValueError("payload['validations'] must be a list")

    result = certify_validations(validations)

    minimal = {
        "consensus_score": result.get("consensus_score"),
        "recommended_certification": result.get("recommended_certification"),
        "diversity_score": result.get("diversity", {}).get("diversity_score"),
    }

    await ui_hook_manager.trigger("diversity_certified", minimal)
    return minimal


register_route_once(
    "diversity_certify",
    diversity_analysis_ui,
    "Certify validations and emit diversity event",
    "diversity",
)
