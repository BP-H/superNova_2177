import logging
import sys
import builtins
import pytest

from governance_config import calculate_entropy_divergence, quantum_consensus, basis
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


def test_quantum_consensus_entanglement_factor():
    if basis is None:
        pytest.skip("qutip not installed")
    votes = [True, True]
    baseline = quantum_consensus(votes)
    entangled = quantum_consensus(votes, 1.0)
    assert entangled != pytest.approx(baseline)
    assert 0.0 <= entangled <= 1.0


def test_quantum_consensus_entanglement_matrix():
    if basis is None:
        pytest.skip("qutip not installed")
    votes = [True, False, True]
    matrix = [
        [0.0, 1.0, 0.0],
        [1.0, 0.0, 0.0],
        [0.0, 0.0, 0.0],
    ]
    result = quantum_consensus(votes, matrix)
    assert 0.0 <= result <= 1.0
