"""Main entry point for the Transcendental Resonance frontend."""

from nicegui import ui

from .utils.api import clear_token
from .utils.styles import apply_global_styles, set_theme, get_theme, THEMES
from .pages import *  # register all pages

ui.context.client.on_disconnect(clear_token)
apply_global_styles()


def toggle_theme() -> None:
    """Switch between light and dark themes."""
    current = get_theme()
    new_name = "light" if current is THEMES["dark"] else "dark"
    set_theme(new_name)


ui.button(
    "Toggle Theme",
    on_click=toggle_theme,
).classes("fixed top-0 right-0 m-2")

# Potential future enhancements:
# - Real-time updates via WebSockets
# - Internationalization support
# - Theming options

ui.run(title='Transcendental Resonance', dark=True, favicon='🌌')
