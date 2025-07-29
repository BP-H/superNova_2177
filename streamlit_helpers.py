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


def apply_theme(theme: str) -> None:
    """Apply global CSS for the selected ``theme``."""
    font_link = (
        "<link href='https://fonts.googleapis.com/css2?family=Inter:wght@400;600&"
        "family=Iosevka&display=swap' rel='stylesheet'>"
    )

    if theme == "dark":
        css = f"""
            {font_link}
            <style>
                :root {{
                    --bg-color: #121212;
                    --text-color: #e0e0e0;
                    --accent-color: #45a1ff;
                }}

                body, .stApp {{
                    background-color: var(--bg-color);
                    color: var(--text-color);
                    font-family: 'Inter', 'Iosevka', monospace;
                }}

                .stButton>button {{
                    background-color: var(--accent-color);
                    color: var(--bg-color);
                    border: none;
                    border-radius: 4px;
                    padding: 0.25rem 0.75rem;
                }}

                .stButton>button:hover {{
                    filter: brightness(1.1);
                }}

                h1, h2, h3 {{
                    color: var(--text-color);
                }}

                hr {{
                    border-color: var(--accent-color);
                    opacity: 0.2;
                }}
            </style>
        """
    elif theme == "modern":
        css = f"""
            {font_link}
            <style>
                :root {{
                    --bg-color: #f5f5f5;
                    --text-color: #333333;
                    --accent-color: #03DAC5;
                }}

                body, .stApp {{
                    background-color: var(--bg-color);
                    color: var(--text-color);
                    font-family: 'Inter', 'Iosevka', monospace;
                }}

                .stButton>button {{
                    background-color: var(--accent-color);
                    color: var(--bg-color);
                    border: none;
                    border-radius: 4px;
                    padding: 0.25rem 0.75rem;
                }}

                .stButton>button:hover {{
                    filter: brightness(1.1);
                }}

                h1, h2, h3 {{
                    color: var(--text-color);
                }}

                hr {{
                    border-color: var(--accent-color);
                    opacity: 0.3;
                }}
            </style>
        """
    elif theme == "minimalist_dark":
        font_link = (
            "<link href='https://fonts.googleapis.com/css2?family=Iosevka:wght@400;700&display=swap' rel='stylesheet'>"
        )
        css = f"""
            {font_link}
            <style>
                :root {{
                    --bg-color: #1a1a1a;
                    --text-color: #e0e0e0;
                    --accent-color: #6d8cff;
                }}

                body, .stApp {{
                    background-color: var(--bg-color);
                    color: var(--text-color);
                    font-family: 'Iosevka', monospace;
                }}

                .stButton>button {{
                    background-color: var(--accent-color);
                    color: var(--bg-color);
                    border: none;
                    border-radius: 4px;
                    padding: 0.25rem 0.75rem;
                }}

                .stButton>button:hover {{
                    filter: brightness(1.1);
                }}

                h1, h2, h3 {{
                    color: var(--text-color);
                }}

                hr {{
                    border-color: var(--accent-color);
                    opacity: 0.2;
                }}
            </style>
        """
    else:
        css = f"""
            {font_link}
            <style>
                :root {{
                    --bg-color: #ffffff;
                    --text-color: #333333;
                    --accent-color: #0066cc;
                }}

                body, .stApp {{
                    background-color: var(--bg-color);
                    color: var(--text-color);
                    font-family: 'Inter', 'Iosevka', monospace;
                }}

                .stButton>button {{
                    background-color: var(--accent-color);
                    color: #ffffff;
                    border: none;
                    border-radius: 4px;
                    padding: 0.25rem 0.75rem;
                }}

                .stButton>button:hover {{
                    filter: brightness(1.1);
                }}

                h1, h2, h3 {{
                    color: var(--text-color);
                }}

                hr {{
                    border-color: var(--accent-color);
                    opacity: 0.3;
                }}
            </style>
        """
    st.markdown(css, unsafe_allow_html=True)


def theme_selector(label: str = "Theme") -> str:
    """Render a radio selector for the app theme and return the choice."""
    if "theme" not in st.session_state:
        st.session_state["theme"] = "light"
    options = ["Light", "Dark", "Modern", "Minimalist Dark"]
    label_map = {
        "light": "Light",
        "dark": "Dark",
        "modern": "Modern",
        "minimalist_dark": "Minimalist Dark",
    }
    current_label = label_map.get(st.session_state["theme"], "Light")
    choice = st.radio(
        label,
        options,
        index=options.index(current_label),
        horizontal=True,
    )
    reverse_map = {v: k for k, v in label_map.items()}
    st.session_state["theme"] = reverse_map[choice]
    apply_theme(st.session_state["theme"])
    return st.session_state["theme"]


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
