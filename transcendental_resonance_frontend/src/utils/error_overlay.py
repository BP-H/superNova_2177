from __future__ import annotations

"""Simple overlay component to surface fatal errors."""

from nicegui import ui


class ErrorOverlay:
    """Display an overlay with an error message."""

    def __init__(self) -> None:
        self._dialog = ui.dialog().props("persistent")
        with self._dialog:
            with ui.card():
                self._label = ui.label("Error")
                ui.button("Close", on_click=self.hide)

    def show(self, message: str) -> None:
        self._label.text = message
        if not self._dialog.open:
            self._dialog.open()

    def hide(self) -> None:
        if self._dialog.open:
            self._dialog.close()


__all__ = ["ErrorOverlay"]
