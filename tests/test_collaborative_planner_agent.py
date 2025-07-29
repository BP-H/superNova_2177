# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards
from protocols.agents.collaborative_planner_agent import CollaborativePlannerAgent
from protocols.core.profiles import AgentProfile
from protocols.core.internal_protocol import InternalAgentProtocol


class DummyAgent(InternalAgentProtocol):
    def __init__(self, name: str):
        super().__init__()
        self.name = name
        self.receive("do_it", self.do_it)

    def do_it(self, payload):
        return {"done": self.name}

    def can(self, task: str) -> bool:
        return task == "do_it"


def test_planner_delegates_to_capable_agent():
    agent_a = DummyAgent("A")
    profile_a = AgentProfile("A", traits=[], powers=["do_it"])

    registry = {"A": agent_a}
    profiles = {"A": profile_a}

    planner = CollaborativePlannerAgent(registry, profiles)
    result = planner.plan_and_delegate({"task": "do_it", "data": {}})

    assert result["delegated_to"] == "A"
    assert result["result"] == {"done": "A"}


def test_planner_handles_missing_agent():
    planner = CollaborativePlannerAgent({}, {})
    result = planner.plan_and_delegate({"task": "nothing", "data": {}})
    assert "error" in result

