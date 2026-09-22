from __future__ import annotations

import dataclasses
import json
from pathlib import Path

from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient as _AzureSearchIndexClient
from azure.search.documents.indexes.models import (
    HnswAlgorithmConfiguration,
    HnswParameters,
    SearchField,
    SearchFieldDataType,
    SearchIndex,
    VectorSearch,
    VectorSearchProfile,
)
from azure.search.documents.models import VectorizedQuery

from siemens_wiki_common.config import Settings
from siemens_wiki_common.models import SearchDocument
from siemens_wiki_common.resilience import retry_transient

SCHEMA_PATH = Path(__file__).with_name("schema.json")

_UPLOAD_BATCH_SIZE = 100


def load_schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def ensure_index(settings: Settings, index_name: str | None = None) -> None:
    """Idempotent create-or-update of an Azure AI Search index from schema.json.
    Defaults to settings.azure_search_index; pass index_name to target a
    different index (e.g. a second Confluence instance's own index)."""
    schema = load_schema()
    dims = settings.ai_foundry_embed_dimensions
    index_name = index_name or settings.azure_search_index

    client = _AzureSearchIndexClient(
        endpoint=settings.azure_search_endpoint,
        credential=AzureKeyCredential(settings.azure_search_key),
    )

    fields = []
    for f in schema["fields"]:
        if f["name"] == "embedding":
            fields.append(
                SearchField(
                    name="embedding",
                    type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                    vector_search_dimensions=dims,
                    vector_search_profile_name=f["vectorSearchProfile"],
                    searchable=True,
                    retrievable=f.get("retrievable", False),
                )
            )
        else:
            fields.append(
                SearchField(
                    name=f["name"],
                    type=_edm_type(f["type"]),
                    key=f.get("key", False),
                    searchable=f.get("searchable", False),
                    filterable=f.get("filterable", False),
                    sortable=f.get("sortable", False),
                    retrievable=f.get("retrievable", True),
                )
            )

    vector_search = VectorSearch(
        profiles=[
            VectorSearchProfile(name="hnsw-profile", algorithm_configuration_name="hnsw-config")
        ],
        algorithms=[HnswAlgorithmConfiguration(name="hnsw-config", parameters=HnswParameters())],
    )

    index = SearchIndex(
        name=index_name,
        fields=fields,
        vector_search=vector_search,
    )
    client.create_or_update_index(index)


def _edm_type(type_str: str) -> str:
    if type_str.startswith("Collection(") and type_str.endswith(")"):
        inner = type_str[len("Collection(") : -1]
        return f"Collection({inner})"
    return type_str


class SearchIndexClient:
    """Thin wrapper around azure.search.documents.SearchClient with a small
    staging buffer so callers can `stage()` many docs and `flush()` in batches."""

    def __init__(self, settings: Settings, index_name: str | None = None):
        self._client = SearchClient(
            endpoint=settings.azure_search_endpoint,
            index_name=index_name or settings.azure_search_index,
            credential=AzureKeyCredential(settings.azure_search_key),
        )
        self._buffer: list[dict] = []

    def stage(self, doc: SearchDocument) -> None:
        self._buffer.append(dataclasses.asdict(doc))
        if len(self._buffer) >= _UPLOAD_BATCH_SIZE:
            self.flush()

    def flush(self) -> None:
        if not self._buffer:
            return
        self._client.upload_documents(documents=self._buffer)
        self._buffer = []

    def delete_page(self, page_id: str) -> None:
        """Delete every existing chunk-document for a page before re-ingesting
        it. Without this, a page that shrinks (fewer chunks after an edit)
        would leave stale extra chunks behind forever, since upload_documents
        only upserts by id -- it never removes documents that are no longer
        produced. No-op if the page has nothing indexed yet."""
        if not page_id.isdigit():
            return
        existing = retry_transient(
            lambda: list(
                self._client.search(
                    search_text="*",
                    filter=f"page_id eq '{page_id}'",
                    select=["id"],
                    top=1000,
                )
            ),
            label="delete_page.lookup",
        )
        if not existing:
            return
        retry_transient(
            lambda: self._client.delete_documents(documents=[{"id": r["id"]} for r in existing]),
            label="delete_page.delete",
        )

    def get_latest_modified(self, space_key: str) -> str | None:
        """Max last_modified already indexed for a space, used as the CQL
        incremental-sync cutoff. None means nothing indexed yet for this
        space (caller should do a full crawl)."""
        rows = retry_transient(
            lambda: list(
                self._client.search(
                    search_text="*",
                    filter=f"space_key eq '{space_key}'",
                    select=["last_modified"],
                    order_by=["last_modified desc"],
                    top=1,
                )
            ),
            label="get_latest_modified",
        )
        if not rows:
            return None
        return str(rows[0].get("last_modified") or "") or None

    def hybrid_search(self, query: str, embedding: list[float], top_k: int = 5) -> list[dict]:
        """Keyword + vector hybrid search over the index.

        Each result includes page_id, chunk_index, and total_chunks_in_page so
        a calling agent can decide whether this chunk is enough or whether it
        should call get_full_page(page_id) for the rest of that page.
        """
        vector_query = VectorizedQuery(
            vector=embedding, k_nearest_neighbors=top_k, fields="embedding"
        )

        def _call():
            return list(
                self._client.search(
                    search_text=query,
                    vector_queries=[vector_query],
                    select=[
                        "page_id", "title", "content", "chunk_index",
                        "source_url", "space_name", "labels", "last_modified",
                    ],
                    top=top_k,
                )
            )

        results = retry_transient(_call, label="hybrid_search")

        page_ids = sorted({r["page_id"] for r in results})
        chunk_counts = self._count_chunks_per_page(page_ids)

        return [
            {
                "page_id": r.get("page_id", ""),
                "title": r.get("title", ""),
                "content": r.get("content", ""),
                "chunk_index": r.get("chunk_index", 0),
                "total_chunks_in_page": chunk_counts.get(r.get("page_id", ""), 1),
                "source_url": r.get("source_url", ""),
                "space": r.get("space_name", ""),
                "labels": r.get("labels", []),
                "last_modified": str(r.get("last_modified", "")),
            }
            for r in results
        ]

    def _count_chunks_per_page(self, page_ids: list[str]) -> dict[str, int]:
        """One batched query to count how many chunks each page has, so
        hybrid_search results can tell an agent whether more content exists."""
        if not page_ids:
            return {}
        ids_csv = ",".join(page_ids)
        rows = retry_transient(
            lambda: list(
                self._client.search(
                    search_text="*",
                    filter=f"search.in(page_id, '{ids_csv}', ',')",
                    select=["page_id"],
                    top=1000,
                )
            ),
            label="count_chunks_per_page",
        )
        counts: dict[str, int] = {}
        for r in rows:
            pid = r["page_id"]
            counts[pid] = counts.get(pid, 0) + 1
        return counts

    def get_full_page(self, page_id: str) -> dict | None:
        """Reconstruct a page's full content from its stored chunks (already
        ingested, no live Confluence call). Returns None if page_id isn't in
        this index or isn't a valid Confluence page ID."""
        if not page_id.isdigit():
            # Confluence page IDs are always numeric; reject anything else
            # rather than interpolating untrusted input into an OData filter.
            return None
        rows = retry_transient(
            lambda: list(
                self._client.search(
                    search_text="*",
                    filter=f"page_id eq '{page_id}'",
                    select=[
                        "page_id", "title", "chunk_index", "content", "source_url",
                        "space_key", "space_name", "labels", "last_modified",
                        "version_number", "ancestors",
                    ],
                    top=1000,
                )
            ),
            label="get_full_page",
        )
        if not rows:
            return None
        rows.sort(key=lambda r: r["chunk_index"])

        first = rows[0]
        full_content = " ".join(r["content"] for r in rows)
        return {
            "page_id": page_id,
            "title": first.get("title", ""),
            "content": full_content,
            "chunk_count": len(rows),
            "source_url": first.get("source_url", ""),
            "space": first.get("space_name", ""),
            "space_key": first.get("space_key", ""),
            "labels": first.get("labels", []),
            "last_modified": str(first.get("last_modified", "")),
            "version_number": first.get("version_number", 0),
            "ancestors": first.get("ancestors", []),
        }
