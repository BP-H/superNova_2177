from __future__ import annotations

from typing import Any, Dict

from sqlalchemy.orm import Session

from frontend_bridge import register_route_once
from hook_manager import HookManager

try:  # pragma: no cover - optional heavy dependency
    from superNova_2177 import simulate_social_entanglement  # type: ignore
except Exception:  # pragma: no cover - fallback for test stub
    simulate_social_entanglement = None  # type: ignore

# Exposed hook manager for observers
ui_hook_manager = HookManager()


async def simulate_entanglement_ui(
    payload: Dict[str, Any], db: Session, **_: Any
) -> Dict[str, Any]:
    """Run :func:`simulate_social_entanglement` from a UI request."""
    user1_id = payload["user1_id"]
    user2_id = payload["user2_id"]

    if simulate_social_entanglement is None:
        raise RuntimeError("simulate_social_entanglement unavailable")

    result = simulate_social_entanglement(db, user1_id, user2_id)
    await ui_hook_manager.trigger("social_entanglement", result)
    return result


# Register route with the frontend router
register_route_once(
    "simulate_entanglement",
    simulate_entanglement_ui,
    "Simulate social entanglement",
    "social",
)
