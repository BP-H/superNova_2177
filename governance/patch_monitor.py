"""Patch compliance monitoring utilities.

These helpers evaluate incoming code additions
for required governance disclaimers or other
policy markers defined in ``DEFAULT_DISCLAIMER_PHRASES``.

The functions can be integrated into commit hooks
or CI jobs to automatically flag patches that
lack mandatory legal language.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, List

DEFAULT_DISCLAIMER_PHRASES = [
    "STRICTLY A SOCIAL MEDIA PLATFORM",
    "Intellectual Property & Artistic Inspiration",
    "Legal & Ethical Safeguards",
]


def _contains_disclaimers(
    text: str, phrases: Iterable[str] = DEFAULT_DISCLAIMER_PHRASES
) -> bool:
    lower = text.lower()
    return all(p.lower() in lower for p in phrases)


def check_file_compliance(
    path: str, phrases: Iterable[str] = DEFAULT_DISCLAIMER_PHRASES
) -> List[str]:
    """Return a list of issues for ``path`` if disclaimers are missing."""
    p = Path(path)
    if not p.is_file():
        return [f"File {path} does not exist"]
    text = p.read_text(errors="ignore")
    if not _contains_disclaimers(text, phrases):
        return [f"Missing required disclaimers in {p.name}"]
    return []


def check_patch_compliance(
    patch: str, phrases: Iterable[str] = DEFAULT_DISCLAIMER_PHRASES
) -> List[str]:
    """Inspect added lines in a diff patch for required disclaimers."""
    additions = [
        line[1:]
        for line in patch.splitlines()
        if line.startswith("+") and not line.startswith("+++")
    ]
    text = "\n".join(additions)
    if additions and not _contains_disclaimers(text, phrases):
        return ["New additions missing required disclaimers"]
    return []
