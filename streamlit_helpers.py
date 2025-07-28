"""Streamlit UI helper utilities.

This module provides small helpers used across the Streamlit
applications to keep the UI code concise and consistent.
"""

from __future__ import annotations

from typing import Literal
from contextlib import contextmanager

import streamlit as st


try:  # pragma: no cover - depends on Streamlit version
    _escape_md = st.escape_markdown
except AttributeError:  # pragma: no cover - fallback for older versions
    try:  # pragma: no cover - optional text_util path
        from streamlit.text_util import escape_markdown as _escape_md  # type: ignore
    except Exception:  # pragma: no cover - final fallback
        def _escape_md(text: str) -> str:
            return (
                text.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
            )


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
        f"{_escape_md(message)}</div>",
        unsafe_allow_html=True,
    )


def header(title: str, *, layout: str = "centered") -> None:
    """Render a standard page header and apply base styling."""
    st.set_page_config(page_title=title, layout=layout)
    st.markdown(
        "<style>.app-container{padding:1rem 2rem;}" "</style>",
        unsafe_allow_html=True,
    )
    st.header(title)


def apply_theme(theme: str) -> None:
    """Apply light or dark theme styles based on ``theme``."""
    if theme == "dark":
        st.markdown(
            """
            <style>
            body, .stApp { background-color: #1e1e1e; color: #f0f0f0; }
            </style>
            """,
            unsafe_allow_html=True,
        )


def theme_selector(label: str = "Theme") -> str:
    """Render a radio selector for the app theme and return the choice."""
    if "theme" not in st.session_state:
        st.session_state["theme"] = "light"
    choice = st.radio(
        label,
        ["Light", "Dark"],
        index=(1 if st.session_state["theme"] == "dark" else 0),
        horizontal=True,
    )
    st.session_state["theme"] = choice.lower()
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

