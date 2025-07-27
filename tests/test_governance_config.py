import logging
import math

from governance_config import calculate_entropy_divergence
from superNova_2177 import Config


def test_calculate_entropy_divergence_zero():
    cfg = {"ROOT_INITIAL_VALUE": Config.ROOT_INITIAL_VALUE}
    assert calculate_entropy_divergence(cfg) == 0.0


def test_calculate_entropy_divergence_invalid_value_logs(caplog):
    cfg = {
        "ROOT_INITIAL_VALUE": "bad",
        "TREASURY_SHARE": "0.5",
    }
    with caplog.at_level(logging.DEBUG):
        result = calculate_entropy_divergence(cfg)
    assert math.isclose(result, abs(float(cfg["TREASURY_SHARE"]) - float(Config.TREASURY_SHARE)))
    assert any("Skipping non-numeric value ROOT_INITIAL_VALUE" in rec.message for rec in caplog.records)


def test_calculate_entropy_divergence_type_error():
    try:
        calculate_entropy_divergence({}, base=object())
    except TypeError:
        pass
    else:
        assert False, "TypeError not raised"
