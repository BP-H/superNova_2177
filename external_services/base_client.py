from __future__ import annotations

"""Abstract base class for optional API integrations.

Each client built on :class:`BaseClient` automatically handles offline mode,
error suppression and metadata injection. The ``offline`` flag is determined by
missing environment variables or ``OFFLINE_MODE=1``. Subclasses implement the
``_api_call`` method and optionally ``_offline_result`` to customize placeholder
payloads.
"""

import os
import logging
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, Dict
from uuid import uuid4


class BaseClient(ABC):
    """Abstract helper providing resilient API behaviour."""

    OFFLINE_ENV = "OFFLINE_MODE"

    def __init__(self, key_env: str, url_env: str, placeholder: Dict[str, Any]):
        self.api_key = os.getenv(key_env, "")
        self.api_url = os.getenv(url_env, "")
        env_offline = os.getenv(self.OFFLINE_ENV, "0") == "1"
        self.offline = env_offline or not self.api_key or not self.api_url
        self.placeholder = placeholder
        self.logger = logging.getLogger(self.__class__.__name__)

    def _meta(self, source: str, error: str | None = None) -> Dict[str, Any]:
        meta = {
            "source": source,
            "trace_id": str(uuid4()),
            "timestamp": datetime.utcnow().replace(tzinfo=timezone.utc).isoformat(),
        }
        if error:
            meta["error"] = error
        return meta

    async def request(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Execute the API request returning a payload with metadata."""
        if self.offline:
            data = await self._offline_result(*args, **kwargs)
            return {**data, **self._meta("offline")}
        try:
            data = await self._api_call(*args, **kwargs)
            return {**data, **self._meta("api")}
        except NotImplementedError as exc:  # pragma: no cover - fallback
            self.logger.warning("API not implemented: %s", exc)
            data = await self._offline_result(*args, **kwargs)
            return {**data, **self._meta("offline", str(exc))}
        except Exception as exc:  # pragma: no cover - network or auth errors
            self.logger.error("API call failed: %s", exc)
            data = await self._offline_result(*args, **kwargs)
            return {**data, **self._meta("offline", str(exc))}

    @abstractmethod
    async def _api_call(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Perform the real API request in subclasses."""
        raise NotImplementedError

    async def _offline_result(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Return placeholder output used when offline or errors occur."""
        return self.placeholder
