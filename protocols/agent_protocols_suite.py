# protocols/agent_protocols_suite.py

"""
This module defines core agent infrastructure:
- AgentProfile: identity and capabilities
- AgentTaskContract: attachable missions
- SelfReflection: feedback-based correction
- RemoteSync: distributed agent pings
- DNAFork: agent evolution and cloning
"""

from typing import Callable, List, Dict, Any
import requests
import copy

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


# Example prebuilt agents
ValidatorElf = AgentProfile(
    "Validator Elf",
    traits=["precise", "rule-based"],
    powers=["audit_rfc", "verify_pr_integrity"]
)

DreamWeaver = AgentProfile(
    "DreamWeaver",
    traits=["creative", "introspective"],
    powers=["generate_summary", "draft_proposal", "simulate_impact"]
)


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


# Ready to be imported in protocols/__init__.py or wired into internal_protocol.py
