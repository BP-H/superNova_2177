"""Streamlit UI helper utilities.

This module provides small helpers used across the Streamlit
applications to keep the UI code concise and consistent.
"""

from __future__ import annotations

from typing import Any, Literal
import importlib
from types import SimpleNamespace

try:  # pragma: no cover - optional for test environments
    import streamlit as st
except Exception:  # pragma: no cover - lightweight stub
    st = SimpleNamespace(
        markdown=lambda *a, **k: None,
        set_page_config=lambda *a, **k: None,
        header=lambda *a, **k: None,
        escape_markdown=lambda t: t,
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
        f"{st.escape_markdown(message)}</div>",
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


def optional_import(module: str, attr: str | None = None, default: Any | None = None) -> Any:
    """Attempt to import ``module`` and return ``attr`` if provided.

    If the import fails, ``default`` is returned instead of raising an error.
    """
    try:
        mod = importlib.import_module(module)
        return getattr(mod, attr) if attr else mod
    except Exception:
        return default


def get_plotly() -> Any:
    """Return :mod:`plotly.graph_objects` or a no-op stand in."""

    class _NoPlotly(SimpleNamespace):
        def __getattr__(self, name: str) -> Any:  # pragma: no cover - minimal stub
            return lambda *a, **k: None

    return optional_import("plotly.graph_objects", default=_NoPlotly())


def get_pyvis() -> Any:
    """Return :class:`pyvis.network.Network` or a no-op alternative."""

    class _NoNetwork:
        def __init__(self, *a, **k) -> None:
            self.node_ids = set()

        def add_node(self, node: Any, **_kw) -> None:
            self.node_ids.add(node)

        def add_edge(self, *_a, **_k) -> None:
            pass

        def show(self, *_a, **_k) -> None:
            pass

    return optional_import("pyvis.network", "Network", default=_NoNetwork)

__all__ = [
    "alert",
    "header",
    "optional_import",
    "get_plotly",
    "get_pyvis",
]

