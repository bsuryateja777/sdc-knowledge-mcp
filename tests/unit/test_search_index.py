from siemens_wiki_common.config import Settings
from siemens_wiki_common.search_index import SearchIndexClient


def _client() -> SearchIndexClient:
    settings = Settings(azure_search_endpoint="https://example.search.windows.net", azure_search_key="x")
    return SearchIndexClient(settings, index_name="test-index")


def test_get_full_page_rejects_non_numeric_page_id_without_network_call():
    # A malicious/malformed page_id must be rejected before ever building an
    # OData filter string with it -- this must not raise or hit the network.
    assert _client().get_full_page("1' or '1' eq '1") is None


def test_get_full_page_rejects_empty_page_id():
    assert _client().get_full_page("") is None
