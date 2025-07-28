from __future__ import annotations

from typing import Any, Dict

from frontend_bridge import register_route
from hook_manager import HookManager
from hooks import events
from importlib import import_module

# Exposed hook manager so external modules can subscribe to simulation events
ui_hook_manager = HookManager()


async def simulate_entanglement_ui(
    payload: Dict[str, Any],
    db,
    **_: Any,
) -> Dict[str, Any]:
    """Run social entanglement simulation between two users.

    Parameters
    ----------
    payload:
        Must contain ``"user1_id"`` and ``"user2_id"`` keys.
    db:
        Database session passed through from the UI layer.

    Returns
    -------
    dict
        Result of :func:`simulate_social_entanglement`.
    """
    user1_id = payload["user1_id"]  # raises KeyError if missing
    user2_id = payload["user2_id"]

    module = import_module("superNova_2177")
    simulate_social_entanglement = getattr(module, "simulate_social_entanglement")
    result = simulate_social_entanglement(db, user1_id, user2_id)

    await ui_hook_manager.trigger(events.ENTANGLEMENT_SIMULATION_RUN, result)
    return result


# Register the route with the central router so UIs can invoke it
register_route(
    "simulate_entanglement",
    simulate_entanglement_ui,
    "Simulate quantum entanglement",
    "quantum",
)
