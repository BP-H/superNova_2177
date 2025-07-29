# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards
import pytest

from protocols.utils.negotiation import AgentNegotiation
from protocols.utils.skills import EmbodiedAgent
from protocols.core.profiles import AgentProfile


class ProfiledAgent(EmbodiedAgent):
    def __init__(self, name: str, profile: AgentProfile):
        super().__init__(name)
        self.profile = profile

    def can(self, task: str) -> bool:  # pragma: no cover - simple passthrough
        return self.profile.can(task)


def test_propose_delegation_success():
    sender = EmbodiedAgent("sender")
    profile = AgentProfile("worker", traits=[], powers=["TASK"])
    worker = ProfiledAgent("worker", profile)

    worker.receive("TASK", lambda p: {"handled": p.get("x")})

    result = AgentNegotiation.propose_delegation(sender, worker, "TASK", {"x": 1})

    assert result == {"handled": 1}
    assert sender.inbox[-1]["topic"] == "DELEGATE_PROPOSAL"
    assert sender.inbox[-1]["payload"] == {"to": "worker", "task": "TASK"}


def test_propose_delegation_failure():
    sender = EmbodiedAgent("sender")
    profile = AgentProfile("worker", traits=[], powers=[])  # cannot handle TASK
    worker = ProfiledAgent("worker", profile)

    result = AgentNegotiation.propose_delegation(sender, worker, "TASK", {"x": 1})

    assert "error" in result
    assert sender.inbox == []
