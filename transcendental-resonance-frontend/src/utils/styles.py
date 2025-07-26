"""Styling utilities for the Transcendental Resonance frontend."""

from typing import Dict

from nicegui import ui

# Theme palettes. The default "dark" theme matches the original neon aesthetic.
THEMES: Dict[str, Dict[str, str]] = {
    "dark": {
        "primary": "#0d47a1",
        "accent": "#00e676",
        "background": "#121212",
        "text": "#ffffff",
        "gradient": "linear-gradient(135deg, #0d47a1 0%, #121212 100%)",
    },
    "light": {
        "primary": "#1976d2",
        "accent": "#ff4081",
        "background": "#ffffff",
        "text": "#000000",
        "gradient": "linear-gradient(135deg, #ffffff 0%, #f3f3f3 100%)",
    },
}

# Currently active theme. Can be switched at runtime via ``set_theme``.
ACTIVE_THEME: Dict[str, str] = THEMES["dark"]


def apply_global_styles() -> None:
    """Inject global CSS styles into the application."""
    ui.add_head_html(
        f"""
        <style id="global-theme">
            body {{ background: {ACTIVE_THEME['background']}; color: {ACTIVE_THEME['text']}; }}
            .q-btn:hover {{ border: 1px solid {ACTIVE_THEME['accent']}; }}
            .futuristic-gradient {{ background: {ACTIVE_THEME['gradient']}; }}
        </style>
        """
    )


def set_theme(name: str) -> None:
    """Switch the active theme by name and reapply global styles."""
    global ACTIVE_THEME
    ACTIVE_THEME = THEMES.get(name, THEMES["dark"])
    apply_global_styles()


def get_theme() -> Dict[str, str]:
    """Return the currently active theme dictionary."""
    return ACTIVE_THEME
