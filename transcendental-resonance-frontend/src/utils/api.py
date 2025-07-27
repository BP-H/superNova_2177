"""Utility functions for communicating with the Transcendental Resonance backend."""

from typing import Optional, Dict, Any

import os
import logging
import requests
from nicegui import ui

# Backend API base URL
BACKEND_URL = os.getenv("BACKEND_URL", "https://localhost:8000")
if BACKEND_URL.startswith("http://"):
    logging.warning("Insecure BACKEND_URL detected; forcing HTTPS")
    BACKEND_URL = BACKEND_URL.replace("http://", "https://", 1)

logger = logging.getLogger(__name__)

TOKEN: Optional[str] = None

def api_call(
    method: str,
    endpoint: str,
    data: Optional[Dict] = None,
    headers: Optional[Dict] = None,
    files: Optional[Dict] = None,
    *,
    return_error: bool = False,
) -> Optional[Dict[str, Any]]:
    """Wrapper around ``requests`` to interact with the backend API.

    Args:
        method: HTTP method ("GET", "POST", etc.).
        endpoint: API endpoint path.
        data: Optional data payload.
        headers: Optional HTTP headers.
        files: Optional file payload for multipart requests.
        return_error: If ``True`` return a dict describing the error instead of
            ``None`` when a request fails.
    """
    url = f"{BACKEND_URL}{endpoint}"
    default_headers = {'Content-Type': 'application/json'} if method != 'multipart' else {}
    if headers:
        default_headers.update(headers)
    if TOKEN:
        default_headers['Authorization'] = f'Bearer {TOKEN}'

    try:
        if method == 'GET':
            response = requests.get(url, headers=default_headers, params=data)
        elif method == 'POST':
            if files:
                response = requests.post(url, headers=default_headers, data=data, files=files)
            else:
                response = requests.post(url, headers=default_headers, json=data)
        elif method == 'PUT':
            response = requests.put(url, headers=default_headers, json=data)
        elif method == 'DELETE':
            response = requests.delete(url, headers=default_headers, json=data)
        else:
            raise ValueError(f"Unsupported method: {method}")
        response.raise_for_status()
        return response.json() if response.text else None
    except requests.exceptions.RequestException as exc:
        logger.error(
            "API request failed: %s %s - %s", method, url, exc, exc_info=True
        )
        ui.notify("API request failed", color="negative")
        if return_error:
            return {
                "error": str(exc),
                "status_code": getattr(exc.response, "status_code", None),
            }
        return None


def set_token(token: str) -> None:
    """Store the user's access token."""
    global TOKEN
    TOKEN = token


def clear_token() -> None:
    """Clear the stored access token."""
    global TOKEN
    TOKEN = None
