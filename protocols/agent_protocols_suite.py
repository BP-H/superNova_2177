# protocols/agent_protocols_suite.py

"""
This module defines core agent infrastructure:
- AgentProfile: identity and capabilities
- AgentTaskContract: attachable missions
- SelfReflection: feedback-based correction
- RemoteSync: distributed agent pings
- DNAFork: agent evolution and cloning
- AgentCoreRuntime: launch, trigger, and score agents
- MessageHub: lightweight pub/sub for multi-agent broadcasts
"""

from typing import Callable, List, Dict, Any
import requests
import copy
import json
import time
import uuid
from collections import defaultdict

# ----------------------
# 1. Agent Personality Profiles
# ----------------------

class AgentProfile:
    """Defines traits and capabilities of autonomous agents."""
    def __init__(self, name: str, traits: List[str], powers: List[str]):
        self.name = name
        self.traits = traits
        self.powers = powers

    def can(self, task: str) -> bool:
        return task in self.powers

    def describe(self) -> str:
        return f"{self.name}: {'/'.join(self.traits)} with powers: {', '.join(self.powers)}"


# ----------------------
# 2. Agent Task Contracts
# ----------------------

class AgentTaskContract:
    def __init__(self, task_name: str, criteria: Callable[[dict], bool], action: Callable[[dict], dict]):
        self.task_name = task_name
        self.criteria = criteria
        self.action = action

    def attempt(self, payload: dict) -> dict:
        if self.criteria(payload):
            return self.action(payload)
        return {"skipped": True}


# ----------------------
# 3. Self-Correction via Reflection
# ----------------------

def self_reflect(agent, memory_log: List[dict]) -> dict:
    last_output = memory_log[-1] if memory_log else {}
    if "ERROR" in str(last_output):
        agent.send("SELF_FIX", {"note": "attempting auto-correction"})
        return agent.process_event({"event": "RETRY", "payload": last_output})
    return {"status": "ok"}


# ----------------------
# 4. Remote Agent Sync Protocol
# ----------------------

def ping_agent(url: str) -> bool:
    try:
        res = requests.get(f"{url}/status")
        return res.status_code == 200
    except Exception:
        return False


def handshake(agent_id: str, url: str) -> dict:
    return {"agent_id": agent_id, "remote_status": ping_agent(url)}


# ----------------------
# 5. DNA-Based Forking
# ----------------------

def fork_agent(agent: Any, mutation: Dict[str, Any]) -> Any:
    child = copy.deepcopy(agent)
    for key, value in mutation.items():
        setattr(child, key, value)
    child.send("FORK_NOTICE", {"from": agent.__class__.__name__})
    return child


# ----------------------
# 6. Agent Runtime Coordinator
# ----------------------

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

    def export_log(self, path: str = "agent_log.json"):
        with open(path, "w") as f:
            json.dump(self.history, f, indent=2)


# ----------------------
# 7. Message Bus (Broadcast System)
# ----------------------

class Message:
    """A versioned agent message with metadata."""
    def __init__(self, topic: str, data: dict, version: str = "1.0"):
        self.id = str(uuid.uuid4())
        self.topic = topic
        self.version = version
        self.data = data


class MessageHub:
    """
    Shared communication hub for agents, tools, and diagnostics.
    Supports publish/subscribe model.
    """
    def __init__(self):
        self.subscribers: Dict[str, List[Callable[[Message], None]]] = defaultdict(list)
        self.history: List[Message] = []

    def publish(self, topic: str, data: dict, version: str = "1.0") -> str:
        message = Message(topic, data, version)
        self.history.append(message)
        for callback in self.subscribers.get(topic, []):
            callback(message)
        return message.id

    def subscribe(self, topic: str, handler: Callable[[Message], None]) -> None:
        self.subscribers[topic].append(handler)

    def get_messages(self, topic: str = None) -> List[Message]:
        if topic:
            return [msg for msg in self.history if msg.topic == topic]
        return self.history


# Example use:
# hub = MessageHub()
# hub.subscribe("INTEGRITY_RESULT", lambda m: print(f"[AUDIT] {m.data}"))
# hub.publish("INTEGRITY_RESULT", {"score": 0.9, "verdict": "PASS"})
