# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards
"""Comedic quantum vibe simulation engine."""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable, List, Optional

from nicegui import ui
from websockets import WebSocketClientProtocol  # type: ignore

from transcendental_resonance_frontend.src.utils.error_overlay import ErrorOverlay
from realtime_comm.video_chat import FrameMetadata


@dataclass
class VibeNodePrediction:
    """Simple predicted path with probability."""

    path: str
    probability: float


@dataclass
class VibeSimulatorEngine:
    """Lightweight engine forecasting quantum narrative vibes."""

    error_overlay: ErrorOverlay
    narrative_tree: List[str] = field(
        default_factory=lambda: [
            "QuantumBloom",
            "FluxDivergence",
            "HarmonyCascade",
            "EchoCollapse",
        ]
    )
    ws_status: str = "disconnected"
    predictions: List[VibeNodePrediction] = field(default_factory=list)
    ws_subscribers: List[Callable[[str], None]] = field(default_factory=list)
    frame_subscribers: List[Callable[[FrameMetadata], None]] = field(default_factory=list)

    # ------------------------------------------------------------
    def subscribe_ws_status(self, callback: Callable[[str], None]) -> None:
        """Register callback for WebSocket status updates."""

        self.ws_subscribers.append(callback)

    def subscribe_frame_metadata(self, callback: Callable[[FrameMetadata], None]) -> None:
        """Register callback for frame metadata events."""

        self.frame_subscribers.append(callback)

    # ------------------------------------------------------------
    def update_ws_status(self, status: str) -> None:
        """Update connection status and notify subscribers."""

        self.ws_status = status
        for cb in list(self.ws_subscribers):
            cb(status)
        if status != "connected":
            self.error_overlay.show("Quantum link unstable! Divergence rising...")
        else:
            self.error_overlay.hide()

    def receive_frame_metadata(self, meta: FrameMetadata) -> None:
        """Notify subscribers with new frame metadata."""

        for cb in list(self.frame_subscribers):
            cb(meta)

    # ------------------------------------------------------------
    def run_prediction(
        self,
        *,
        event: str = "",
        face: str = "",
        emotion: str = "",
        timestamp: Optional[datetime] = None,
    ) -> str:
        """Predict a whimsical VibeNode path and return markdown summary."""

        timestamp = timestamp or datetime.utcnow()
        path = random.choice(self.narrative_tree)
        prob = random.random()
        self.predictions.append(VibeNodePrediction(path=path, probability=prob))

        risk = 1 - prob
        if risk > 0.7:
            self.error_overlay.show(
                f"Divergence imminent! Risk {risk:.2f}"  # comedic warning
            )

        summary = (
            f"### Quantum Vibe Forecast\n"
            f"*Event*: {event or 'none'}\n"
            f"*Face*: {face or 'neutral'}\n"
            f"*Emotion*: {emotion or 'neutral'}\n"
            f"*Timestamp*: {timestamp.isoformat()}\n"
            f"*Predicted Path*: **{path}**\n"
            f"*Resonance Probability*: **{prob:.2f}**\n"
        )
        ui.notify(f"Vibe trajectory: {path} ({prob:.2f})", color="primary")
        return summary


__all__ = ["VibeSimulatorEngine", "VibeNodePrediction"]
