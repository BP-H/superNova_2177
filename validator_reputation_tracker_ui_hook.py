# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards
from __future__ import annotations

from typing import Any, Dict

from frontend_bridge import register_route_once
from hook_manager import HookManager
from validator_reputation_tracker import update_validator_reputations

ui_hook_manager = HookManager()


async def update_reputations_ui(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Update validator reputations from a UI payload."""
    validations = payload.get("validations", [])
    result = update_validator_reputations(validations)
    from hooks import events
    minimal = {"reputations": result.get("reputations", {})}
    await ui_hook_manager.trigger(events.VALIDATOR_REPUTATIONS, minimal)
    return minimal


register_route_once(
    "update_reputations",
    update_reputations_ui,
    "Update validator reputations",
    "validators",
)
