"""Streamlit UI helper utilities.

This module provides small helpers used across the Streamlit
applications to keep the UI code concise and consistent.
"""

from __future__ import annotations

from typing import Any, Literal
import html
import io
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


def graph_to_graphml_buffer(graph: Any) -> io.BytesIO:
    """Return a ``BytesIO`` buffer containing GraphML for ``graph``."""
    buf = io.BytesIO()
    try:  # Prefer networkx when available
        import networkx as nx  # type: ignore

        write_fn = getattr(nx, "write_graphml", None)
        if callable(write_fn):
            write_fn(graph, buf)
            buf.seek(0)
            return buf
    except Exception:
        pass

    nodes = list(getattr(graph, "nodes", []))
    edges_iter = getattr(graph, "edges", lambda data=False: [])(data=True)
    buf.write(b'<?xml version="1.0" encoding="utf-8"?>\n')
    buf.write(b'<graphml xmlns="http://graphml.graphdrawing.org/xmlns">\n')
    buf.write(b"  <graph edgedefault=\"undirected\">\n")
    for n in nodes:
        buf.write(f'    <node id="{n}"/>\n'.encode())
    for edge in edges_iter:
        if len(edge) == 3:
            u, v, data = edge
        else:
            u, v = edge[:2]
            data = {}
        weight = data.get("weight") if isinstance(data, dict) else None
        attr = f' weight="{weight}"' if weight is not None else ""
        buf.write(f'    <edge source="{u}" target="{v}"{attr}/>\n'.encode())
    buf.write(b"  </graph>\n</graphml>")
    buf.seek(0)
    return buf


def figure_to_png_buffer(fig: Any) -> io.BytesIO:
    """Return a ``BytesIO`` buffer containing a PNG of ``fig``."""
    buf = io.BytesIO()
    fig.write_image(buf, format="png")
    buf.seek(0)
    return buf

__all__ = [
    "alert",
    "header",
    "apply_theme",
    "theme_selector",
    "centered_container",
    "graph_to_graphml_buffer",
    "figure_to_png_buffer",
]

