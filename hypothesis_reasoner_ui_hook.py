from __future__ import annotations

from typing import Any, Dict

from db_models import SessionLocal
from hook_manager import HookManager
from frontend_bridge import register_route_once
from hypothesis_reasoner import auto_flag_stale_or_redundant

ui_hook_manager = HookManager()


async def auto_flag_stale_ui(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Automatically flag stale or redundant hypotheses."""
    db = SessionLocal()
    try:
        flagged = auto_flag_stale_or_redundant(db)
    finally:
        db.close()
    result = {"flagged": flagged}
    await ui_hook_manager.trigger("stale_flagged", result)
    return result


register_route_once(
    "auto_flag_stale",
    auto_flag_stale_ui,
    "Auto-flag stale hypotheses",
    "hypothesis",
)
