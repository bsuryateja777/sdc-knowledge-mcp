from siemens_wiki_common.auth.cookie_auth import CookieAuthProvider
from siemens_wiki_common.confluence_client import ConfluenceClient


def _client() -> ConfluenceClient:
    return ConfluenceClient(base_url="https://wiki.siemens.com", auth=CookieAuthProvider("x"))


def test_source_url_uses_links_base_and_webui_when_present():
    data = {
        "id": "295931756",
        "title": "Siemens Data & AI Cloud",
        "_links": {"base": "https://wiki.siemens.com", "webui": "/spaces/en/pages/295931756/Foo"},
    }
    page = _client()._page_from_json(data)
    assert page.source_url == "https://wiki.siemens.com/spaces/en/pages/295931756/Foo"


def test_source_url_falls_back_to_client_base_url_when_links_base_missing():
    data = {
        "id": "295931756",
        "title": "Siemens Data & AI Cloud",
        "_links": {"webui": "/spaces/en/pages/295931756/Foo"},
    }
    page = _client()._page_from_json(data)
    assert page.source_url == "https://wiki.siemens.com/spaces/en/pages/295931756/Foo"


def test_source_url_falls_back_to_viewpage_action_when_no_webui():
    data = {"id": "295931756", "title": "Siemens Data & AI Cloud", "_links": {}}
    page = _client()._page_from_json(data)
    assert page.source_url == "https://wiki.siemens.com/pages/viewpage.action?pageId=295931756"


def test_source_url_uses_a_different_instances_own_base_url():
    client = ConfluenceClient(
        base_url="https://confluence.ct.daai.siemens.cloud", auth=CookieAuthProvider("x")
    )
    data = {
        "id": "595283402",
        "title": "38. SDC Lake",
        "_links": {
            "base": "https://confluence.ct.daai.siemens.cloud",
            "webui": "/spaces/SDCOPSL1/pages/595283402/38.+SDC+Lake",
        },
    }
    page = client._page_from_json(data)
    assert page.source_url == "https://confluence.ct.daai.siemens.cloud/spaces/SDCOPSL1/pages/595283402/38.+SDC+Lake"
