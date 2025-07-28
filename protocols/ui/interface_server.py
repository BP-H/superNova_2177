# START: agent_ui_controller_setup
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import importlib
import pkgutil
from typing import Dict, Type, Any, List, Optional

from protocols.core.runtime import set_provider_key, get_key
from llm_backends import get_backend

app = FastAPI(title="Protocol Agent UI")

# Discover available Agent classes dynamically
AGENT_PACKAGE = "protocols.agents"


def _scan_agents() -> Dict[str, Type[Any]]:
    agents: Dict[str, Type[Any]] = {}
    pkg = importlib.import_module(AGENT_PACKAGE)
    for _, module_name, _ in pkgutil.iter_modules(pkg.__path__):
        module = importlib.import_module(f"{AGENT_PACKAGE}.{module_name}")
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if isinstance(attr, type) and attr_name.endswith("Agent"):
                agents[attr_name] = attr
    return agents


available_agents = _scan_agents()
active_agents: Dict[str, Any] = {}


class LaunchRequest(BaseModel):
    provider: str
    api_key: str
    agents: List[str]
    llm_backend: Optional[str] = None
# END: agent_ui_controller_setup


# START: agent_ui_routes
@app.get("/agents")
def list_agents():
    """Return all available agent class names."""
    return list(available_agents.keys())


@app.post("/launch")
def launch_agents(req: LaunchRequest):
    """Instantiate and launch selected agents."""
    set_provider_key(req.provider, req.api_key)
    backend_fn = None
    if req.llm_backend:
        backend_fn = get_backend(req.llm_backend)
        if backend_fn is None:
            raise HTTPException(status_code=404, detail=f"Backend {req.llm_backend} not found")

    launched = []
    for name in req.agents:
        cls = available_agents.get(name)
        if cls is None:
            raise HTTPException(status_code=404, detail=f"Agent {name} not found")
        try:
            if backend_fn is not None:
                try:
                    instance = cls(backend_fn)
                except TypeError:
                    instance = cls()
            else:
                instance = cls()
            active_agents[name] = instance
            if hasattr(instance, "start") and callable(getattr(instance, "start")):
                instance.start()
            launched.append(name)
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"Failed to launch {name}: {exc}")

    return {"launched": launched, "provider": req.provider}


@app.post("/step")
def step_agents():
    """Trigger one tick on all active agents if they implement ``tick``."""
    stepped = []
    for name, agent in active_agents.items():
        tick = getattr(agent, "tick", None)
        if callable(tick):
            tick()
            stepped.append(name)
    return {"stepped": stepped, "active_agents": list(active_agents.keys())}
# END: agent_ui_routes
