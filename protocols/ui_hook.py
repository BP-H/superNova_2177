from __future__ import annotations

from typing import Any, Dict, List

from frontend_bridge import register_route
from hook_manager import HookManager

from protocols.agents.cross_universe_bridge_agent import CrossUniverseBridgeAgent

# Exposed hook manager and agent instance
bridge_hook_manager = HookManager()
bridge_agent = CrossUniverseBridgeAgent()


async def register_bridge_ui(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and store cross-universe provenance via the UI."""
    result = bridge_agent.register_bridge(payload)
    await bridge_hook_manager.trigger("bridge_registered", result)
    return result


async def get_provenance_ui(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Return provenance information for ``coin_id`` via the UI."""
    result = bridge_agent.get_provenance(payload)
    await bridge_hook_manager.trigger("provenance_returned", result)
    return result


# Register with the central frontend router
register_route("cross_universe_register_bridge", register_bridge_ui)
register_route("cross_universe_get_provenance", get_provenance_ui)
