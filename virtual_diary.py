"""Minimal virtual diary interface."""

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
