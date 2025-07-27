"""Utility functions for communicating with the Transcendental Resonance backend."""

from typing import Optional, Dict

import os
import requests
from nicegui import ui

# Backend API base URL
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")


class TokenManager:
    """Simple token container to avoid relying on module level globals."""

    def __init__(self) -> None:
        self._token: Optional[str] = None

    def set_token(self, token: str) -> None:
        """Store the user's access token."""
        self._token = token

    def clear_token(self) -> None:
        """Clear the stored access token."""
        self._token = None

    def get_token(self) -> Optional[str]:
        return self._token


token_manager = TokenManager()


def api_call(
    method: str,
    endpoint: str,
    data: Optional[Dict] = None,
    headers: Optional[Dict] = None,
    files: Optional[Dict] = None,
) -> Optional[Dict]:
    """Wrapper around ``requests`` to interact with the backend API."""
    url = f"{BACKEND_URL}{endpoint}"
    default_headers = (
        {"Content-Type": "application/json"} if method != "multipart" else {}
    )
    if headers:
        default_headers.update(headers)
    token = token_manager.get_token()
    if token:
        default_headers["Authorization"] = f"Bearer {token}"

    try:
        if method == "GET":
            response = requests.get(url, headers=default_headers, params=data)
        elif method == "POST":
            if files:
                response = requests.post(
                    url, headers=default_headers, data=data, files=files
                )
            else:
                response = requests.post(url, headers=default_headers, json=data)
        elif method == "PUT":
            response = requests.put(url, headers=default_headers, json=data)
        elif method == "DELETE":
            response = requests.delete(url, headers=default_headers, json=data)
        else:
            raise ValueError(f"Unsupported method: {method}")
        response.raise_for_status()
        return response.json() if response.text else None
    except requests.exceptions.RequestException as exc:
        ui.notify(f"API Error: {exc}", color="negative")
        return None
