from __future__ import annotations

from typing import Any, Dict, List

from frontend_bridge import register_route
from hook_manager import HookManager
from . import compute_diversity_score, certify_validations

# Exposed hook manager so external modules can subscribe to events
ui_hook_manager = HookManager()


async def compute_diversity_ui(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Compute diversity score from a UI payload."""
    validations: List[Dict[str, Any]] = payload.get("validations", [])
    result = compute_diversity_score(validations)
    minimal = {
        "diversity_score": result.get("diversity_score", 0.0),
        "flags": result.get("flags", []),
    }
    await ui_hook_manager.trigger("diversity_score_computed", minimal)
    return minimal


async def certify_validations_ui(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Certify validations and emit a minimal summary."""
    validations: List[Dict[str, Any]] = payload.get("validations", [])
    result = certify_validations(validations)
    minimal = {
        "consensus_score": result.get("consensus_score", 0.0),
        "recommended_certification": result.get("recommended_certification"),
    }
    await ui_hook_manager.trigger("validations_certified", minimal)
    return minimal


# Register routes with the frontend bridge
register_route("compute_diversity", compute_diversity_ui)
register_route("certify_validations", certify_validations_ui)
