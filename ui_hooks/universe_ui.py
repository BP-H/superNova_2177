# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards
from __future__ import annotations

from typing import Any, Dict, Optional, TYPE_CHECKING

from frontend_bridge import register_route_once
from hook_manager import HookManager

if TYPE_CHECKING:  # pragma: no cover - type hints only
    from superNova_2177 import CosmicNexus as UniverseManager
    from proposals.engine import ProposalEngine

ui_hook_manager = HookManager()

universe_manager: Optional["UniverseManager"] = None
proposal_engine: Optional[Any] = None


async def get_universe_overview(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Return an overview of a universe."""
    if universe_manager is None:
        raise RuntimeError("universe_manager not configured")
    universe_id = payload.get("universe_id")
    overview = universe_manager.get_overview(universe_id)
    await ui_hook_manager.trigger("universe_overview_returned", overview)
    return overview


async def list_available_proposals(payload: Dict[str, Any]) -> Dict[str, Any]:
    """List proposals available to the caller based on karma and state."""
    if universe_manager is None or proposal_engine is None:
        raise RuntimeError("universe_manager or proposal_engine not configured")
    user_id = payload.get("user_id")
    universe_id = payload.get("universe_id")
    karma = universe_manager.get_karma(user_id)
    state = universe_manager.get_state(universe_id)
    proposals = proposal_engine.list_proposals(karma, state)
    await ui_hook_manager.trigger("proposal_list_returned", proposals)
    return {"proposals": proposals}


async def submit_universe_proposal(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Persist a proposal in the caller's universe."""
    if universe_manager is None:
        raise RuntimeError("universe_manager not configured")
    universe_id = payload.get("universe_id")
    proposal = payload.get("proposal", {})
    proposal_id = universe_manager.submit_proposal(universe_id, proposal)
    await ui_hook_manager.trigger("proposal_submitted", {"proposal_id": proposal_id})
    return {"proposal_id": proposal_id}


register_route_once(
    "get_universe_overview",
    get_universe_overview,
    "Get an overview of the universe",
    "universe",
)
register_route_once(
    "list_available_proposals",
    list_available_proposals,
    "List available proposals",
    "universe",
)
register_route_once(
    "submit_universe_proposal",
    submit_universe_proposal,
    "Submit a universe proposal",
    "universe",
)
