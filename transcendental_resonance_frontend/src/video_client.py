from __future__ import annotations

from typing import Dict
import base64
import os

from quantum_futures import DISCLAIMER

# Default offline mode flag
_DEFAULT_OFFLINE = os.getenv("TR_OFFLINE", "0") == "1"


async def generate_video_preview(
    script: str,
    *,
    offline: bool | None = None,
) -> Dict[str, str]:
    """Return a short video preview for ``script``.

    In offline mode a deterministic placeholder is returned.
    """
    if offline is None:
        offline = _DEFAULT_OFFLINE

    if offline:
        placeholder = base64.b64encode(b"preview").decode("ascii")
        return {"preview": placeholder, "disclaimer": DISCLAIMER}

    # Online mode would call an external service; stub using encoded script
    preview = base64.b64encode(script.encode("utf-8")).decode("ascii")
    return {"preview": preview, "disclaimer": DISCLAIMER}


__all__ = ["generate_video_preview"]
