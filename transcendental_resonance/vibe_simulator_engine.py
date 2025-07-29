from __future__ import annotations

"""Quantum-inspired simulator predicting VibeNode futures."""

import asyncio
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

try:  # pragma: no cover - allow import without NiceGUI
    from nicegui import ui
    from nicegui.element import Element
except Exception:  # pragma: no cover - fallback stubs for testing

    class Element:  # type: ignore
        pass

    class _DummyUI:
        def notify(self, *args: Any, **kwargs: Any) -> Element:  # noqa: D401
            return Element()

    ui = _DummyUI()  # type: ignore

from quantum_sim import QuantumContext

try:
    from transcendental_resonance_frontend.src.utils.api import (
        listen_ws,
        on_ws_status_change,
    )
    from transcendental_resonance_frontend.src.utils.error_overlay import ErrorOverlay
except Exception:  # pragma: no cover - fallback when frontend not available

    def listen_ws(*_args: Any, **_kwargs: Any) -> asyncio.Task:
        async def dummy() -> None:
            return None

        return asyncio.create_task(dummy())

    def on_ws_status_change(*_args: Any, **_kwargs: Any) -> None:
        return None

    class ErrorOverlay:  # type: ignore
        def show(self, _msg: str) -> None:
            pass

        def hide(self) -> None:
            pass


@dataclass
class NarrativeNode:
    """Simple node within the quantum narrative tree."""

    name: str
    probability: float = 1.0
    children: list["NarrativeNode"] = field(default_factory=list)


@dataclass
class SimulatedOutcome:
    """Representation of a speculative future branch."""

    title: str
    description: str
    mood: str
    probability: float
    emoji_tags: List[str]


class VibeSimulatorEngine:
    """Predict future VibeNode trajectories using quantum heuristics."""

    def __init__(
        self,
        error_overlay: Optional[ErrorOverlay] = None,
        *,
        include_emoji: bool = True,
    ) -> None:
        self.qc = QuantumContext(simulate=True)
        self.error_overlay = error_overlay or ErrorOverlay()
        self.root = NarrativeNode("root")
        self.ws_connected = False
        self.include_emoji = include_emoji
        on_ws_status_change(self._on_ws_status_change)
        self._listen_task: Optional[asyncio.Task] = None
        self.last_meta: Dict[str, Any] = {}

    def start(self) -> None:
        """Begin listening for WebSocket frame metadata."""

        if self._listen_task is None:
            self._listen_task = listen_ws(self._handle_ws_event)

    async def _on_ws_status_change(self, status: str) -> None:
        self.ws_connected = status == "connected"

    async def _handle_ws_event(self, event: Dict[str, Any]) -> None:
        if event.get("type") == "frame_meta":
            self.last_meta = event.get("meta", {})

    # ------------------------------------------------------------------
    def _show_feedback(self, text: str, *, warn: bool = False) -> None:
        color = "warning" if warn else "positive"
        ui.notify(text, color=color)

    def _display_risk(self, risk: float) -> None:
        if risk > 0.7:
            self.error_overlay.show(f"Divergence risk {risk:.0%}")
        else:
            self.error_overlay.hide()

    def generate_possible_outcomes(self, event: str) -> List[SimulatedOutcome]:
        """Create optimistic, chaotic and dystopian outcome branches."""
        base = self.qc.measure_superposition(0.5)["value"]
        optimistic_prob = min(1.0, base + 0.25)
        chaotic_prob = max(0.0, base * 0.5)
        dystopian_prob = max(0.0, 1 - optimistic_prob)

        outcomes = [
            SimulatedOutcome(
                title="Optimistic",
                description=f"In a bright timeline, {event} leads to communal bliss and free snacks for everyone.",
                mood="uplifting",
                probability=optimistic_prob,
                emoji_tags=["🌈", "✨", "🥳"],
            ),
            SimulatedOutcome(
                title="Chaotic",
                description=f"Chaos theory kicks in as {event} spirals into meme-worthy unpredictability.",
                mood="chaotic",
                probability=chaotic_prob,
                emoji_tags=["🤪", "🌀", "🎲"],
            ),
            SimulatedOutcome(
                title="Dystopian",
                description=f"A darker path where {event} ushers in the robo-overlords' soggy Monday.",
                mood="dystopian",
                probability=dystopian_prob,
                emoji_tags=["😱", "🤖", "🌧️"],
            ),
        ]
        return outcomes

    def run_prediction(
        self,
        event: str,
        *,
        face: str | None = None,
        emotion: str | None = None,
        timestamp: float | None = None,
    ) -> str:
        """Return a markdown summary of predicted futures."""

        prob = self.qc.measure_superposition(0.5)["value"]
        node = NarrativeNode(event, probability=prob)
        self.root.children.append(node)

        risk = 1 - prob
        self._display_risk(risk)
        if prob < 0.3:
            self._show_feedback("your vibe may collapse in 3 days", warn=True)
        else:
            self._show_feedback("vibe stable")

        outcomes = self.generate_possible_outcomes(event)

        lines = [
            "## Predicted Future",
            f"- Event: {event}",
            f"- Probability: {prob:.2%}",
        ]
        if face:
            lines.append(f"- Face: {face}")
        if emotion:
            lines.append(f"- Emotion: {emotion}")
        if timestamp is not None:
            lines.append(f"- Timestamp: {timestamp}")

        lines.append("")
        for outcome in outcomes:
            emojis = " ".join(outcome.emoji_tags) if self.include_emoji else ""
            lines.extend(
                [
                    f"### {outcome.title} {emojis}",
                    f"- Probability: {outcome.probability:.2%}",
                    f"- Mood: {outcome.mood}",
                    f"- {outcome.description}",
                    "",
                ]
            )

        lines.append(
            "🌀 Quantum Disclaimer: Simulations may not reflect actual vibe conditions. Use caution in all dimensions."
        )

        return "\n".join(lines)


__all__ = ["VibeSimulatorEngine", "NarrativeNode", "SimulatedOutcome"]
