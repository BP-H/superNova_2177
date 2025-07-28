from __future__ import annotations

from typing import Any, Dict, List

from frontend_bridge import register_route_once
from llm_backends import get_backend
from protocols.core.runtime import set_provider_key
from . import interface_server as server


async def list_agents_ui(payload: Dict[str, Any]) -> List[str]:
    """Return available protocol agent class names."""
    return list(server.available_agents.keys())


async def launch_agents_ui(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Instantiate and launch selected agents."""
    provider = payload.get("provider")
    api_key = payload.get("api_key")
    agents: List[str] = payload.get("agents", [])
    llm_backend = payload.get("llm_backend")

    if provider and api_key:
        set_provider_key(provider, api_key)

    backend_fn = None
    if llm_backend:
        backend_fn = get_backend(llm_backend)
        if backend_fn is None:
            raise ValueError(f"Backend {llm_backend} not found")

    launched = []
    for name in agents:
        cls = server.available_agents.get(name)
        if cls is None:
            raise ValueError(f"Agent {name} not found")
        try:
            if backend_fn is not None:
                try:
                    instance = cls(backend_fn)
                except TypeError:
                    instance = cls()
            else:
                instance = cls()
            server.active_agents[name] = instance
            if hasattr(instance, "start") and callable(getattr(instance, "start")):
                instance.start()
            launched.append(name)
        except Exception as exc:  # pragma: no cover - defensive
            raise RuntimeError(f"Failed to launch {name}: {exc}") from exc

    return {"launched": launched, "provider": provider}


async def step_agents_ui(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Trigger one tick on all active agents if they implement ``tick``."""
    stepped = []
    for name, agent in server.active_agents.items():
        tick = getattr(agent, "tick", None)
        if callable(tick):
            tick()
            stepped.append(name)
    return {"stepped": stepped, "active_agents": list(server.active_agents.keys())}


# Register routes with the frontend bridge
register_route_once(
    "protocol_agents_list",
    list_agents_ui,
    "List protocol agent classes",
    "protocols",
)
register_route_once(
    "protocol_agents_launch",
    launch_agents_ui,
    "Launch protocol agents",
    "protocols",
)
register_route_once(
    "protocol_agents_step",
    step_agents_ui,
    "Step running protocol agents",
    "protocols",
)
