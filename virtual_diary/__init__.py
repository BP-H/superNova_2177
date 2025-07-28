"""Minimal virtual diary interface.

Diary entries are stored as dictionaries in ``virtual_diary.json``. Each entry
may contain a ``timestamp`` and free form ``note`` text.  The optional
``rfc_ids`` field stores a list of referenced RFC identifiers.  This module only
provides a lightweight loader used by the tests and the Streamlit UI.
"""

import json
import logging
import os
from typing import Any, Dict, List

logger = logging.getLogger(__name__)
logger.propagate = False


def load_entries(limit: int = 20) -> List[Dict[str, Any]]:
    """Return the most recent diary entries.

    Parameters
    ----------
    limit:
        Maximum number of entries to return.
    """
    path = os.environ.get("VIRTUAL_DIARY_FILE", "virtual_diary.json")
    try:
        with open(path, "r") as f:
            data = json.load(f)
        if isinstance(data, list):
            return data[-limit:]
    except Exception:
        logger.exception("Failed to load virtual diary")
    return []

__all__ = ["load_entries"]

def add_entry(entry: Dict[str, Any]) -> None:
    """Append ``entry`` to the virtual diary file."""
    path = os.environ.get("VIRTUAL_DIARY_FILE", "virtual_diary.json")
    try:
        data: List[Dict[str, Any]] = []
        if os.path.exists(path):
            with open(path, "r") as f:
                loaded = json.load(f)
                if isinstance(loaded, list):
                    data = loaded
        data.append(entry)
        with open(path, "w") as f:
            json.dump(data, f, default=str)
    except Exception:
        logger.exception("Failed to update virtual diary")


