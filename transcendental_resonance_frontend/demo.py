"""Run the Transcendental Resonance UI in demo mode."""

from __future__ import annotations

from typing import Any, Dict, Optional

from utils import api, demo_data  # type: ignore


USERS = demo_data.load_users()
EVENTS = demo_data.load_events()
VIBENODES = demo_data.load_vibenodes()


def _mock_api_call(method: str, endpoint: str, data: Optional[Dict] = None,
                   headers: Optional[Dict] = None, files: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
    if method == "GET":
        if endpoint == "/users":
            return USERS
        if endpoint == "/events":
            return EVENTS
        if endpoint == "/vibenodes":
            return VIBENODES
    return api._original_api_call(method, endpoint, data, headers, files)  # type: ignore


def main() -> None:
    """Launch the UI with API calls mocked using sample data."""
    api._original_api_call = api.api_call  # type: ignore
    api.api_call = _mock_api_call  # type: ignore

    import main  # noqa: F401 - importing runs the UI


if __name__ == "__main__":
    main()
