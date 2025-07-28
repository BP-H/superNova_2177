# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards
from __future__ import annotations

from typing import Any, Dict

from frontend_bridge import register_route_once
from hook_manager import HookManager

from . import load_votes as _load_votes
from . import record_vote as _record_vote

# Exposed hook manager so other modules can listen for vote events
ui_hook_manager = HookManager()


async def record_vote_ui(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Record a vote from the UI and emit an event."""
    _record_vote(payload)
    await ui_hook_manager.trigger("vote_recorded", payload)
    return {"recorded": True}


async def load_votes_ui(_: Dict[str, Any]) -> Dict[str, Any]:
    """Return all recorded votes and emit an event."""
    votes = _load_votes()
    await ui_hook_manager.trigger("votes_loaded", votes)
    return votes


# Register with the frontend bridge
register_route_once(
    "record_vote",
    record_vote_ui,
    "Record a new vote",
    "vote",
)
register_route_once(
    "load_votes",
    load_votes_ui,
    "Load recorded votes",
    "vote",
)
