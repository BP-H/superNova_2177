from __future__ import annotations

"""Base client for external API integrations with runtime BYOK support."""

import os
import uuid
from datetime import datetime
from typing import Any, Dict

from disclaimers import STRICTLY_SOCIAL_MEDIA


class BaseClient:
    """Minimal base client providing response metadata helpers."""

    def __init__(self, api_url: str | None = None, api_key: str | None = None) -> None:
        self.api_url = api_url or ""
        self.api_key = api_key or ""

    @property
    def offline(self) -> bool:
        return (
            os.getenv("OFFLINE_MODE", "0") == "1"
            or not self.api_key
            or not self.api_url
        )

    def _metadata(self, source: str) -> Dict[str, str]:
        return {
            "source": source,
            "timestamp": datetime.utcnow().isoformat(),
            "trace_id": uuid.uuid4().hex,
            "disclaimer": STRICTLY_SOCIAL_MEDIA,
        }

    def _wrap(self, source: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        data = self._metadata(source)
        data.update(payload)
        return data
