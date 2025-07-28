from __future__ import annotations

from typing import Any, Dict

from frontend_bridge import register_route_once
from hook_manager import HookManager
from virtual_diary import load_entries

ui_hook_manager = HookManager()


async def get_diary_entries_ui(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Return diary entries using :func:`load_entries`."""
    limit = payload.get("limit")
    try:
        limit_int = int(limit) if limit is not None else 20
    except (TypeError, ValueError):
        limit_int = 20
    entries = load_entries(limit=limit_int)
    await ui_hook_manager.trigger("diary_entries_returned", entries)
    return {"entries": entries}


register_route_once(
    "get_diary_entries",
    get_diary_entries_ui,
    "Retrieve diary entries",
    "diary",
)
