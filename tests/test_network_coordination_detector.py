# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards
import pytest
from network.network_coordination_detector import (
    calculate_sophisticated_risk_score,
    analyze_coordination_patterns,
    detect_semantic_coordination,
)


def test_calculate_sophisticated_risk_score_basic():
    # Example with moderate flag counts and validator set
    score = calculate_sophisticated_risk_score(
        temporal_flags=2,
        score_flags=3,
        semantic_flags=1,
        total_validators=5,
    )
    assert pytest.approx(0.305, rel=1e-2) == score


def test_calculate_sophisticated_risk_score_extremes():
    # Zero validators should yield zero risk
    assert calculate_sophisticated_risk_score(1, 1, 1, 0) == 0.0

    # Extremely high flags should cap the score at 1.0
    high = calculate_sophisticated_risk_score(20, 20, 20, 1)
    assert 0.99 <= high <= 1.0


def test_analyze_coordination_patterns_empty():
    result = analyze_coordination_patterns([])
    assert result["overall_risk_score"] == 0.0
    assert result["flags"] == ["no_validations"]
    assert result["coordination_clusters"] == []
    assert result["graph"]["edges"] == []
    assert result["risk_breakdown"] == {"temporal": 0, "score": 0, "semantic": 0}


def test_analyze_coordination_patterns_detects_clusters():
    base_ts = "2025-01-01T00:00:00Z"
    # Create four hypotheses with nearly identical validations from two validators
    validations = []
    for i in range(4):
        ts = f"2025-01-01T00:0{i}:00Z"
        note = "the quick brown fox jumps over the lazy dog"
        validations.append({
            "validator_id": "v1",
            "hypothesis_id": f"h{i}",
            "score": 0.8,
            "timestamp": ts,
            "note": note,
        })
        validations.append({
            "validator_id": "v2",
            "hypothesis_id": f"h{i}",
            "score": 0.8,
            "timestamp": ts,
            "note": note,
        })

    result = analyze_coordination_patterns(validations)

    # Expect one flag from each detector
    assert result["risk_breakdown"] == {"temporal": 1, "score": 1, "semantic": 1}
    assert len(result["flags"]) == 3

    clusters = result["coordination_clusters"]
    assert clusters["temporal"] and clusters["score"] and clusters["semantic"]

    # Graph should include both validators
    assert set(result["graph"]["nodes"]) == {"v1", "v2"}
    assert result["graph"]["edges"]

    # Overall risk score is rounded to three decimals
    assert result["overall_risk_score"] == pytest.approx(0.32, abs=0.01)


def test_detect_semantic_coordination_embeddings():
    validations = [
        {
            "validator_id": "v1",
            "hypothesis_id": "h1",
            "score": 0.8,
            "timestamp": "2025-01-01T00:00:00Z",
            "note": "the quick brown fox jumps over the lazy dog",
        },
        {
            "validator_id": "v2",
            "hypothesis_id": "h2",
            "score": 0.8,
            "timestamp": "2025-01-01T00:01:00Z",
            "note": "the quick brown fox leaps over the lazy dog",
        },
    ]

    result = detect_semantic_coordination(validations)
    assert result["semantic_clusters"]
    assert result["semantic_clusters"][0]["similarity_score"] >= 0.8


def test_detect_semantic_coordination_no_numpy_sklearn(monkeypatch):
    validations = [
        {
            "validator_id": "v1",
            "hypothesis_id": "h1",
            "score": 0.8,
            "timestamp": "2025-01-01T00:00:00Z",
            "note": "the quick brown fox jumps over the lazy dog",
        },
        {
            "validator_id": "v2",
            "hypothesis_id": "h2",
            "score": 0.8,
            "timestamp": "2025-01-01T00:01:00Z",
            "note": "the quick brown fox leaps over the lazy dog",
        },
    ]

    import builtins, sys

    original_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name.startswith("sentence_transformers") or name.startswith("sklearn") or name == "numpy":
            raise ImportError("missing")
        return original_import(name, *args, **kwargs)

    for mod in ["sentence_transformers", "sklearn", "numpy"]:
        monkeypatch.delitem(sys.modules, mod, raising=False)

    monkeypatch.setattr(builtins, "__import__", fake_import)

    result = detect_semantic_coordination(validations)
    assert result["semantic_clusters"]
    assert result["semantic_clusters"][0]["similarity_score"] >= 0.8


def test_detect_semantic_coordination_sentence_transformer_failure(monkeypatch):
    validations = [
        {
            "validator_id": "v1",
            "hypothesis_id": "h1",
            "score": 0.8,
            "timestamp": "2025-01-01T00:00:00Z",
            "note": "the quick brown fox jumps over the lazy dog",
        },
        {
            "validator_id": "v2",
            "hypothesis_id": "h2",
            "score": 0.8,
            "timestamp": "2025-01-01T00:01:00Z",
            "note": "the quick brown fox leaps over the lazy dog",
        },
    ]

    import types, sys

    class FailingST:
        def __init__(self, *args, **kwargs):
            raise RuntimeError("no model")

    fake_module = types.SimpleNamespace(SentenceTransformer=FailingST)
    monkeypatch.setitem(sys.modules, "sentence_transformers", fake_module)

    result = detect_semantic_coordination(validations)
    assert result["semantic_clusters"]
    assert result["semantic_clusters"][0]["similarity_score"] >= 0.8

