from __future__ import annotations

from typing import Any, Dict, List

from nicegui import ui


def emoji_toolbar(input_ref: Any) -> None:
    """Display emoji buttons with category selection."""
    categories: Dict[str, List[str]] = {
        "emotion": ["😀", "😂", "😢", "😎"],
        "gesture": ["👍", "👎", "🙏", "👏"],
        "hearts": ["❤️", "💜", "💖", "💙"],
    }
    selector = ui.select(list(categories.keys()), value="emotion").props(
        "dense outlined"
    ).classes("w-28 mb-1")
    button_row = ui.row().classes("mb-2")

    def populate(_: Any = None) -> None:
        button_row.clear()
        for emoji in categories[selector.value]:
            ui.button(
                emoji,
                on_click=lambda _=None, e=emoji: input_ref.set_value(
                    (input_ref.value or "") + e
                ),
            ).props("flat").classes("min-w-min")

    selector.on("update:model-value", populate)
    populate()
