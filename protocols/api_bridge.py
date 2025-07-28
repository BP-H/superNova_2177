from __future__ import annotations

from typing import Any, Dict, List

from llm_backends import get_backend

# Active agent instances keyed by name
ACTIVE_AGENTS: Dict[str, Any] = {}


async def list_agents(_payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """Return available agent names from ``AGENT_REGISTRY``."""
    from ._registry import AGENT_REGISTRY

    return {"agents": list(AGENT_REGISTRY.keys())}


async def launch_agents(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Instantiate and store selected agents.

    Parameters
    ----------
    payload : dict
        Expected to contain ``"agents"`` list and optional ``"llm_backend"`` name.
    """
    names = payload.get("agents", [])
    if not isinstance(names, list):
        raise ValueError("payload['agents'] must be a list")

    from ._registry import AGENT_REGISTRY

    backend_name = payload.get("llm_backend")
    backend_fn = None
    if backend_name:
        backend_fn = get_backend(backend_name)
        if backend_fn is None:
            raise ValueError(f"Unknown backend {backend_name}")

    launched: List[str] = []
    for name in names:
        meta = AGENT_REGISTRY.get(name)
        if meta is None:
            continue
        cls = meta["class"]
        try:
            if backend_fn is not None:
                try:
                    agent = cls(backend_fn)
                except TypeError:
                    agent = cls()
            else:
                agent = cls()
        except Exception:
            continue
        ACTIVE_AGENTS[name] = agent
        start = getattr(agent, "start", None)
        if callable(start):
            try:
                start()
            except Exception:
                pass
        launched.append(name)

    return {"launched": launched}


async def step_agents(_payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """Trigger ``tick`` on active agents if available."""
    stepped: List[str] = []
    for name, agent in list(ACTIVE_AGENTS.items()):
        tick = getattr(agent, "tick", None)
        if callable(tick):
            try:
                tick()
                stepped.append(name)
            except Exception:
                pass
    return {"stepped": stepped, "active_agents": list(ACTIVE_AGENTS.keys())}


def _reset() -> None:
    """Clear all active agents (for tests)."""
    ACTIVE_AGENTS.clear()
