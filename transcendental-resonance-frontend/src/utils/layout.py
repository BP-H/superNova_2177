from typing import Sequence, Tuple, Callable
from nicegui import ui
from .styles import get_theme


Link = Tuple[str, Callable]


def create_header(links: Sequence[Link], toggle_theme: Callable, logout: Callable) -> ui.element:
    """Create a persistent header with navigation and actions."""
    header = ui.header().classes("items-center justify-between px-4 py-2")

    with header:
        with ui.row().classes("gap-4"):
            for text, target in links:
                ui.link(text, target)
        with ui.row().classes("gap-2"):
            ui.button("Toggle Theme", on_click=toggle_theme)
            ui.button("Logout", on_click=logout)

    update_header_style(header)
    return header


def update_header_style(header: ui.element) -> None:
    """Apply the current theme colors to the header."""
    theme = get_theme()
    header.style(f"background: {theme['gradient']}; color: {theme['text']};")
