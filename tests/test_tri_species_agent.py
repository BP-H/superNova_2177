import sys
import types
from decimal import Decimal
import importlib
import pytest

if "superNova_2177" in sys.modules:
    stub = sys.modules["superNova_2177"]
else:
    stub = types.ModuleType("superNova_2177")
    sys.modules["superNova_2177"] = stub

if not hasattr(stub, "RemixAgent"):
    stub.RemixAgent = type("RemixAgent", (), {"fork_badges": {}})
if not hasattr(stub, "Config"):
    stub.Config = type("Config", (), {"SPECIES": ["human", "ai", "company"]})

ImmutableTriSpeciesAgent = importlib.import_module(
    "immutable_tri_species_adjust"
).ImmutableTriSpeciesAgent


class DummyStorage:
    def __init__(self):
        self.proposals = {}
        self.users = {}

    def get_proposal(self, pid):
        return self.proposals.get(pid)

    def set_proposal(self, pid, data):
        self.proposals[pid] = data

    def get_user(self, uid):
        return self.users.get(uid)

    def set_user(self, uid, data):
        self.users[uid] = data


class AgentWrapper(ImmutableTriSpeciesAgent):
    def __init__(self, storage):
        self.storage = storage


@pytest.fixture
def storage():
    return DummyStorage()


@pytest.fixture
def agent(storage):
    return AgentWrapper(storage)


@pytest.fixture
def add_voters(storage):
    def _add(voters):
        for name, species in voters.items():
            storage.set_user(name, {"species": species, "karma": 1})
    return _add


def test_dynamic_threshold_levels(agent):
    assert agent._get_dynamic_threshold(10, True, Decimal("0.8")) == Decimal("0.9")
    assert agent._get_dynamic_threshold(30, True, Decimal("0.8")) == Decimal("0.92")
    assert agent._get_dynamic_threshold(60, True, Decimal("0.8")) == Decimal("0.95")
    assert agent._get_dynamic_threshold(5, False, Decimal("0.8")) == Decimal("0.5")


def test_constitutional_requires_all_species(agent, storage, add_voters):
    storage.set_proposal("p1", {"type": "constitutional", "description": "update"})
    add_voters({"h1": "human", "a1": "ai"})
    agent._apply_VOTE_PROPOSAL({"proposal_id": "p1", "voter": "h1", "vote": "yes"})
    agent._apply_VOTE_PROPOSAL({"proposal_id": "p1", "voter": "a1", "vote": "yes"})
    proposal = storage.get_proposal("p1")
    assert proposal.get("status") != "passed"


def test_single_species_blocked_with_many_voters(agent, storage, add_voters):
    storage.set_proposal("p2", {"description": "regular"})
    voters = {f"h{i}": "human" for i in range(1, 12)}
    add_voters(voters)
    votes = ["no", "yes", "yes"] + ["no"] * 8
    for voter, vote in zip(voters, votes):
        agent._apply_VOTE_PROPOSAL({"proposal_id": "p2", "voter": voter, "vote": vote})
    proposal = storage.get_proposal("p2")
    assert proposal.get("status") == "open"
    assert len(proposal["votes"]["human"]) == 11
