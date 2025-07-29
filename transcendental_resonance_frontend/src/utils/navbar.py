"""Reusable navigation bar for the Transcendental Resonance UI."""
# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards

from nicegui import ui

from .styles import get_theme


def navigation_bar() -> None:
    """Render the standard navigation bar with themed links."""
    theme = get_theme()
    with ui.row().classes('navigation-bar w-full mb-4').style(
        f"background: {theme['primary']}; color: {theme['text']};"
    ):
        ui.link('Profile', '/profile').classes('px-2')
        ui.link('VibeNodes', '/vibenodes').classes('px-2')
        ui.link('Groups', '/groups').classes('px-2')
        ui.link('Events', '/events').classes('px-2')
        ui.link('Proposals', '/proposals').classes('px-2')
        ui.link('Messages', '/messages').classes('px-2')
        ui.link('Status', '/status').classes('px-2')
        ui.link('Insights', '/system-insights').classes('px-2')

