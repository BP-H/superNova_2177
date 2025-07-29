from nicegui import ui
from typing import Any

CATEGORIES = {
    "emotion": ["😀", "😂", "😊", "😭"],
    "gesture": ["👍", "🤘", "🙏", "👏"],
    "hearts": ["❤️", "💜", "💙", "💚"],
}


def emoji_toolbar(input_ref: Any) -> None:
    """Add emoji buttons with simple category tabs."""
    tabs = ui.tabs(list(CATEGORIES.keys()), value="emotion").classes("mb-1")
    container = ui.row().classes("mb-2")

    def populate(category: str) -> None:
        container.clear()
        with container:
            for emoji in CATEGORIES[category]:
                ui.button(
                    emoji,
                    on_click=lambda _=None, e=emoji: input_ref.set_value((input_ref.value or "") + e),
                ).props("flat", "dense")

    tabs.on("update:model-value", lambda e: populate(e.value))
    populate("emotion")
