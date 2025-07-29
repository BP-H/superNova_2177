# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards
"""Utility functions for streamlit UIs."""

from pathlib import Path
import streamlit as st


def summarize_text(text: str, max_len: int = 150) -> str:
    """Basic text summarizer placeholder."""
    if len(text) <= max_len:
        return text
    return text[: max_len - 3] + "..."


def parse_summary(text: str) -> str:
    """Extract the summary section from an RFC markdown text."""
    if "## Summary" not in text:
        return ""
    part = text.split("## Summary", 1)[1]
    lines = []
    for line in part.splitlines()[1:]:
        if line.startswith("##"):
            break
        if line.strip():
            lines.append(line.strip())
    return " ".join(lines)


@st.cache_data
def load_rfc_entries(rfc_dir: Path):
    """Return list and index of RFC entries from a directory."""
    rfc_paths = sorted(rfc_dir.rglob("rfc-*.md"))
    rfc_entries = []
    rfc_index = {}
    for path in rfc_paths:
        text = path.read_text()
        summary = parse_summary(text)
        entry = {
            "id": path.stem,
            "summary": summary,
            "text": text,
            "path": path,
        }
        rfc_entries.append(entry)
        rfc_index[path.stem.lower()] = entry
    return rfc_entries, rfc_index


def render_main_ui() -> None:
    """Entry point wrapper for the main UI module."""
    from ui import main as _main

    _main()

