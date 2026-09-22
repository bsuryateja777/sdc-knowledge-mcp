from __future__ import annotations

from siemens_wiki_common.auth.base import ConfluenceAuthProvider


class CookieAuthProvider(ConfluenceAuthProvider):
    """JSESSIONID cookie auth. Short-lived (8-24h) stopgap until a PAT or
    service account is granted for wiki.siemens.com."""

    def __init__(self, jsessionid: str):
        if not jsessionid:
            raise ValueError(
                "WIKI_JSESSIONID is empty. Grab a fresh cookie from browser DevTools "
                "(Application > Cookies > wiki.siemens.com) and set it in .env."
            )
        self._jsessionid = jsessionid

    def get_headers(self) -> dict[str, str]:
        return {
            "Cookie": f"JSESSIONID={self._jsessionid}",
            "Accept": "application/json",
        }

    def refresh(self) -> None:
        raise RuntimeError(
            "JSESSIONID appears to have expired (401/403 from wiki.siemens.com). "
            "Grab a fresh cookie from browser DevTools and update WIKI_JSESSIONID in .env."
        )
