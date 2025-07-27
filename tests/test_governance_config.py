import logging
import sys
import builtins
import pytest

from governance_config import calculate_entropy_divergence
from superNova_2177 import Config


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
