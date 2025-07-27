import pytest
from diversity_analyzer import (
    compute_diversity_score,
    detect_semantic_contradictions,
    certify_validations,
)


def test_compute_diversity_score_with_types():
    vals = [
        {"validator_id": "a", "specialty": "x", "validator_type": "expert"},
        {"validator_id": "b", "specialty": "y", "validator_type": "community"},
        {"validator_id": "c", "specialty": "x", "validator_type": "expert"},
    ]
    result = compute_diversity_score(vals)
    assert result["counts"]["unique_validator_types"] == 2
    assert 0.0 <= result["diversity_score"] <= 1.0


def test_detect_semantic_contradictions():
    vals = [
        {"validator_id": "a", "note": "This method is valid"},
        {"validator_id": "b", "note": "I contradict this method is valid"},
    ]
    contradictions = detect_semantic_contradictions(vals)
    assert contradictions
    assert {"a", "b"} == set(contradictions[0]["validators"])


def test_certify_validations_enhanced_fields():
    vals = [
        {
            "validator_id": "a",
            "score": 0.8,
            "confidence": 0.8,
            "signal_strength": 0.7,
            "note": "This method is valid",
            "timestamp": "2025-01-01T00:00:00Z",
            "validator_type": "expert",
            "hypothesis_id": "h1",
        },
        {
            "validator_id": "b",
            "score": 0.2,
            "confidence": 0.4,
            "signal_strength": 0.3,
            "note": "I contradict this method is valid",
            "timestamp": "2025-01-02T00:00:00Z",
            "validator_type": "community",
            "hypothesis_id": "h2",
        },
    ]
    result = certify_validations(vals)
    assert "reputations" in result
    assert "temporal_consistency" in result
    assert "cross_validation" in result
    assert result["semantic_contradictions"]
