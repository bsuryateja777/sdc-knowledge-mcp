from __future__ import annotations

import time
from datetime import datetime, timedelta

import requests

from siemens_wiki_common.auth.base import ConfluenceAuthProvider
from siemens_wiki_common.models import ConfluencePage

_EXPAND = "body.storage,version,space,ancestors,metadata.labels"


def _to_cql_datetime(iso_str: str) -> str:
    """Confluence CQL wants "yyyy-MM-dd HH:mm"; our stored last_modified
    values are ISO-8601 (e.g. "2026-09-18T10:47:29Z") with second precision.

    Rounds up to the next minute before truncating so the most-recently
    -indexed page's own minute is excluded from the next incremental query --
    without this, `lastModified > "<its minute>:00"` still matches that page's
    real timestamp (which has non-zero seconds), causing it to be re-crawled
    on every single incremental run forever."""
    dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00")) + timedelta(minutes=1)
    return dt.strftime("%Y-%m-%d %H:%M")


class ConfluenceClient:
    def __init__(self, base_url: str, auth: ConfluenceAuthProvider, timeout: int = 30):
        self._base_url = base_url.rstrip("/")
        self._auth = auth
        self._timeout = timeout

    def _get(self, path: str, params: dict) -> dict:
        url = f"{self._base_url}{path}"
        resp = requests.get(
            url, headers=self._auth.get_headers(), params=params, timeout=self._timeout
        )
        if resp.status_code in (401, 403):
            self._auth.refresh()
        resp.raise_for_status()
        return resp.json()

    def get_page(self, page_id: str) -> ConfluencePage:
        data = self._get(f"/rest/api/content/{page_id}", {"expand": _EXPAND})
        return self._page_from_json(data)

    def search_descendants(
        self,
        space_key: str,
        root_page_id: str,
        limit: int = 50,
        polite_delay: float = 0.3,
        modified_since: str | None = None,
    ) -> list[ConfluencePage]:
        """modified_since (ISO-8601, e.g. a stored last_modified value) restricts
        to pages changed after that point -- pass None for a full crawl."""
        pages: list[ConfluencePage] = []
        start = 0
        cql = f'space="{space_key}" AND type=page AND ancestor={root_page_id}'
        if modified_since:
            cql += f' AND lastModified > "{_to_cql_datetime(modified_since)}"'
        while True:
            data = self._get(
                "/rest/api/content/search",
                {"cql": cql, "expand": _EXPAND, "limit": limit, "start": start},
            )
            results = data.get("results", [])
            pages.extend(self._page_from_json(r) for r in results)
            total = data.get("totalSize", len(results))
            if start + limit >= total:
                break
            start += limit
            time.sleep(polite_delay)
        return pages

    def _page_from_json(self, data: dict) -> ConfluencePage:
        labels = [
            label["name"]
            for label in data.get("metadata", {}).get("labels", {}).get("results", [])
        ]
        ancestors = [a.get("title", "") for a in data.get("ancestors", [])]
        space = data.get("space", {})
        version = data.get("version", {})
        links = data.get("_links", {})
        base = links.get("base", self._base_url)
        webui = links.get("webui", "")
        return ConfluencePage(
            id=data["id"],
            title=data.get("title", ""),
            space_key=space.get("key", ""),
            space_name=space.get("name", ""),
            body_storage=data.get("body", {}).get("storage", {}).get("value", ""),
            version_number=version.get("number", 0),
            last_modified=version.get("when"),
            labels=labels,
            ancestors=ancestors,
            source_url=f"{base}{webui}" if webui else f"{self._base_url}/pages/viewpage.action?pageId={data['id']}",
        )
