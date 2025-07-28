from __future__ import annotations

from typing import Any, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - type check only
    from protocols._registry import AGENT_REGISTRY  # noqa: F401


def _registry() -> Dict[str, Dict[str, Any]]:
    from protocols._registry import AGENT_REGISTRY
    return AGENT_REGISTRY

from protocols.core.runtime import set_provider_key
from llm_backends import get_backend

# Active agent instances keyed by name
active_agents: Dict[str, Any] = {}


async def list_agents_api(_: Dict[str, Any] | None = None) -> Dict[str, List[str]]:
    """Return available agent class names."""
    return {"agents": list(_registry().keys())}


async def launch_agents_api(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Instantiate and start selected agents."""
    provider = payload.get("provider", "")
    api_key = payload.get("api_key", "")
    if provider:
        set_provider_key(provider, api_key)

    backend_fn = None
    llm_backend = payload.get("llm_backend")
    if llm_backend:
        backend_fn = get_backend(llm_backend)
        if backend_fn is None:
            raise ValueError(f"Backend {llm_backend} not found")

    launched: List[str] = []
    for name in payload.get("agents", []):
        info = _registry().get(name)
        if info is None:
            raise ValueError(f"Agent {name} not found")
        cls = info["class"]
        try:
            if backend_fn is not None:
                try:
                    instance = cls(backend_fn)
                except TypeError:
                    instance = cls()
            else:
                instance = cls()
        except Exception as exc:  # pragma: no cover - initialization failure
            raise RuntimeError(f"Failed to launch {name}: {exc}") from exc
        active_agents[name] = instance
        start = getattr(instance, "start", None)
        if callable(start):
            try:
                start()
            except Exception:  # pragma: no cover - best effort
                pass
        launched.append(name)

    return {"launched": launched, "active_agents": list(active_agents.keys())}


async def step_agents_api(_: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """Trigger a single ``tick`` on all active agents."""
    stepped: List[str] = []
    for name, agent in active_agents.items():
        tick = getattr(agent, "tick", None)
        if callable(tick):
            try:
                tick()
            except Exception:  # pragma: no cover - step errors ignored
                continue
            stepped.append(name)
    return {"stepped": stepped, "active_agents": list(active_agents.keys())}
