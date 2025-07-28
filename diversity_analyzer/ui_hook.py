from __future__ import annotations

from typing import Any, Dict

from frontend_bridge import register_route_once
from hook_manager import HookManager
from . import compute_diversity_score, certify_validations

ui_hook_manager = HookManager()


async def compute_diversity_ui(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Compute diversity score from a UI payload."""
    validations = payload.get("validations", [])
    result = compute_diversity_score(validations)
    minimal = {
        "diversity_score": result.get("diversity_score", 0.0),
        "flags": result.get("flags", []),
    }
    await ui_hook_manager.trigger("diversity_score", minimal)
    return minimal


async def certify_validations_ui(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Certify validations from a UI payload."""
    validations = payload.get("validations", [])
    result = certify_validations(validations)
    minimal = {
        "consensus_score": result.get("consensus_score", 0.0),
        "recommended_certification": result.get("recommended_certification"),
        "flags": result.get("flags", []),
    }
    await ui_hook_manager.trigger("certify_validations", minimal)
    return minimal


register_route_once(
    "diversity_score",
    compute_diversity_ui,
    "Compute diversity score",
    "diversity",
)
register_route_once(
    "certify_validations",
    certify_validations_ui,
    "Certify validations",
    "diversity",
)
