from nicegui import ui
from typing import Any


def emoji_toolbar(input_ref: Any) -> None:
    """Add simple emoji buttons that append to the given textarea."""
    with ui.row().classes("mb-2"):
        for emoji in ["😀", "🔥", "🎉"]:
            ui.button(
                emoji,
                on_click=lambda _=None, e=emoji: input_ref.set_value((input_ref.value or "") + e),
            ).props("flat")
