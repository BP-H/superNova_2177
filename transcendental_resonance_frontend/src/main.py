"""Main entry point for the Transcendental Resonance frontend."""
# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards

from nicegui import ui, background_tasks
import asyncio

from .utils.api import clear_token, api_call
from .utils.styles import apply_global_styles, set_theme, get_theme_name, THEMES
from .utils.navbar import navigation_bar
from .pages import *  # register all pages
from .pages.system_insights_page import system_insights_page  # noqa: F401

ui.context.client.on_disconnect(clear_token)
apply_global_styles()
navigation_bar()


def toggle_theme() -> None:
    """Cycle through available themes."""
    order = list(THEMES.keys())
    current = get_theme_name()
    try:
        idx = order.index(current)
    except ValueError:
        idx = 0
    new_name = order[(idx + 1) % len(order)]
    set_theme(new_name)


async def keep_backend_awake() -> None:
    """Periodically ping the backend to keep data fresh."""
    while True:
        await api_call('GET', '/status')
        await asyncio.sleep(300)


ui.button(
    "Theme",
    on_click=toggle_theme,
).classes("fixed top-0 right-0 m-2")

ui.on_startup(lambda: background_tasks.create(keep_backend_awake(), name='backend-pinger'))

# Potential future enhancements:
# - Real-time updates via WebSockets
# - Internationalization support
# - Theming options

ui.run(title='Transcendental Resonance', dark=True, favicon='🌌', reload=False)
