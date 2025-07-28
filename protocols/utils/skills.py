from typing import Callable, Dict

from ..core.base import InternalAgentProtocol

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

class AgentNegotiation:
    @staticmethod
    def propose_delegation(from_agent, to_agent, task: str, payload: dict):
        if to_agent.can(task):
            from_agent.send("DELEGATE_PROPOSAL", {"to": to_agent.name, "task": task})
            return to_agent.process_event({"event": task, "payload": payload})
        return {"error": f"{to_agent.name} can't handle task '{task}'"}

class FatigueMemoryMixin:
    def __init__(self):
        from collections import defaultdict
        import time
        self.task_count = defaultdict(int)
        self.last_reset = time.time()

    def fatigue_score(self, task: str) -> float:
        import time
        elapsed = time.time() - self.last_reset
        base = self.task_count[task]
        decay = max(1.0 - (elapsed / 300), 0.1)
        return min(base * decay, 1.0)

    def register_task(self, task: str):
        self.task_count[task] += 1

class ProbabilisticBeliefSystem:
    def __init__(self):
        from collections import defaultdict
        self.beliefs = defaultdict(lambda: 0.5)

    def update_belief(self, key: str, evidence: float):
        prior = self.beliefs[key]
        self.beliefs[key] = (prior + evidence) / 2

    def belief(self, key: str) -> float:
        return self.beliefs[key]

class IntrospectiveMixin:
    def export_reasoning(self) -> dict:
        return {
            "name": self.name,
            "memory": self.memory,
            "recent_events": self.inbox[-5:],
            "handlers": list(self.hooks.keys()),
        }
