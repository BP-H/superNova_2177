# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards
"""Utility functions for communicating with the Transcendental Resonance backend."""

import logging
import os
from typing import Any, Dict, Optional

import httpx
from nicegui import ui

# Backend API base URL
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

logger = logging.getLogger(__name__)
logger.propagate = False

TOKEN: Optional[str] = None


async def api_call(
    method: str,
    endpoint: str,
    data: Optional[Dict] = None,
    headers: Optional[Dict] = None,
    files: Optional[Dict] = None,
    *,
    return_error: bool = False,
) -> Optional[Dict[str, Any]]:
    """Wrapper around ``httpx.AsyncClient`` to interact with the backend API.

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
    default_headers = (
        {"Content-Type": "application/json"} if method != "multipart" else {}
    )
    if headers:
        default_headers.update(headers)
    if TOKEN:
        default_headers["Authorization"] = f"Bearer {TOKEN}"

    try:
        async with httpx.AsyncClient() as client:
            if method == "GET":
                response = await client.get(url, headers=default_headers, params=data)
            elif method == "POST":
                if files:
                    response = await client.post(
                        url, headers=default_headers, data=data, files=files
                    )
                else:
                    response = await client.post(
                        url, headers=default_headers, json=data
                    )
            elif method == "PUT":
                response = await client.put(url, headers=default_headers, json=data)
            elif method == "DELETE":
                response = await client.delete(url, headers=default_headers, json=data)
            else:
                raise ValueError(f"Unsupported method: {method}")
            response.raise_for_status()
            return response.json() if response.text else None
    except httpx.RequestError as exc:
        logger.error("API request failed: %s %s - %s", method, url, exc, exc_info=True)
        ui.notify("API request failed", color="negative")
        if return_error:
            return {
                "error": str(exc),
                "status_code": getattr(
                    getattr(exc, "response", None), "status_code", None
                ),
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


async def get_user(username: str) -> Optional[Dict[str, Any]]:
    return await api_call("GET", f"/users/{username}")


async def get_followers(username: str) -> Dict[str, Any]:
    return await api_call("GET", f"/users/{username}/followers") or {
        "count": 0,
        "followers": [],
    }


async def get_following(username: str) -> Dict[str, Any]:
    return await api_call("GET", f"/users/{username}/following") or {
        "count": 0,
        "following": [],
    }


async def toggle_follow(username: str) -> Optional[Dict[str, Any]]:
    return await api_call("POST", f"/users/{username}/follow")
