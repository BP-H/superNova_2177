"""LLM response parser utility."""

import json
import logging

logger = logging.getLogger(__name__)

__all__ = ["parse_llm_response"]


def parse_llm_response(text: str) -> dict | str:
    """Return parsed JSON if ``text`` is valid JSON, else return original string."""
    try:
        return json.loads(text)
    except Exception:
        logger.warning("Failed to parse LLM response as JSON: %s", text)
        return text
