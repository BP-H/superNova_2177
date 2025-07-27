"""Utility functions for communicating with the Transcendental Resonance backend."""

from typing import Optional, Dict

import os
import aiohttp
from nicegui import ui

# Backend API base URL
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

TOKEN: Optional[str] = None


async def api_call(
    method: str,
    endpoint: str,
    data: Optional[Dict] = None,
    headers: Optional[Dict] = None,
    files: Optional[Dict] = None,
) -> Optional[Dict]:
    """Asynchronous wrapper using ``aiohttp`` to interact with the backend API."""
    url = f"{BACKEND_URL}{endpoint}"
    default_headers = {'Content-Type': 'application/json'} if method != 'multipart' else {}
    if headers:
        default_headers.update(headers)
    if TOKEN:
        default_headers['Authorization'] = f'Bearer {TOKEN}'

    try:
        async with aiohttp.ClientSession() as session:
            if method == 'GET':
                async with session.get(url, headers=default_headers, params=data) as response:
                    response.raise_for_status()
                    text = await response.text()
                    return await response.json() if text else None
            elif method == 'POST':
                if files:
                    form = aiohttp.FormData()
                    if data:
                        for key, value in data.items():
                            form.add_field(key, str(value))
                    for field, (filename, content, content_type) in files.items():
                        form.add_field(field, content, filename=filename, content_type=content_type)
                    async with session.post(url, headers=default_headers, data=form) as response:
                        response.raise_for_status()
                        text = await response.text()
                        return await response.json() if text else None
                else:
                    async with session.post(url, headers=default_headers, json=data) as response:
                        response.raise_for_status()
                        text = await response.text()
                        return await response.json() if text else None
            elif method == 'PUT':
                async with session.put(url, headers=default_headers, json=data) as response:
                    response.raise_for_status()
                    text = await response.text()
                    return await response.json() if text else None
            elif method == 'DELETE':
                async with session.delete(url, headers=default_headers, json=data) as response:
                    response.raise_for_status()
                    text = await response.text()
                    return await response.json() if text else None
            else:
                raise ValueError(f"Unsupported method: {method}")
    except aiohttp.ClientError as exc:
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
