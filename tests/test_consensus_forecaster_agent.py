from consensus_forecaster_agent import forecast_consensus_trend


def test_forecast_basic_increasing():
    vals = [
        {"score": 0.5, "timestamp": "2025-01-01T00:00:00Z"},
        {"score": 0.6, "timestamp": "2025-01-02T00:00:00Z"},
        {"score": 0.7, "timestamp": "2025-01-03T00:00:00Z"},
    ]
    result = forecast_consensus_trend(vals)
    assert result["trend"] == "increasing"
    assert result["forecast_score"] >= 0.7


def test_risk_modifier_applied():
    vals = [
        {"score": 0.6, "timestamp": "2025-01-01T00:00:00Z"},
        {"score": 0.6, "timestamp": "2025-01-02T00:00:00Z"},
    ]
    result = forecast_consensus_trend(vals, {"overall_risk_score": 0.5})
    assert result["risk_modifier"] < 0
    assert result["forecast_score"] <= 0.6


def test_no_data():
    res = forecast_consensus_trend([])
    assert res["flags"] == ["no_data"]
