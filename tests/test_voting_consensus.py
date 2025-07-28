import datetime
from datetime import UTC

from validators.strategies.voting_consensus_engine import (
    aggregate_validator_votes,
    VotingMethod,
)


def test_ranked_choice_basic():
    votes = [
        {"validator_id": "a", "ranking": ["x", "y", "z"]},
        {"validator_id": "b", "ranking": ["y", "x", "z"]},
        {"validator_id": "c", "ranking": ["y", "z", "x"]},
    ]
    reps = {"a": 1.0, "b": 1.0, "c": 1.0}
    result = aggregate_validator_votes(
        votes,
        method=VotingMethod.RANKED_CHOICE,
        reputations=reps,
        current_time=datetime.datetime.now(UTC),
    )
    assert result["consensus_decision"] == "y"
    assert result["vote_breakdown"]["method"] == "ranked_choice"


def test_quadratic_voting():
    votes = [
        {"validator_id": "a", "decision": "yes", "credits": 4},
        {"validator_id": "b", "decision": "no", "credits": 1},
        {"validator_id": "c", "decision": "yes", "credits": 1},
    ]
    reps = {"a": 1.0, "b": 1.0, "c": 1.0}
    result = aggregate_validator_votes(
        votes,
        method=VotingMethod.QUADRATIC,
        reputations=reps,
        current_time=datetime.datetime.now(UTC),
    )
    assert result["consensus_decision"] == "yes"
    assert result["vote_breakdown"]["method"] == "quadratic"


def test_delegation_support():
    votes = [
        {"validator_id": "a", "decision": "x"},
        {"validator_id": "b", "decision": "y"},
        {"validator_id": "c", "delegate_to": "a"},
        {"validator_id": "d", "delegate_to": "a"},
    ]
    reps = {"a": 1.0, "b": 1.0, "c": 1.0, "d": 1.0}
    result = aggregate_validator_votes(
        votes,
        method=VotingMethod.MAJORITY_RULE,
        reputations=reps,
        current_time=datetime.datetime.now(UTC),
    )
    assert result["consensus_decision"] == "x"


def test_time_decay_affects_outcome():
    now = datetime.datetime.now(UTC).replace(microsecond=0)
    old = (now - datetime.timedelta(days=60)).isoformat()
    votes = [
        {"validator_id": "a", "decision": "yes", "timestamp": old},
        {"validator_id": "b", "decision": "yes", "timestamp": old},
        {"validator_id": "c", "decision": "no", "timestamp": now.isoformat()},
    ]
    reps = {"a": 1.0, "b": 1.0, "c": 1.0}
    result = aggregate_validator_votes(
        votes,
        method=VotingMethod.MAJORITY_RULE,
        reputations=reps,
        current_time=now,
    )
    assert result["consensus_decision"] == "no"


def test_cross_validation_tracking():
    history = []
    now = datetime.datetime.now(UTC).replace(microsecond=0)
    reps = {"a": 1.0, "b": 1.0, "c": 1.0}
    votes1 = [
        {"validator_id": "a", "decision": "yes"},
        {"validator_id": "b", "decision": "yes"},
        {"validator_id": "c", "decision": "no"},
    ]
    aggregate_validator_votes(
        votes1,
        method=VotingMethod.MAJORITY_RULE,
        reputations=reps,
        current_time=now,
        cross_validation_history=history,
    )
    votes2 = [
        {"validator_id": "a", "decision": "no"},
        {"validator_id": "b", "decision": "no"},
        {"validator_id": "c", "decision": "no"},
    ]
    result = aggregate_validator_votes(
        votes2,
        method=VotingMethod.MAJORITY_RULE,
        reputations=reps,
        current_time=now,
        cross_validation_history=history,
    )
    assert result["cross_validation"]["history_size"] == 2
    assert result["cross_validation"]["consistency_score"] == 0.5