import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

import notion_lib as n


class FakeResponse:
    def __init__(self, status_code, json_data=None, headers=None):
        self.status_code = status_code
        self._json = json_data or {}
        self.headers = headers or {}

    def json(self):
        return self._json

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")


class FakeSession:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = 0

    def request(self, method, url, **kwargs):
        self.calls += 1
        return self.responses.pop(0)


def _no_sleep(monkeypatch):
    sleeps = []
    monkeypatch.setattr(n.time, "sleep", lambda s: sleeps.append(s))
    return sleeps


def test_succeeds_first_try(monkeypatch):
    sleeps = _no_sleep(monkeypatch)
    session = FakeSession([FakeResponse(200, {"ok": True})])
    r = n._request("GET", "https://example.com", session=session)
    assert r.json() == {"ok": True}
    assert session.calls == 1
    assert sleeps == []


def test_retries_on_429_then_succeeds(monkeypatch):
    sleeps = _no_sleep(monkeypatch)
    session = FakeSession([FakeResponse(429), FakeResponse(200, {"ok": True})])
    r = n._request("GET", "https://example.com", session=session)
    assert r.json() == {"ok": True}
    assert session.calls == 2
    assert sleeps == [1]


def test_retries_on_5xx_with_exponential_backoff(monkeypatch):
    sleeps = _no_sleep(monkeypatch)
    session = FakeSession([
        FakeResponse(500), FakeResponse(502), FakeResponse(200, {"ok": True}),
    ])
    r = n._request("GET", "https://example.com", session=session)
    assert r.json() == {"ok": True}
    assert sleeps == [1, 2]


def test_honours_retry_after_header(monkeypatch):
    sleeps = _no_sleep(monkeypatch)
    session = FakeSession([
        FakeResponse(429, headers={"Retry-After": "7"}),
        FakeResponse(200, {"ok": True}),
    ])
    n._request("GET", "https://example.com", session=session)
    assert sleeps == [7]


def test_raises_after_max_retries(monkeypatch):
    sleeps = _no_sleep(monkeypatch)
    session = FakeSession([FakeResponse(500)] * 5)
    try:
        n._request("GET", "https://example.com", session=session)
        raised = False
    except RuntimeError:
        raised = True
    assert raised
    assert session.calls == n.MAX_RETRIES + 1
    assert sleeps == [1, 2, 4]


def test_does_not_retry_on_non_retryable_error(monkeypatch):
    sleeps = _no_sleep(monkeypatch)
    session = FakeSession([FakeResponse(404)])
    try:
        n._request("GET", "https://example.com", session=session)
        raised = False
    except RuntimeError:
        raised = True
    assert raised
    assert session.calls == 1
    assert sleeps == []
