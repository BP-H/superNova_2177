"""Utility functions for communicating with the Transcendental Resonance backend."""

from typing import Optional, Dict

import httpx
from httpx import Response
from nicegui import ui

# Backend API base URL
BACKEND_URL = "http://localhost:8000"

# Theme configuration used across all pages
THEME = {
    'primary': '#0d47a1',  # Deep blue for futuristic feel
    'accent': '#00e676',   # Neon green
    'background': '#121212',  # Dark mode
    'text': '#ffffff',
    'gradient': 'linear-gradient(135deg, #0d47a1 0%, #121212 100%)'
}

TOKEN: Optional[str] = None

async def api_call(
    method: str,
    endpoint: str,
    data: Optional[Dict] = None,
    headers: Optional[Dict] = None,
    files: Optional[Dict] = None,
) -> Optional[Dict]:
    """Wrapper around ``httpx`` to interact with the backend API."""
    url = f"{BACKEND_URL}{endpoint}"
    default_headers = {'Content-Type': 'application/json'} if method != 'multipart' else {}
    if headers:
        default_headers.update(headers)
    if TOKEN:
        default_headers['Authorization'] = f'Bearer {TOKEN}'

    try:
        async with httpx.AsyncClient() as client:
            response: Response
            if method == 'GET':
                response = await client.get(url, headers=default_headers, params=data)
            elif method == 'POST':
                response = await client.post(url, headers=default_headers, json=data)
            elif method == 'PUT':
                response = await client.put(url, headers=default_headers, json=data)
            elif method == 'DELETE':
                response = await client.delete(url, headers=default_headers, json=data)
            elif method == 'multipart':
                response = await client.post(url, headers=default_headers, data=data, files=files)
            else:
                raise ValueError(f"Unsupported method: {method}")
        response.raise_for_status()
        return response.json() if response.text else None
    except httpx.HTTPError as exc:
        ui.notify(f"API Error: {exc}", color='negative')
        return None


def set_token(token: str) -> None:
    """Store the user's access token."""
    global TOKEN
    TOKEN = token


def clear_token() -> None:
    """Clear the stored access token."""
    global TOKEN
    TOKEN = None
