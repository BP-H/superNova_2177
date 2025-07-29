"""Utility functions for communicating with the Transcendental Resonance backend."""

# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards

import asyncio
import inspect
import json
import logging
import os
from typing import (Any, Awaitable, Callable, Coroutine, Dict, List, Optional,
                    cast)

import httpx
import websockets
from nicegui import ui

# Backend API base URL
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
OFFLINE_MODE = os.getenv("OFFLINE_MODE") == "1"

logger = logging.getLogger(__name__)
logger.propagate = False

TOKEN: Optional[str] = None
WS_CONNECTION = None

# WebSocket status listeners
_ws_status_listeners: List[Callable[[str], Any]] = []

# Callbacks triggered when API requests start or finish
_start_listeners: List[Callable[[], Any]] = []
_end_listeners: List[Callable[[], Any]] = []


def on_request_start(func: Callable[[], Any]) -> None:
    """Register a callback fired before each API request."""
    _start_listeners.append(func)


def on_request_end(func: Callable[[], Any]) -> None:
    """Register a callback fired after each API request."""
    _end_listeners.append(func)


def _fire_listeners(listeners: List[Callable[[], Any]]) -> None:
    """Invoke listeners synchronously or schedule if coroutine."""
    for func in list(listeners):
        try:
            result = func()
            if inspect.isawaitable(result):
                asyncio.create_task(cast(Coroutine[Any, Any, Any], result))
        except Exception:  # pragma: no cover - best effort
            logger.exception("API event listener error")


def on_ws_status_change(func: Callable[[str], Any]) -> None:
    """Register a callback fired when WebSocket connection state changes."""
    _ws_status_listeners.append(func)


def _fire_ws_status(status: str) -> None:
    for func in list(_ws_status_listeners):
        try:
            result = func(status)
            if inspect.isawaitable(result):
                asyncio.create_task(cast(Coroutine[Any, Any, Any], result))
        except Exception:
            logger.exception("WS status listener error")


async def api_call(
    method: str,
    endpoint: str,
    data: Optional[Dict] = None,
    headers: Optional[Dict] = None,
    files: Optional[Dict] = None,
    *,
    timeout: float = 10.0,
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

    _fire_listeners(_start_listeners)
    if OFFLINE_MODE:
        logger.info("Offline mode active: skipping API call %s %s", method, endpoint)
        _fire_listeners(_end_listeners)
        return None

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
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
    except asyncio.TimeoutError:
        logger.error("API request timed out: %s %s", method, url)
        ui.notify("Request timeout", color="negative")
        if return_error:
            return {"error": "timeout", "status_code": None}
        return None
    finally:
        _fire_listeners(_end_listeners)


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


async def get_user_recommendations() -> list[Dict[str, Any]]:
    """Return a list of recommended users."""
    return cast(
        List[Dict[str, Any]], await api_call("GET", "/recommendations/users") or []
    )


async def get_group_recommendations() -> list[Dict[str, Any]]:
    """Return a list of recommended groups."""
    return cast(
        List[Dict[str, Any]], await api_call("GET", "/recommendations/groups") or []
    )


async def connect_ws(path: str = "/ws", timeout: float = 5.0):
    """Establish and return a WebSocket connection to the backend."""
    global WS_CONNECTION
    if OFFLINE_MODE:
        logger.info("Offline mode active: skipping WebSocket connection")
        _fire_ws_status("offline")
        return None
    url = BACKEND_URL.replace("http", "ws") + path
    headers = {"Authorization": f"Bearer {TOKEN}"} if TOKEN else None
    try:
        WS_CONNECTION = await asyncio.wait_for(
            websockets.connect(url, extra_headers=headers), timeout
        )
        _fire_ws_status("connected")
        return WS_CONNECTION
    except Exception as exc:  # pragma: no cover - network errors
        logger.error("WebSocket connection failed: %s", exc, exc_info=True)
        _fire_ws_status("disconnected")
        return None


async def listen_ws(
    handler: Callable[[dict], Awaitable[None]], *, reconnect: bool = True
) -> None:
    """Listen for events on the WebSocket and pass them to ``handler``."""
    global WS_CONNECTION
    if OFFLINE_MODE:
        logger.info("Offline mode active: skipping WebSocket listener")
        _fire_ws_status("offline")
        return
    retry_delay = 3
    while True:
        ws = await connect_ws()
        if ws is None:
            if not reconnect:
                return
            await asyncio.sleep(retry_delay)
            continue
        try:
            async for message in ws:
                try:
                    data = json.loads(message)
                except Exception:
                    data = {"event": "raw", "data": message}
                await handler(data)
        except Exception as exc:  # pragma: no cover - network errors
            logger.error("WebSocket listen error: %s", exc, exc_info=True)
        finally:
            if not ws.closed:
                await ws.close()
            if WS_CONNECTION is ws:
                WS_CONNECTION = None
            _fire_ws_status("disconnected")
        if not reconnect:
            break
        await asyncio.sleep(retry_delay)


async def combined_search(query: str) -> list[Dict[str, Any]]:
    """Search across users, VibeNodes, and events."""
    params = {"search": query}
    results: list[Dict[str, Any]] = []

    users = cast(List[Dict[str, Any]], await api_call("GET", "/users/", params) or [])
    for u in users:
        label = u.get("username") or u.get("name")
        if label:
            results.append({"type": "user", "label": label, "id": u.get("username")})

    vns = cast(List[Dict[str, Any]], await api_call("GET", "/vibenodes/", params) or [])
    for vn in vns:
        label = vn.get("name")
        if label:
            results.append({"type": "vibenode", "label": label, "id": vn.get("id")})

    events = cast(List[Dict[str, Any]], await api_call("GET", "/events/", params) or [])
    for ev in events:
        label = ev.get("name") or ev.get("title")
        if label:
            results.append({"type": "event", "label": label, "id": ev.get("id")})

    return results
