from __future__ import annotations

from typing import Any, Dict

from frontend_bridge import register_route
from hook_manager import HookManager

from . import load_entries

# Exposed hook manager so external listeners can react to diary events
ui_hook_manager = HookManager()


async def load_entries_ui(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Load diary entries and emit a hook event."""
    try:
        limit = int(payload.get("limit", 20))
    except (TypeError, ValueError):
        limit = 20

    entries = load_entries(limit=limit)
    await ui_hook_manager.trigger("diary_entries_loaded", entries)
    return {"entries": entries}


# Register route with the frontend router
register_route("load_diary_entries", load_entries_ui)
