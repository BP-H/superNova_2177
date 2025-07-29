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

from disclaimers import (
    STRICTLY_SOCIAL_MEDIA,
    INTELLECTUAL_PROPERTY_ARTISTIC_INSPIRATION,
    LEGAL_ETHICAL_SAFEGUARDS,
)

DEFAULT_DISCLAIMER_PHRASES = [
    STRICTLY_SOCIAL_MEDIA,
    INTELLECTUAL_PROPERTY_ARTISTIC_INSPIRATION,
    LEGAL_ETHICAL_SAFEGUARDS,
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


def _check_patch_file(path: str | None, additions: List[str], phrases: Iterable[str]) -> List[str]:
    """Return issues for a single file patch."""
    if not additions:
        return []
    text = "\n".join(additions)
    if _contains_disclaimers(text, phrases):
        return []
    if path:
        p = Path(path)
        if p.is_file() and _contains_disclaimers(p.read_text(errors="ignore"), phrases):
            return []
    return ["New additions missing required disclaimers"]


def check_patch_compliance(
    patch: str, phrases: Iterable[str] = DEFAULT_DISCLAIMER_PHRASES
) -> List[str]:
    """Inspect added lines in a diff patch for required disclaimers.

    If a modified file already contains the required phrases, the patch is
    considered compliant even when the additions themselves omit the lines.
    """
    issues: List[str] = []
    current_path: str | None = None
    additions: List[str] = []

    for line in patch.splitlines():
        if line.startswith("diff --git"):
            if current_path is not None:
                issues.extend(_check_patch_file(current_path, additions, phrases))
            current_path = None
            additions = []
            continue
        if line.startswith("+++ "):
            path = line[4:].strip()
            if path != "/dev/null":
                current_path = path[2:] if path.startswith("b/") else path
            continue
        if line.startswith("+") and not line.startswith("+++"):
            additions.append(line[1:])

    if current_path is not None:
        issues.extend(_check_patch_file(current_path, additions, phrases))

    # Handle patches without path information
    if not issues and additions:
        issues.extend(_check_patch_file(None, additions, phrases))

    return issues
