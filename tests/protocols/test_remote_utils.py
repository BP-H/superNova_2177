# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards
import requests  # type: ignore

import protocols.utils.remote as remote


def test_ping_agent_uses_timeout(monkeypatch):
    called = {}

    def fake_get(url, timeout=None):
        called["url"] = url
        called["timeout"] = timeout

        class Response:
            status_code = 200

        return Response()

    monkeypatch.setattr(requests, "get", fake_get)
    assert remote.ping_agent("http://example.com") is True  # nosec B101
    assert called["url"] == "http://example.com/status"  # nosec B101
    assert called["timeout"] == 5.0  # nosec B101


def test_ping_agent_custom_timeout(monkeypatch):
    called = {}

    def fake_get(url, timeout=None):
        called["timeout"] = timeout

        class Response:
            status_code = 200

        return Response()

    monkeypatch.setattr(requests, "get", fake_get)
    assert remote.ping_agent("http://example.com", timeout=2.5)  # nosec B101
    assert called["timeout"] == 2.5  # nosec B101


def test_ping_agent_timeout_exception(monkeypatch):
    def fake_get(url, timeout=None):
        raise requests.Timeout

    monkeypatch.setattr(requests, "get", fake_get)
    assert remote.ping_agent("http://example.com") is False  # nosec B101


def test_handshake_passes_timeout(monkeypatch):
    def fake_ping(url, timeout=5.0):
        fake_ping.called_timeout = timeout
        return True

    monkeypatch.setattr(remote, "ping_agent", fake_ping)
    result = remote.handshake("agent42", "http://example.com", timeout=3)
    assert result == {"agent_id": "agent42", "remote_status": True}  # nosec B101
    assert fake_ping.called_timeout == 3  # nosec B101
