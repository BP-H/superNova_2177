import pytest
from diversity_analyzer import compute_diversity_score


def test_compute_diversity_score_basic():
    vals = [
        {"validator_id": "a", "specialty": "x", "affiliation": "u"},
        {"validator_id": "b", "specialty": "y", "affiliation": "u"},
    ]
    result = compute_diversity_score(vals)
    assert 0.0 <= result["diversity_score"] <= 1.0
    assert result["counts"]["unique_validators"] == 2
