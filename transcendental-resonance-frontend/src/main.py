"""Main entry point for the Transcendental Resonance frontend."""

from nicegui import ui, background_tasks
import asyncio

from .utils.api import clear_token, api_call
from .utils.styles import apply_global_styles
from .utils.layout import header
from .pages import *  # register all pages
from .pages.system_insights_page import system_insights_page  # noqa: F401

ui.context.client.on_disconnect(clear_token)
apply_global_styles()
header()


async def keep_backend_awake() -> None:
    """Periodically ping the backend to keep data fresh."""
    while True:
        api_call('GET', '/status')
        await asyncio.sleep(300)

ui.on_startup(lambda: background_tasks.create(keep_backend_awake(), name='backend-pinger'))

# Potential future enhancements:
# - Real-time updates via WebSockets
# - Internationalization support
# - Theming options

ui.run(title='Transcendental Resonance', dark=True, favicon='🌌', reload=False)
