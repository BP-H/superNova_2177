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


THEMES = {
    "dark": {"bg": "#1e1e1e", "text": "#f0f0f0", "font": "'Inter', sans-serif"},
    "minimalist_dark": {
        "bg": "#1a1a1a",
        "text": "#f0f0f0",
        "font": "'Iosevka', monospace",
        "font_link": '<link href="https://fonts.googleapis.com/css2?family=Iosevka:wght@400;700&display=swap" rel="stylesheet">',
    },
    "light": {"bg": "#ffffff", "text": "#000000", "font": "'Inter', sans-serif"},
    "modern": {"bg": "#f5f5f5", "text": "#333333", "font": "'Inter', sans-serif"},
}


def apply_theme(theme: str) -> None:
    """Apply styles based on ``theme``."""
    cfg = THEMES.get(theme, THEMES["light"])
    font_link = cfg.get(
        "font_link",
        '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap" rel="stylesheet">',
    )
    css = f"""
        {font_link}
        <style id="app-theme">
        body, .stApp {{
            background-color: {cfg['bg']};
            color: {cfg['text']};
            font-family: {cfg['font']};
        }}
        </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def theme_selector(label: str = "Theme") -> str:
    """Render a radio selector for the app theme and return the choice."""
    themes = [
        ("Light", "light"),
        ("Dark", "dark"),
        ("Minimalist Dark", "minimalist_dark"),
        ("Modern", "modern"),
    ]
    if "theme" not in st.session_state:
        st.session_state["theme"] = "light"
    labels = [t[0] for t in themes]
    current_label = next(
        (l for l, v in themes if v == st.session_state["theme"]), labels[0]
    )
    choice = st.radio(label, labels, index=labels.index(current_label), horizontal=True)
    selected = next(v for l, v in themes if l == choice)
    st.session_state["theme"] = selected
    apply_theme(selected)
    return selected


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
