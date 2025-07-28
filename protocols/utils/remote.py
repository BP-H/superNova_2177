"""Remote ping and handshake helpers."""
import requests


def ping_agent(url: str) -> bool:
    try:
        res = requests.get(f"{url}/status")
        return res.status_code == 200
    except Exception:
        return False


def handshake(agent_id: str, url: str) -> dict:
    return {"agent_id": agent_id, "remote_status": ping_agent(url)}
