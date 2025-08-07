"""STRICTLY A SOCIAL MEDIA PLATFORM
Intellectual Property & Artistic Inspiration
Legal & Ethical Safeguards

Display proposal ideas from the RFC directory.
"""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from ui_utils import summarize_text

# Load the initial proposals document containing the idea list
IDEAS_FILE = (
    Path(__file__).resolve().parents[1] / "rfcs" / "001-initial-proposals" / "README.md"
)


def _load_ideas() -> list[str]:
    """Return bullet list items extracted from the initial proposals file."""
    try:
        text = IDEAS_FILE.read_text()
    except Exception:
        return []

    ideas: list[str] = []
    recording = False
    for line in text.splitlines():
        if line.startswith("## Specification"):
            recording = True
            continue
        if line.startswith("## ") and recording:
            # stop when leaving the specification section
            if not line.startswith("###"):
                break
        if recording and line.lstrip().startswith("-"):
            idea = line.lstrip("- ").strip()
            if idea:
                ideas.append(idea)
    return ideas


def main() -> None:
    """Render the ideas page."""
    st.header("Project Ideas")
    ideas = _load_ideas()
    if not ideas:
        st.info("No ideas found")
        return

    for idea in ideas:
        st.markdown(f"- {summarize_text(idea)}")
