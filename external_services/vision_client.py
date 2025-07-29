# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards
"""Stub client for simple vision analysis."""

from __future__ import annotations

from typing import Any, Dict

from .base_client import BaseClient


class VisionClient(BaseClient):
    """Vision analysis client providing deterministic offline results."""

    OFFLINE_TEXT = "An offline description of the provided image."

    async def analyze_image(self, _image: bytes) -> Dict[str, Any]:
        """Return a simple description for an image."""
        placeholder = {"text": self.OFFLINE_TEXT}
        if self.offline:
            return self._offline_response(placeholder)
        try:
            raise NotImplementedError("Vision API not implemented")
        except Exception as e:  # pragma: no cover - until implemented
            return self._error_response(e, placeholder)


__all__ = ["VisionClient"]
