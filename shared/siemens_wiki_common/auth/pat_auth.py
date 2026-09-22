from __future__ import annotations

from siemens_wiki_common.auth.base import ConfluenceAuthProvider


class PATAuthProvider(ConfluenceAuthProvider):
    """Personal Access Token auth. Activate once wikisphere@siemens.com grants
    a PAT or service account: set WIKI_AUTH_STRATEGY=pat and WIKI_PAT=<token>."""

    def __init__(self, token: str):
        if not token:
            raise ValueError("WIKI_PAT is empty but WIKI_AUTH_STRATEGY=pat.")
        self._token = token

    def get_headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self._token}",
            "Accept": "application/json",
        }

    def refresh(self) -> None:
        raise RuntimeError(
            "PAT rejected (401/403) from wiki.siemens.com. It may have been revoked; "
            "generate a new one at /plugins/personalaccesstokens/usertokens.action."
        )
