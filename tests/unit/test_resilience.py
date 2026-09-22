import pytest
from azure.core.exceptions import HttpResponseError

from siemens_wiki_common.resilience import retry_transient


class RateLimitError(Exception):
    """Stands in for openai.RateLimitError -- resilience.py matches by class
    name only, so it doesn't need an openai import/dependency."""


def test_retries_on_transient_http_error_and_eventually_succeeds():
    calls = {"n": 0}

    def flaky():
        calls["n"] += 1
        if calls["n"] < 3:
            raise HttpResponseError(message="server hiccup", response=_response(503))
        return "ok"

    result = retry_transient(flaky, max_attempts=3, base_delay=0.01)
    assert result == "ok"
    assert calls["n"] == 3


def test_raises_immediately_on_non_transient_http_error():
    calls = {"n": 0}

    def bad_request():
        calls["n"] += 1
        raise HttpResponseError(message="bad input", response=_response(400))

    with pytest.raises(HttpResponseError):
        retry_transient(bad_request, max_attempts=3, base_delay=0.01)
    assert calls["n"] == 1  # never retried


def test_retries_on_transient_error_matched_by_class_name():
    calls = {"n": 0}

    def flaky():
        calls["n"] += 1
        if calls["n"] < 2:
            raise RateLimitError("rate limited")
        return "ok"

    assert retry_transient(flaky, max_attempts=3, base_delay=0.01) == "ok"
    assert calls["n"] == 2


def test_gives_up_after_max_attempts():
    def always_fails():
        raise HttpResponseError(message="down", response=_response(503))

    with pytest.raises(HttpResponseError):
        retry_transient(always_fails, max_attempts=2, base_delay=0.01)


class _FakeResponse:
    def __init__(self, status_code: int):
        self.status_code = status_code
        self.headers = {}
        self.reason = "error"
        self.content_type = "application/json"

    def body(self):
        return b"{}"

    def text(self, encoding=None):
        return "{}"


def _response(status_code: int) -> _FakeResponse:
    return _FakeResponse(status_code)
