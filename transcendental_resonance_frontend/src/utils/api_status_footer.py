# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards
"""Footer widget displaying backend connectivity status."""

from __future__ import annotations

import asyncio
import logging

try:  # pragma: no cover - allow import without NiceGUI installed
    from nicegui import background_tasks, ui
    from nicegui.element import Element
except Exception:  # pragma: no cover - fallback stubs for testing
    import types

    class Element:  # type: ignore
        pass

    class _DummyBG:
        def create(self, *args, **kwargs):
            return None

    class _DummyUI:
        def row(self, *args, **kwargs) -> Element:
            return Element()

        def icon(self, *args, **kwargs) -> Element:
            return Element()

        def label(self, *args, **kwargs) -> Element:
            return Element()

    background_tasks = _DummyBG()  # type: ignore
    ui = _DummyUI()  # type: ignore

from .api import api_call


class ApiStatusFooter:
    """Periodic API checker showing online/offline state."""

    def __init__(self, interval: int = 30) -> None:
        self._interval = interval
        with ui.row().classes("fixed bottom-0 right-0 items-center m-2"):
            self._icon = ui.icon("cloud").style("color: red")
            self._label = ui.label("Offline").classes("text-sm")
        background_tasks.create(self._update_loop(), name="api-status-footer")
        self._logger = logging.getLogger(__name__)

    async def _update_loop(self) -> None:
        while True:  # pragma: no cover - animation loop
            try:
                ok = await api_call("GET", "/status")
            except Exception as exc:  # pragma: no cover - network errors
                self._logger.error("API status check failed: %s", exc)
                ok = None
            if ok is not None:
                self._icon.style("color: green")
                self._label.text = "Online"
            else:
                self._icon.style("color: red")
                self._label.text = "Offline"
            await asyncio.sleep(self._interval)


__all__ = ["ApiStatusFooter"]
