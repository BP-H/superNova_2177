from __future__ import annotations

from typing import Any, Dict

from sqlalchemy.orm import Session

from hook_manager import HookManager
from frontend_bridge import register_route_once
from . import build_causal_graph

try:  # pragma: no cover - optional dependency during tests
    from superNova_2177 import simulate_social_entanglement
except Exception:  # pragma: no cover - fallback stub

    def simulate_social_entanglement(*_a: Any, **_k: Any) -> Dict[str, Any]:
        return {"source": None, "target": None, "probabilistic_influence": 0.0}


ui_hook_manager = HookManager()


async def build_graph_ui(_: Dict[str, Any], db: Session, **__: Any) -> Dict[str, Any]:
    """Return the causal graph structure for the current database."""
    graph = build_causal_graph(db)
    data = {
        "nodes": [{"id": n, **graph.graph.nodes.get(n, {})} for n in graph.graph.nodes],
        "edges": [
            {"source": u, "target": v, **d} for u, v, d in graph.graph.edges(data=True)
        ],
    }
    await ui_hook_manager.trigger("graph_built", data)
    return data


async def simulate_entanglement_ui(
    payload: Dict[str, Any], db: Session, **__: Any
) -> Dict[str, Any]:
    """Run :func:`simulate_social_entanglement` and return its result."""
    user1 = int(payload["user1_id"])
    user2 = int(payload["user2_id"])
    result = simulate_social_entanglement(db, user1, user2)
    await ui_hook_manager.trigger("entanglement_simulated", result)
    return result


register_route_once(
    "build_causal_graph",
    build_graph_ui,
    "Return the causal graph structure",
    "causal",
)
register_route_once(
    "simulate_entanglement_causal",
    simulate_entanglement_ui,
    "Simulate entanglement on the causal graph",
    "causal",
)
