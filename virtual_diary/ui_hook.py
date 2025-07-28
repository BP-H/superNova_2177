from __future__ import annotations

from typing import Any, Dict

from frontend_bridge import register_route_once
from hook_manager import HookManager

from . import load_entries, add_entry

# Expose hook manager for listeners
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


async def add_entry_ui(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Add a diary entry and emit an event."""
    entry = payload.get("entry", payload)
    add_entry(entry)
    await ui_hook_manager.trigger("diary_entry_added", entry)
    return {"status": "added"}


# Register routes
register_route_once(
    "load_diary_entries",
    load_entries_ui,
    "Load diary entries",
    "diary",
)
register_route_once(
    "add_diary_entry",
    add_entry_ui,
    "Add a diary entry",
    "diary",
)
