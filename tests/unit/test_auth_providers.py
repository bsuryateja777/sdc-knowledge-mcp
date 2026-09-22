import pytest

from siemens_wiki_common.auth.base import ConfluenceAuthProvider
from siemens_wiki_common.auth.cookie_auth import CookieAuthProvider
from siemens_wiki_common.auth.factory import get_auth_provider
from siemens_wiki_common.auth.pat_auth import PATAuthProvider
from siemens_wiki_common.config import ConfluenceInstance


def test_cookie_provider_sets_cookie_header():
    provider = CookieAuthProvider("abc123")
    headers = provider.get_headers()
    assert headers["Cookie"] == "JSESSIONID=abc123"


def test_cookie_provider_rejects_empty_value():
    with pytest.raises(ValueError):
        CookieAuthProvider("")


def test_cookie_provider_refresh_raises_actionable_error():
    provider = CookieAuthProvider("abc123")
    with pytest.raises(RuntimeError):
        provider.refresh()


def test_pat_provider_sets_bearer_header():
    provider = PATAuthProvider("token-xyz")
    headers = provider.get_headers()
    assert headers["Authorization"] == "Bearer token-xyz"


def test_both_providers_satisfy_the_interface():
    assert isinstance(CookieAuthProvider("x"), ConfluenceAuthProvider)
    assert isinstance(PATAuthProvider("x"), ConfluenceAuthProvider)


def test_factory_selects_cookie_strategy():
    instance = ConfluenceInstance(
        name="wiki", base_url="https://x", auth_strategy="cookie",
        jsessionid="abc123", pat="", index_name="idx",
    )
    provider = get_auth_provider(instance)
    assert isinstance(provider, CookieAuthProvider)


def test_factory_selects_pat_strategy():
    instance = ConfluenceInstance(
        name="wiki", base_url="https://x", auth_strategy="pat",
        jsessionid="", pat="token-xyz", index_name="idx",
    )
    provider = get_auth_provider(instance)
    assert isinstance(provider, PATAuthProvider)


def test_factory_rejects_unknown_strategy():
    instance = ConfluenceInstance(
        name="wiki", base_url="https://x", auth_strategy="bogus",
        jsessionid="", pat="", index_name="idx",
    )
    with pytest.raises(ValueError):
        get_auth_provider(instance)
