"""Coordinator to launch and manage agent runs."""
from typing import Dict, Any
import time
import json
from .profiles import AgentProfile


class AgentCoreRuntime:
    """Launch and coordinate agents against input tasks."""
    def __init__(self, registry: Dict[str, AgentProfile]):
        self.registry = registry
        self.history = []

    def run(self, task: str, data: dict) -> Dict[str, Any]:
        result_log = {}
        for agent_id, agent in self.registry.items():
            if agent.can(task):
                result_log[agent_id] = self._simulate_run(agent, task, data)
        self.history.append({"task": task, "input": data, "result": result_log})
        return result_log

    def _simulate_run(self, agent: AgentProfile, task: str, data: dict) -> dict:
        try:
            time.sleep(0.1)
            return {
                "agent": agent.name,
                "action": task,
                "result": f"Simulated result of {task} by {agent.name}"
            }
        except Exception as e:
            return {"agent": agent.name, "error": str(e)}

    def export_log(self, path: str = "agent_log.json") -> None:
        with open(path, "w") as f:
            json.dump(self.history, f, indent=2)


# Provider API key storage
_provider_keys: Dict[str, str] = {}


def set_provider_key(provider: str, key: str) -> None:
    """Store an API key for the given provider."""
    _provider_keys[provider] = key


def get_key(provider: str) -> str:
    """Retrieve the stored API key for ``provider``."""
    return _provider_keys.get(provider, "")
