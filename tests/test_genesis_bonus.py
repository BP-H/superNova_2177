import types
import datetime
import threading
from decimal import Decimal

import agent_core
from scientific_utils import calculate_genesis_bonus_decay, safe_decimal

# Provide implementations used by the agent
agent_core.calculate_genesis_bonus_decay = calculate_genesis_bonus_decay
agent_core.safe_decimal = safe_decimal

class DummyUser:
    def __init__(self, name, is_genesis, species, config):
        self.name = name
        self.is_genesis = is_genesis
        self.species = species
        self.karma = Decimal("0")
        self.harmony_score = Decimal("0")
        self.join_time = ""
        self.consent = True
        self.lock = threading.RLock()

    @classmethod
    def from_dict(cls, data, config):
        obj = cls(
            data["name"], data.get("is_genesis", False), data.get("species", "human"), config
        )
        obj.karma = Decimal(str(data.get("karma", "0")))
        obj.harmony_score = Decimal(str(data.get("harmony_score", "0")))
        obj.join_time = data.get("join_time", "")
        obj.consent = data.get("consent", True)
        return obj

    def to_dict(self):
        return {
            "name": self.name,
            "is_genesis": self.is_genesis,
            "species": self.species,
            "karma": str(self.karma),
            "harmony_score": str(self.harmony_score),
            "join_time": self.join_time,
            "consent": self.consent,
        }

agent_core.User = DummyUser

class DummyStorage:
    def __init__(self, users, proposals):
        self.users = users
        self.proposals = proposals

    def get_all_users(self):
        return list(self.users.values())

    def set_user(self, name, data):
        self.users[name] = data

    def get_proposal(self, pid):
        return self.proposals.get(pid)

class DummyConfig:
    DAILY_DECAY = Decimal("0.99")
    GENESIS_BONUS_DECAY_YEARS = 4
    SPECIES = ["human"]


def test_genesis_decay_with_z_suffix():
    join_time = "2023-01-01T00:00:00Z"
    users = {
        "alice": {
            "name": "alice",
            "is_genesis": True,
            "species": "human",
            "karma": "100",
            "join_time": join_time,
            "harmony_score": "1",
            "consent": True,
        }
    }
    proposals = {
        "p1": {
            "proposal_id": "p1",
            "votes": {"alice": "yes"},
            "status": "open",
            "voting_deadline": join_time,
        }
    }
    storage = DummyStorage(users, proposals)
    dummy = types.SimpleNamespace(storage=storage, config=DummyConfig())

    agent_core.RemixAgent._apply_DAILY_DECAY(dummy, {"event": "DAILY_DECAY"})

    dt = datetime.datetime.fromisoformat(join_time.replace("Z", "+00:00"))
    expected = Decimal("100") * DummyConfig.DAILY_DECAY * calculate_genesis_bonus_decay(
        dt, DummyConfig.GENESIS_BONUS_DECAY_YEARS
    )
    actual = Decimal(storage.users["alice"]["karma"])
    assert abs(actual - expected) < Decimal("1e-6")

    result = agent_core.RemixAgent._tally_proposal(dummy, "p1")
    assert result["yes"] > Decimal("0")
    assert result["quorum"] > Decimal("0")
