"""Styling utilities for the Transcendental Resonance frontend."""

from nicegui import ui
from .api import THEME


def apply_global_styles() -> None:
    """Inject global CSS styles into the application."""
    ui.add_head_html(
        f"""
        <style>
            body {{ background: {THEME['background']}; color: {THEME['text']}; }}
            .q-btn:hover {{ border: 1px solid {THEME['accent']}; }}
            .futuristic-gradient {{ background: {THEME['gradient']}; }}
        </style>
        """
    )
