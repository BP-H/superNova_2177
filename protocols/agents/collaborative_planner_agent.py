"""CollaborativePlannerAgent orchestrates delegation among protocol agents."""

from typing import Dict

from protocols.core.internal_protocol import InternalAgentProtocol
from protocols.core.profiles import AgentProfile
from protocols.utils.negotiation import AgentNegotiation


class CollaborativePlannerAgent(InternalAgentProtocol):
    """Coordinates tasks and delegates them to capable agents."""

    def __init__(self, registry: Dict[str, InternalAgentProtocol], profiles: Dict[str, AgentProfile]):
        super().__init__()
        self.name = "CollaborativePlanner"
        self.registry = registry
        self.profiles = profiles
        self.receive("PLAN_TASK", self.plan_and_delegate)

    def plan_and_delegate(self, payload: Dict) -> Dict:
        task = payload.get("task")
        data = payload.get("data", {})

        for agent_name, profile in self.profiles.items():
            if profile.can(task) and agent_name in self.registry:
                agent = self.registry[agent_name]
                result = AgentNegotiation.propose_delegation(self, agent, task, data)
                return {
                    "delegated_to": agent_name,
                    "result": result,
                }

        return {"error": f"No agent available for task '{task}'"}
