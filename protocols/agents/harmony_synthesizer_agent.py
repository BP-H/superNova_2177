"""HarmonySynthesizerAgent
==========================

Converts aggregated system metrics into short MIDI snippets using
``resonance_music.generate_midi_from_metrics``.

This agent can subscribe to a metrics feed or accept metrics directly
through events. The resulting MIDI bytes are emitted on the
``MIDI_CREATED`` topic for downstream consumers.
"""

from typing import Callable, Dict, Any

from protocols.core.internal_protocol import InternalAgentProtocol
from resonance_music import generate_midi_from_metrics


class HarmonySynthesizerAgent(InternalAgentProtocol):
    """Translate metrics into MIDI using a provided aggregator."""

    def __init__(self, metrics_provider: Callable[[], Dict[str, float]] | None = None) -> None:
        super().__init__()
        self.name = "HarmonySynthesizer"
        self.metrics_provider = metrics_provider
        self.receive("GENERATE_MIDI", self.handle_generate)

    def handle_generate(self, payload: Dict[str, Any] | None = None) -> bytes:
        """Return MIDI bytes for provided or aggregated metrics."""

        payload = payload or {}
        metrics = payload.get("metrics")
        if metrics is None and self.metrics_provider:
            metrics = self.metrics_provider()
        if not isinstance(metrics, dict):
            metrics = {}
        midi = generate_midi_from_metrics(metrics)
        self.send("MIDI_CREATED", {"midi": midi, "metrics": metrics})
        return midi
