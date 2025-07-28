import json
from typing import Any


def parse_llm_response(text: str) -> Any:
    """Return JSON object if ``text`` contains valid JSON, else stripped text."""
    try:
        return json.loads(text)
    except Exception:
        return text.strip()
