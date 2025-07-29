# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards
import pytest

from validator_reputation_tracker import (
    update_validator_reputations,
    load_validator_profiles,
)
from db_models import ValidatorReputation


def test_semantic_contradiction_penalty():
    vals_good = [
        {"validator_id": "v1", "score": 0.5, "note": "supports"},
        {"validator_id": "v1", "score": 0.5, "note": "agrees"},
    ]
    good_rep = update_validator_reputations(vals_good)["reputations"]["v1"]

    vals_bad = [
        {"validator_id": "v2", "score": 0.5, "note": "supports"},
        {"validator_id": "v2", "score": 0.5, "note": "I refute this"},
    ]
    bad_rep = update_validator_reputations(vals_bad)["reputations"]["v2"]

    assert bad_rep < good_rep


def test_diversity_tracking():
    vals = [
        {"validator_id": "a", "score": 0.6, "specialty": "s1", "affiliation": "x"},
        {"validator_id": "a", "score": 0.6, "specialty": "s1", "affiliation": "x"},
        {"validator_id": "b", "score": 0.6, "specialty": "s2", "affiliation": "x"},
        {"validator_id": "b", "score": 0.6, "specialty": "s2", "affiliation": "x"},
        {"validator_id": "c", "score": 0.6, "specialty": "s1", "affiliation": "y"},
        {"validator_id": "c", "score": 0.6, "specialty": "s1", "affiliation": "y"},
    ]
    res = update_validator_reputations(vals)
    div = res["diversity"]
    assert div["unique_specialties"] == 2
    assert div["unique_affiliations"] == 2
    assert div["validator_count"] == 3


def test_persistence_with_profiles(test_db):
    vals = [
        {"validator_id": "p1", "score": 0.8, "specialty": "astro", "affiliation": "uni"},
        {"validator_id": "p1", "score": 0.9, "specialty": "astro", "affiliation": "uni"},
    ]
    result = update_validator_reputations(vals, db=test_db)

    # reputations persisted
    rows = {r.validator_id: r.reputation for r in test_db.query(ValidatorReputation).all()}
    assert rows == result["reputations"]

    profiles = load_validator_profiles(test_db)
    assert profiles["p1"]["specialty"] == "astro"
    assert profiles["p1"]["affiliation"] == "uni"
