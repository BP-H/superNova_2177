"""UI component displaying a loading spinner during API requests."""

from __future__ import annotations

from nicegui import ui

from .api import on_request_start, on_request_end


class LoadingOverlay:
    """Display a simple spinner dialog while API calls are running."""

    def __init__(self) -> None:
        self._count = 0
        self._dialog = ui.dialog().props("persistent")
        with self._dialog:
            with ui.card():
                ui.spinner(size="lg")

        on_request_start(self._on_start)
        on_request_end(self._on_end)

    def _on_start(self) -> None:
        self._count += 1
        if not self._dialog.open:
            self._dialog.open()

    def _on_end(self) -> None:
        self._count = max(0, self._count - 1)
        if self._count == 0 and self._dialog.open:
            self._dialog.close()


__all__ = ["LoadingOverlay"]
