"""Consensus Forecaster Agent.

Analyzes historical validator scores and optional network
coordination metrics to forecast short-term consensus trends.
"""

from __future__ import annotations

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

try:
    import numpy as np  # type: ignore
except Exception:  # pragma: no cover - fallback minimal implementation
    class _NP:
        def array(self, x):
            return list(x)

        def polyfit(self, x, y, deg):
            # simple linear regression fallback
            n = len(x)
            if n == 0:
                return 0.0, 0.0
            mean_x = sum(x) / n
            mean_y = sum(y) / n
            num = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, y))
            den = sum((xi - mean_x) ** 2 for xi in x) or 1.0
            slope = num / den
            intercept = mean_y - slope * mean_x
            return slope, intercept

        def clip(self, a, a_min, a_max):
            return max(a_min, min(a_max, a))

    np = _NP()  # type: ignore

logger = logging.getLogger("superNova_2177.forecaster")
logger.propagate = False


class Config:
    """Default forecasting configuration."""

    TREND_THRESHOLD = 0.001
    RISK_MODIFIER = 0.2


def forecast_consensus_trend(
    validations: List[Dict[str, Any]],
    network_analysis: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Forecast consensus score based on validator history.

    Parameters
    ----------
    validations:
        List of validation records with ``score`` and ``timestamp`` fields.
    network_analysis:
        Optional output from ``analyze_coordination_patterns``. If provided,
        the overall risk score will adjust the forecast downward.

    Returns
    -------
    Dict[str, Any]
        Dictionary containing ``forecast_score`` (0.0-1.0) and ``trend``.
    """

    if not validations:
        return {"forecast_score": 0.0, "trend": "stable", "flags": ["no_data"]}

    times = []
    scores = []
    for v in validations:
        ts = v.get("timestamp")
        if not ts:
            continue
        try:
            dt = datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
        except Exception:  # pragma: no cover - skip malformed timestamps
            continue
        times.append(dt.timestamp())
        try:
            scores.append(float(v.get("score", 0.5)))
        except Exception:
            scores.append(0.5)

    if len(times) == 0:
        return {"forecast_score": 0.0, "trend": "stable", "flags": ["no_valid_timestamps"]}

    if len(times) < 2:
        forecast = scores[-1]
        return {
            "forecast_score": round(np.clip(forecast, 0.0, 1.0), 3),
            "trend": "stable",
            "flags": ["insufficient_history"],
        }

    # Normalize time axis using simple sequential indices to avoid
    # extremely small slope values when timestamps are far apart.
    norm_times = list(range(len(times)))
    slope, intercept = np.polyfit(norm_times, scores, 1)
    next_time = norm_times[-1] + 1
    forecast = slope * next_time + intercept

    trend = "stable"
    if slope > Config.TREND_THRESHOLD:
        trend = "increasing"
    elif slope < -Config.TREND_THRESHOLD:
        trend = "decreasing"

    risk_modifier = 0.0
    if network_analysis:
        risk = float(network_analysis.get("overall_risk_score", 0.0))
        risk_modifier = -Config.RISK_MODIFIER * risk
        forecast += risk_modifier

    forecast = np.clip(forecast, 0.0, 1.0)

    return {
        "forecast_score": round(float(forecast), 3),
        "trend": trend,
        "risk_modifier": round(float(risk_modifier), 3),
    }

