# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards
"""Streamlit UI helper utilities.

This module provides small helpers used across the Streamlit
applications to keep the UI code concise and consistent.
"""

from __future__ import annotations

import html
from typing import Literal

import streamlit as st

# isort: off
from transcendental_resonance_frontend.src.utils import styles
from transcendental_resonance_frontend.src.utils.styles import get_theme, get_theme_name

# isort: on


def alert(message: str, level: Literal["warning", "error", "info"] = "info") -> None:
    """Display a styled Markdown alert box."""
    colors = {
        "warning": ("#fff4e5", "#e6a700"),
        "error": ("#ffe5e5", "#c80000"),
        "info": ("#e5f2ff", "#0049b5"),
    }
    bg_color, border_color = colors.get(level, colors["info"])
    st.markdown(
        f"<div style='border-left: 4px solid {border_color}; "
        f"background-color: {bg_color}; padding: 0.5em; "
        f"border-radius: 0 4px 4px 0; margin-bottom: 1em;'>"
        f"{html.escape(message)}</div>",
        unsafe_allow_html=True,
    )


def header(title: str, *, layout: str = "centered") -> None:
    """Render a standard page header and apply base styling."""
    st.markdown(
        "<style>.app-container{padding:1rem 2rem;}" "</style>",
        unsafe_allow_html=True,
    )
    st.header(title)


def apply_theme(theme: str) -> None:
    """Apply light or dark theme styles based on ``theme``."""
    if theme == "dark":
        # Align Streamlit dark mode with the frontend's minimalist style
        styles.set_theme("minimalist_dark")
    else:
        styles.set_theme(theme)

    palette = get_theme()

    font_family = "'Inter', sans-serif"
    font_link = (
        '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap"'
        ' rel="stylesheet">'
    )
    if get_theme_name() == "cyberpunk":
        font_family = "'Orbitron', sans-serif"
        font_link = (
            '<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap"'
            ' rel="stylesheet">'
        )

    css = f"""
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        {font_link}
        <style id="streamlit-theme">
            body, .stApp {{
                background-color: {palette['background']};
                color: {palette['text']};
                font-family: {font_family};
            }}
        </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def theme_selector(label: str = "Theme") -> str:
    """Render a radio selector for the app theme and return the choice."""
    if "theme" not in st.session_state:
        st.session_state["theme"] = "light"

    options = ["Light", "Dark", "Minimalist Dark"]
    if st.session_state["theme"] == "dark":
        index = 1
    elif st.session_state["theme"] == "minimalist_dark":
        index = 2
    else:
        index = 0

    choice = st.radio(label, options, index=index, horizontal=True)
    key = choice.lower().replace(" ", "_")
    st.session_state["theme"] = key
    apply_theme(key)
    return key


def centered_container(max_width: str = "900px") -> "st.delta_generator.DeltaGenerator":
    """Return a container with standardized width constraints."""
    st.markdown(
        f"<style>.main .block-container{{max-width:{max_width};margin:auto;}}</style>",
        unsafe_allow_html=True,
    )
    return st.container()


__all__ = [
    "alert",
    "header",
    "apply_theme",
    "theme_selector",
    "centered_container",
]
