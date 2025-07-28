"""Remote ping and handshake helpers."""

import requests  # type: ignore


def ping_agent(url: str, timeout: float = 5.0) -> bool:
    """Return ``True`` if the remote agent responds within ``timeout`` seconds."""

    try:
        res = requests.get(f"{url}/status", timeout=timeout)
        return res.status_code == 200
    except requests.Timeout:
        return False
    except Exception:
        return False


def handshake(agent_id: str, url: str, timeout: float = 5.0) -> dict:
    """Return handshake information including ping status."""

    return {"agent_id": agent_id, "remote_status": ping_agent(url, timeout=timeout)}
