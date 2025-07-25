"""Main entry point for the Transcendental Resonance frontend."""

from nicegui import ui

from .utils.api import clear_token
from .utils.styles import apply_global_styles
from .pages import *  # register all pages

ui.context.client.on_disconnect(clear_token)
apply_global_styles()

# Potential future enhancements:
# - Real-time updates via WebSockets
# - Internationalization support
# - Theming options

ui.run(title='Transcendental Resonance', dark=True, favicon='🌌')
