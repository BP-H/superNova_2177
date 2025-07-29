"""Styling utilities for the Transcendental Resonance frontend."""

from typing import Dict, Optional
import json

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
    "modern": {
        "primary": "#6200EE",
        "accent": "#03DAC5",
        "background": "#f5f5f5",
        "text": "#333333",
        "gradient": "linear-gradient(135deg, #6200EE 0%, #03DAC5 100%)",
    },
}

# Custom themes created by the user are stored separately so they can be
# persisted to and loaded from ``localStorage``.
CUSTOM_THEMES: Dict[str, Dict[str, str]] = {}

# Currently active theme name and accent color. They can be changed at runtime
# and are persisted in the browser ``localStorage``.
ACTIVE_THEME_NAME: str = "dark"
ACTIVE_ACCENT: str = THEMES[ACTIVE_THEME_NAME]["accent"]


def _persist_custom_themes() -> None:
    """Write custom themes to ``localStorage``."""
    try:
        ui.run_javascript(
            f"localStorage.setItem('customThemes', '{json.dumps(CUSTOM_THEMES)}')"
        )
    except Exception:
        # Accessing localStorage may fail during testing
        pass


def save_custom_theme(name: str, theme: Dict[str, str]) -> None:
    """Save a new custom theme and persist it."""
    CUSTOM_THEMES[name] = theme
    THEMES[name] = theme
    _persist_custom_themes()


def create_custom_theme(name: str, background: str, text: str) -> None:
    """Create and store a custom theme using the current accent."""
    base = THEMES[ACTIVE_THEME_NAME]
    theme = {
        "primary": base["primary"],
        "accent": ACTIVE_ACCENT,
        "background": background,
        "text": text,
        "gradient": f"linear-gradient(135deg, {background} 0%, {background} 100%)",
    }
    save_custom_theme(name, theme)


def apply_global_styles() -> None:
    """Inject global CSS styles based on stored theme and accent settings."""
    global ACTIVE_THEME_NAME, ACTIVE_ACCENT

    try:
        stored_custom = ui.run_javascript(
            "localStorage.getItem('customThemes')",
            respond=True,
        )
        if isinstance(stored_custom, str) and stored_custom:
            try:
                data = json.loads(stored_custom)
                if isinstance(data, dict):
                    CUSTOM_THEMES.update(
                        {k: v for k, v in data.items() if isinstance(v, dict)}
                    )
                    THEMES.update(CUSTOM_THEMES)
            except Exception:
                pass
        stored_theme: Optional[str] = ui.run_javascript(
            "localStorage.getItem('theme')",
            respond=True,
        )
        if isinstance(stored_theme, str) and stored_theme in THEMES:
            ACTIVE_THEME_NAME = stored_theme
        stored_accent: Optional[str] = ui.run_javascript(
            "localStorage.getItem('accent')",
            respond=True,
        )
        if isinstance(stored_accent, str) and stored_accent:
            ACTIVE_ACCENT = stored_accent
    except Exception:
        # Accessing localStorage may fail during testing
        pass

    theme = THEMES[ACTIVE_THEME_NAME].copy()
    theme["accent"] = ACTIVE_ACCENT

    ui.add_head_html(
        f"""
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap" rel="stylesheet">
        <style id="global-theme">
            body {{ font-family: 'Inter', sans-serif; background: {theme['background']}; color: {theme['text']}; }}
            .q-btn:hover {{ border: 1px solid {theme['accent']}; }}
            .futuristic-gradient {{ background: {theme['gradient']}; }}
        </style>
        """
    )


def set_theme(name: str) -> None:
    """Switch the active theme by name and reapply global styles."""
    global ACTIVE_THEME_NAME, ACTIVE_ACCENT
    ACTIVE_THEME_NAME = name if name in THEMES else "dark"
    # reset accent to theme default when switching themes
    ACTIVE_ACCENT = THEMES[ACTIVE_THEME_NAME]["accent"]
    ui.run_javascript(f"localStorage.setItem('theme', '{ACTIVE_THEME_NAME}')")
    ui.run_javascript(f"localStorage.setItem('accent', '{ACTIVE_ACCENT}')")
    apply_global_styles()


def get_theme() -> Dict[str, str]:
    """Return the currently active theme dictionary."""
    theme = THEMES[ACTIVE_THEME_NAME].copy()
    theme["accent"] = ACTIVE_ACCENT
    return theme


def get_theme_name() -> str:
    """Return the name of the currently active theme."""
    return ACTIVE_THEME_NAME


def set_accent(color: str) -> None:
    """Update only the accent color and store the preference."""
    global ACTIVE_ACCENT
    ACTIVE_ACCENT = color
    ui.run_javascript(f"localStorage.setItem('accent', '{color}')")
    apply_global_styles()

