import requests
import protocols.utils.remote as remote


def test_ping_agent_uses_timeout(monkeypatch):
    called = {}

    def fake_get(url, timeout=None):
        called['url'] = url
        called['timeout'] = timeout
        class Response:
            status_code = 200
        return Response()

    monkeypatch.setattr(requests, "get", fake_get)
    assert remote.ping_agent("http://example.com") is True
    assert called['url'] == "http://example.com/status"
    assert called['timeout'] == 5.0


def test_ping_agent_custom_timeout(monkeypatch):
    called = {}

    def fake_get(url, timeout=None):
        called['timeout'] = timeout
        class Response:
            status_code = 200
        return Response()

    monkeypatch.setattr(requests, "get", fake_get)
    assert remote.ping_agent("http://example.com", timeout=2.5)
    assert called['timeout'] == 2.5


def test_handshake_passes_timeout(monkeypatch):
    def fake_ping(url, timeout=5.0):
        fake_ping.called_timeout = timeout
        return True

    monkeypatch.setattr(remote, "ping_agent", fake_ping)
    result = remote.handshake("agent42", "http://example.com", timeout=3)
    assert result == {"agent_id": "agent42", "remote_status": True}
    assert fake_ping.called_timeout == 3


def test_ping_agent_handles_timeout(monkeypatch):
    def fake_get(url, timeout=None):
        raise requests.exceptions.Timeout

    monkeypatch.setattr(requests, "get", fake_get)
    assert remote.ping_agent("http://example.com") is False

