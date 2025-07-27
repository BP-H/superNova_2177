import logging
import sys
import builtins
import pytest

from governance_config import calculate_entropy_divergence, karma_percentile_cutoff
from superNova_2177 import Config
from db_models import Harmonizer


def test_calculate_entropy_divergence_warns_for_invalid(caplog):
    cfg = {"TREASURY_SHARE": "0.5", "ROOT_INITIAL_VALUE": "bad"}
    with caplog.at_level(logging.WARNING):
        result = calculate_entropy_divergence(cfg, base=Config)
    expected = abs(float(cfg["TREASURY_SHARE"]) - float(Config.TREASURY_SHARE))
    assert result == pytest.approx(expected)
    assert any("ROOT_INITIAL_VALUE" in rec.message for rec in caplog.records)


def test_calculate_entropy_divergence_import_error(monkeypatch):
    original_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "superNova_2177":
            raise ImportError("missing")
        return original_import(name, *args, **kwargs)

    monkeypatch.delitem(sys.modules, "superNova_2177", raising=False)
    monkeypatch.setattr(builtins, "__import__", fake_import)
    with pytest.raises(ImportError):
        calculate_entropy_divergence({})


def test_karma_percentile_cutoff_edge_cases(test_db):
    users = [
        Harmonizer(
            username=f"u{i}",
            email=f"{i}@example.com",
            hashed_password="x",
            karma_score=score,
        )
        for i, score in enumerate([10.0, 20.0, 30.0])
    ]
    test_db.add_all(users)
    test_db.commit()

    high_cutoff = karma_percentile_cutoff(0.0, db=test_db)
    low_cutoff = karma_percentile_cutoff(1.0, db=test_db)

    assert high_cutoff == pytest.approx(30.0)
    assert low_cutoff == pytest.approx(10.0)
