"""Utilities for loading sample data used in demo mode."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

_DATA_DIR = Path(__file__).parent / "sample_data"


def _load_json(name: str) -> List[Dict[str, Any]]:
    path = _DATA_DIR / name
    if not path.is_file():
        return []
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_users() -> List[Dict[str, Any]]:
    """Return the list of sample users."""
    return _load_json("users.json")


def load_events() -> List[Dict[str, Any]]:
    """Return the list of sample events."""
    return _load_json("events.json")


def load_vibenodes() -> List[Dict[str, Any]]:
    """Return the list of sample VibeNodes."""
    return _load_json("vibenodes.json")
