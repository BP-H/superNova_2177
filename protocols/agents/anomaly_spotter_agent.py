# protocols/anomaly_spotter_agent.py

"""AnomalySpotterAgent detects suspicious patterns in metrics.

The agent consumes streams of numerical data or network notes and
flags anomalies before they propagate into the validation pipeline.
It can optionally leverage an ``llm_backend`` callable for additional
analysis of metric context or textual notes.
"""

import logging
from statistics import mean, stdev
from typing import List

from protocols.core.internal_protocol import InternalAgentProtocol

logger = logging.getLogger("AnomalySpotterAgent")


class AnomalySpotterAgent(InternalAgentProtocol):
    """Analyze metrics to preemptively surface unusual activity.

    Parameters
    ----------
    llm_backend : callable, optional
        Optional function used for deeper metric inspection.
    """

    def __init__(self, llm_backend=None) -> None:
        super().__init__()
        self.name = "AnomalySpotter"
        self.llm_backend = llm_backend
        self.threshold = 2.0
        self.receive("DATA_METRICS", self.inspect_data)

    def inspect_data(self, payload: dict) -> dict:
        """Return anomaly information for provided metrics."""

        values: List[float] = payload.get("metrics", [])
        notes = payload.get("notes", "")

        if self.llm_backend:
            notes = self.llm_backend(notes or str(values))

        if len(values) < 2:
            return {"flagged": False, "details": "insufficient data"}

        avg = mean(values)
        dev = stdev(values)
        outliers = [v for v in values if dev and abs(v - avg) / dev > self.threshold]

        flagged = bool(outliers)
        suspicious_keywords = ["attack", "breach", "malware"]
        if any(word in notes.lower() for word in suspicious_keywords):
            flagged = True

        result = {
            "mean": avg,
            "stdev": dev,
            "outliers": outliers,
            "flagged": flagged,
        }
        logger.info(f"[AnomalySpotter] result: {result}")
        return result
