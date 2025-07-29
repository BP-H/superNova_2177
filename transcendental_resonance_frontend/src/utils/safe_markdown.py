"""Utilities for safe Markdown rendering."""

import html
import re

_TAG_RE = re.compile(r"<[^>]+>")


def safe_markdown(text: str) -> str:
    """Return sanitized markdown text by stripping HTML tags."""
    if not text:
        return ""
    cleaned = _TAG_RE.sub("", text)
    return html.escape(cleaned)
