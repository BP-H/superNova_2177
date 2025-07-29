"""Main entry point for the Transcendental Resonance frontend."""

# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards

import asyncio

from nicegui import background_tasks, ui

from .pages import *  # register all pages  # noqa: F401,F403
from .pages.explore_page import explore_page  # noqa: F401
from .pages.system_insights_page import system_insights_page  # noqa: F401
from .utils.api import api_call, clear_token
from .utils.loading_overlay import LoadingOverlay
from .utils.styles import (THEMES, apply_global_styles, get_theme_name,
                           set_theme)

ui.context.client.on_disconnect(clear_token)
apply_global_styles()
LoadingOverlay()


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
        await api_call("GET", "/status")
        await asyncio.sleep(300)


ui.button(
    "Theme",
    on_click=toggle_theme,
).classes("fixed top-0 right-0 m-2")

ui.on_startup(
    lambda: background_tasks.create(keep_backend_awake(), name="backend-pinger")
)

# Potential future enhancements:
# - Real-time updates via WebSockets
# - Internationalization support
# - Theming options

ui.run(title="Transcendental Resonance", dark=True, favicon="🌌", reload=False)
