import datetime
import types
from unittest.mock import MagicMock

import pytest

from introspection.introspection_pipeline import run_full_audit


def test_run_full_audit_missing_hypothesis(monkeypatch):
    """Gracefully handles unknown hypothesis IDs."""
    mock_db = MagicMock()
    import introspection.introspection_pipeline as ip
    monkeypatch.setattr(ip.ht, "_get_hypothesis_record", lambda db, hid: None, raising=False)

    result = run_full_audit("HYP_X", mock_db)

    assert result == {"error": "Hypothesis 'HYP_X' not found."}


def test_run_full_audit_no_valid_logs(monkeypatch):
    """Returns an error when no logs contain a causal audit ref."""
    mock_db = MagicMock()
    import introspection.introspection_pipeline as ip
    monkeypatch.setattr(
        ip.ht,
        "_get_hypothesis_record",
        lambda db, hid: {"text": "desc", "validation_log_ids": [1]},
        raising=False,
    )

    log = types.SimpleNamespace(
        id=1,
        timestamp=datetime.datetime.utcnow(),
        payload="{}",
    )
    mock_query = MagicMock()
    mock_query.filter.return_value.all.return_value = [log]
    mock_db.query.return_value = mock_query

    result = run_full_audit("HYP_X", mock_db)

    assert "No valid causal audit reference" in result["error"]


def test_run_full_audit_with_malformed_log(monkeypatch):
    """Ignores malformed logs and uses the latest valid one."""
    mock_db = MagicMock()
    import introspection.introspection_pipeline as ip
    monkeypatch.setattr(
        ip.ht,
        "_get_hypothesis_record",
        lambda db, hid: {"text": "desc", "validation_log_ids": [1, 2]},
        raising=False,
    )

    bad = types.SimpleNamespace(
        id=1,
        timestamp=datetime.datetime(2024, 1, 1),
        payload="{bad json}",
    )
    good = types.SimpleNamespace(
        id=2,
        timestamp=datetime.datetime(2024, 1, 2),
        payload='{"causal_audit_ref": "ref1"}',
    )
    mock_query = MagicMock()
    mock_query.filter.return_value.all.return_value = [bad, good]
    mock_db.query.return_value = mock_query

    calls = {}

    def fake_explain(hid, log_id, db):
        calls["explain"] = (hid, log_id, db)
        return {"summary": "ok", "risk_flags": []}

    def fake_summarize(hid, db):
        calls["bias"] = (hid, db)
        return {}

    def fake_trace(ref, db):
        calls["trace"] = (ref, db)
        return []

    def fake_bundle(**kwargs):
        calls["bundle"] = kwargs
        return {"bundle": True}

    monkeypatch.setattr(
        "introspection.introspection_pipeline.explain_validation_reasoning",
        fake_explain,
    )
    monkeypatch.setattr(
        "introspection.introspection_pipeline.summarize_bias_impact_on",
        fake_summarize,
    )
    monkeypatch.setattr(
        "introspection.introspection_pipeline.trace_causal_chain",
        fake_trace,
    )
    monkeypatch.setattr(
        "introspection.introspection_pipeline.generate_structured_audit_bundle",
        fake_bundle,
    )

    result = run_full_audit("HYP_X", mock_db)

    assert result == {"bundle": True}
    assert calls["explain"] == ("HYP_X", 2, mock_db)
    assert calls["trace"] == ("ref1", mock_db)
    assert calls["bundle"]["validation_id"] == 2
