# protocols/agent_protocols_suite.py

"""
This module defines advanced agent infrastructure:
- InternalAgentProtocol: base class for memory-bound, message-driven agents
- AgentProfile: identity and capabilities
- AgentTaskContract: attachable missions
- SelfReflection: feedback-based correction
- RemoteSync: distributed agent pings
- DNAFork: agent evolution and cloning
- AgentCoreRuntime: launch, trigger, and score agents
- MessageHub: lightweight pub/sub for multi-agent broadcasts
- Skill system: modular skills agents can learn or mutate
- NegotiationLayer: agents delegate or reject tasks socially
- Fatigue + Belief tracking: add decay and trust to reasoning
"""

from typing import Callable, List, Dict, Any, Optional
import requests
import copy
import json
import time
import uuid
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)

# ----------------------
# 0. Internal Agent Protocol Base Class
# ----------------------

class InternalAgentProtocol:
    def __init__(self):
        self.memory: Dict[str, Any] = {}
        self.inbox: List[dict] = []
        self.name: str = self.__class__.__name__
        self.hooks: Dict[str, Callable[[dict], Any]] = {}

    def send(self, topic: str, payload: dict):
        logger.info(f"[{self.name}] SEND {topic}: {payload}")
        self.inbox.append({"topic": topic, "payload": payload})

    def receive(self, topic: str, handler: Callable[[dict], Any]):
        self.hooks[topic] = handler

    def process_event(self, event: dict):
        topic = event.get("event")
        payload = event.get("payload", {})
        if topic in self.hooks:
            return self.hooks[topic](payload)
        else:
            logger.warning(f"[{self.name}] Unknown event: {topic}")
            return {"error": f"Unhandled event {topic}"}

# ----------------------
# 1. Agent Personality Profiles
# ----------------------

class AgentProfile:
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
# 7. Message Bus
# ----------------------

class Message:
    def __init__(self, topic: str, data: dict, version: str = "1.0"):
        self.id = str(uuid.uuid4())
        self.topic = topic
        self.version = version
        self.data = data

class MessageHub:
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
        return [msg for msg in self.history if topic is None or msg.topic == topic]

# ----------------------
# 8. Agent Skills and Embodiment
# ----------------------

class Skill:
    def __init__(self, name: str, action: Callable[[dict], dict], description: str = ""):
        self.name = name
        self.action = action
        self.description = description

    def run(self, input_data: dict) -> dict:
        return self.action(input_data)

class EmbodiedAgent(InternalAgentProtocol):
    def __init__(self, name: str):
        super().__init__()
        self.name = name
        self.skills: Dict[str, Skill] = {}

    def register_skill(self, skill: Skill):
        self.skills[skill.name] = skill

    def invoke(self, skill_name: str, data: dict) -> dict:
        if skill_name in self.skills:
            return self.skills[skill_name].run(data)
        return {"error": f"Skill '{skill_name}' not found in {self.name}."}

# ----------------------
# 9. Social Behavior / Delegation Layer
# ----------------------

class AgentNegotiation:
    @staticmethod
    def propose_delegation(from_agent, to_agent, task: str, payload: dict):
        if to_agent.can(task):
            from_agent.send("DELEGATE_PROPOSAL", {"to": to_agent.name, "task": task})
            return to_agent.process_event({"event": task, "payload": payload})
        return {"error": f"{to_agent.name} can't handle task '{task}'"}

# ----------------------
# 10. Fatigue & Belief Tracking
# ----------------------

class FatigueMemoryMixin:
    def __init__(self):
        self.task_count = defaultdict(int)
        self.last_reset = time.time()

    def fatigue_score(self, task: str) -> float:
        elapsed = time.time() - self.last_reset
        base = self.task_count[task]
        decay = max(1.0 - (elapsed / 300), 0.1)
        return min(base * decay, 1.0)

    def register_task(self, task: str):
        self.task_count[task] += 1

class ProbabilisticBeliefSystem:
    def __init__(self):
        self.beliefs = defaultdict(lambda: 0.5)

    def update_belief(self, key: str, evidence: float):
        prior = self.beliefs[key]
        self.beliefs[key] = (prior + evidence) / 2

    def belief(self, key: str) -> float:
        return self.beliefs[key]

# ----------------------
# 11. Introspection Mixin
# ----------------------

class IntrospectiveMixin:
    def export_reasoning(self) -> dict:
        return {
            "name": self.name,
            "memory": self.memory,
            "recent_events": self.inbox[-5:],
            "handlers": list(self.hooks.keys())
        }
