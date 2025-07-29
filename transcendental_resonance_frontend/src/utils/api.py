"""Utility functions for communicating with the Transcendental Resonance backend."""

import json
import logging
import os
from typing import Any, Awaitable, Callable, Dict, Optional, List

import inspect
import asyncio

import httpx
import websockets
from nicegui import ui

# Backend API base URL
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
# When running in offline mode, network calls should be skipped
OFFLINE_MODE: bool = os.getenv("OFFLINE_MODE", "0") == "1"

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
                asyncio.create_task(result)
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
                asyncio.create_task(result)
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
        logger.info("Offline mode: %s %s skipped", method, endpoint)
        try:
            ui.notify("Offline mode: request skipped", color="warning")
        except Exception:
            pass
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
    except httpx.HTTPStatusError as exc:
        status = exc.response.status_code if exc.response else None
        logger.error(
            "API returned HTTP %s for %s %s - %s",
            status,
            method,
            url,
            exc,
            exc_info=True,
        )
        ui.notify(f"API error {status}", color="negative")
        if return_error:
            body = None
            try:
                body = exc.response.json()
            except Exception:
                body = exc.response.text if exc.response else None
            return {"error": str(exc), "status_code": status, "body": body}
        return None
    except httpx.RequestError as exc:
        logger.error(
            "API request failed: %s %s - %s", method, url, exc, exc_info=True
        )
        ui.notify("API request failed", color="negative")
        if return_error:
            return {
                "error": str(exc),
                "status_code": getattr(getattr(exc, "response", None), "status_code", None),
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
    return await api_call("GET", "/recommendations/users") or []


async def get_group_recommendations() -> list[Dict[str, Any]]:
    """Return a list of recommended groups."""
    return await api_call("GET", "/recommendations/groups") or []


async def connect_ws(path: str = "/ws", timeout: float = 5.0):
    """Establish and return a WebSocket connection to the backend."""
    global WS_CONNECTION
    url = BACKEND_URL.replace("http", "ws") + path
    headers = {"Authorization": f"Bearer {TOKEN}"} if TOKEN else None
    if OFFLINE_MODE:
        logger.info("Offline mode: skipping WebSocket connection to %s", url)
        _fire_ws_status("disconnected")
        return None
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


def listen_ws(
    handler: Callable[[dict], Awaitable[None]], *, reconnect: bool = True
async def listen_ws(
    handler: Callable[[dict], Awaitable[None]], *, reconnect: bool = True
) -> asyncio.Task:
    """Start listening for WebSocket events and return the ``asyncio`` task."""

    async def _listen() -> None:
        global WS_CONNECTION
        retry_delay = 3
        if OFFLINE_MODE:
            _fire_ws_status("disconnected")
            return
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

    return asyncio.create_task(_listen())

            if not reconnect:
                break
            await asyncio.sleep(retry_delay)

    return asyncio.create_task(_listen())


async def combined_search(query: str) -> list[Dict[str, Any]]:
    """Search across users, VibeNodes, and events."""
    params = {"search": query}
    results: list[Dict[str, Any]] = []

    users = await api_call("GET", "/users/", params) or []
    for u in users:
        label = u.get("username") or u.get("name")
        if label:
            results.append({"type": "user", "label": label, "id": u.get("username")})

    vns = await api_call("GET", "/vibenodes/", params) or []
    for vn in vns:
        label = vn.get("name")
        if label:
            results.append({"type": "vibenode", "label": label, "id": vn.get("id")})

    events = await api_call("GET", "/events/", params) or []
    for ev in events:
        label = ev.get("name") or ev.get("title")
        if label:
            results.append({"type": "event", "label": label, "id": ev.get("id")})

    return results
