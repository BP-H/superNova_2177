"""Remote ping and handshake helpers."""
import requests

DEFAULT_TIMEOUT = 5.0


def ping_agent(url: str, timeout: float = DEFAULT_TIMEOUT) -> bool:
    """Return ``True`` if the remote agent responds within ``timeout`` seconds."""

    try:
        res = requests.get(f"{url}/status", timeout=timeout)
        return res.status_code == 200
    except Exception:
        return False


def handshake(agent_id: str, url: str, timeout: float = DEFAULT_TIMEOUT) -> dict:
    """Return handshake information including ping status."""

    return {"agent_id": agent_id, "remote_status": ping_agent(url, timeout=timeout)}
