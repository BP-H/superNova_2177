# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards
import logging
from unittest.mock import Mock
import pytest

from protocols.agents.anomaly_spotter_agent import AnomalySpotterAgent


def test_inspect_data_no_anomalies(caplog):
    agent = AnomalySpotterAgent()
    metrics = [1, 1, 1, 1, 1, 1]
    with caplog.at_level(logging.INFO):
        result = agent.inspect_data({"metrics": metrics})
    assert result == {
        "mean": pytest.approx(1.0),
        "stdev": pytest.approx(0.0),
        "outliers": [],
        "flagged": False,
    }
    assert any("AnomalySpotter" in rec.message for rec in caplog.records)


def test_inspect_data_identifies_outliers(caplog):
    agent = AnomalySpotterAgent()
    metrics = [1, 1, 1, 1, 1, 10]
    with caplog.at_level(logging.INFO):
        result = agent.inspect_data({"metrics": metrics})
    assert result["flagged"] is True
    assert result["outliers"] == [10]
    assert pytest.approx(2.5) == result["mean"]
    assert pytest.approx(3.674, rel=1e-3) == result["stdev"]
    assert any("flagged" in rec.message for rec in caplog.records)


def test_llm_backend_called_and_flags_notes():
    backend = Mock(return_value="possible malware activity")
    agent = AnomalySpotterAgent(llm_backend=backend)
    metrics = [1, 1, 1, 1, 1, 1]
    result = agent.inspect_data({"metrics": metrics, "notes": ""})
    backend.assert_called_once()
    assert result["flagged"] is True
    assert result["outliers"] == []


def test_process_event_routes_and_returns():
    agent = AnomalySpotterAgent()
    metrics = [1, 2, 1, 1]
    result = agent.process_event({"event": "DATA_METRICS", "payload": {"metrics": metrics}})
    assert result["flagged"] is False
    assert result["outliers"] == []

