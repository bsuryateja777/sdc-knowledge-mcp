from __future__ import annotations

import logging
import time

from siemens_wiki_common.config import Settings, get_instance, get_settings
from siemens_wiki_common.embeddings import FoundryEmbedder
from siemens_wiki_common.search_index import SearchIndexClient

# Pure tool logic: no `mcp`/FastMCP imports here. This is what keeps the
# search behavior usable by any future MCP client (Claude Code now, a
# chatbot later) via a plain, stable, JSON-serializable return shape.

logger = logging.getLogger(__name__)

_settings: Settings | None = None
_embedder: FoundryEmbedder | None = None
_indexes: dict[str, SearchIndexClient] = {}

# Guardrails: keep a misbehaving/abusive caller from running up embedding
# costs or hammering the index with an unbounded top_k.
MAX_TOP_K = 20
MAX_QUERY_LENGTH = 500


def _get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = get_settings()
    return _settings


def _get_embedder() -> FoundryEmbedder:
    global _embedder
    if _embedder is None:
        _embedder = FoundryEmbedder(_get_settings())
    return _embedder


def _get_index(instance_name: str) -> SearchIndexClient:
    if instance_name not in _indexes:
        settings = _get_settings()
        instance = get_instance(settings, instance_name)
        _indexes[instance_name] = SearchIndexClient(settings, index_name=instance.index_name)
    return _indexes[instance_name]


def _clamp_inputs(query: str, top_k: int) -> tuple[str, int]:
    query = (query or "").strip()[:MAX_QUERY_LENGTH]
    top_k = max(1, min(top_k, MAX_TOP_K))
    return query, top_k


def _search(instance_name: str, query: str, top_k: int) -> dict:
    query, top_k = _clamp_inputs(query, top_k)
    if not query:
        return {"results": [], "sources": [], "error": "query must not be empty"}

    start = time.perf_counter()
    try:
        embedder = _get_embedder()
        index = _get_index(instance_name)
        embedding = embedder.embed(query)
        results = index.hybrid_search(query, embedding, top_k=top_k)
    except Exception:
        logger.exception("search failed instance=%s query=%r top_k=%d", instance_name, query, top_k)
        return {
            "results": [],
            "sources": [],
            "error": "search is temporarily unavailable, please try again shortly",
        }

    elapsed = time.perf_counter() - start
    logger.info(
        "search instance=%s query=%r top_k=%d result_count=%d elapsed=%.2fs",
        instance_name, query, top_k, len(results), elapsed,
    )

    seen: set[str] = set()
    sources: list[dict] = []
    for r in results:
        url = r["source_url"]
        if url not in seen:
            seen.add(url)
            sources.append({"title": r["title"], "source_url": url})

    return {"results": results, "sources": sources}


def search_siemens_wiki(query: str, top_k: int = 5) -> dict:
    """Search the Siemens Wikisphere (wiki.siemens.com) knowledge base.

    Covers SDC product documentation (SDC Marketplace, Data Products,
    Snowflake, dbt, etc.) and the ai:attack Azure platform's public wiki
    pages. Does NOT cover DAAI internal ops/support runbooks -- use
    search_sdc_ops_confluence for those.
    """
    return _search("wiki", query, top_k)


def search_sdc_ops_confluence(query: str, top_k: int = 5) -> dict:
    """Search the DAAI internal Confluence knowledge base
    (confluence.ct.daai.siemens.cloud).

    Covers SDC Operations L1 Support runbooks (per-platform troubleshooting:
    Snowflake, PowerBI, Neo4j, ERP Data Ingest, etc.), the Aiattack on Azure
    platform's internal ops docs (including concrete admin/config guides like
    enabling Azure SQL auto-pause), and Neo4j service operations. Use this for
    "how do I configure/enable/troubleshoot X" operational questions -- this
    index has hands-on admin guides that the public wiki does not.
    """
    return _search("confluence", query, top_k)


def get_full_page(page_id: str) -> dict:
    """Fetch a page's complete content by page_id (from a previous search
    result), reassembled from its stored chunks in order -- use this when a
    search result's chunk isn't enough context and you need the whole page.

    Checks both the wiki and confluence indexes since page_id alone doesn't
    say which one it came from. Returns {"found": False} if the ID isn't in
    either index.
    """
    page_id = (page_id or "").strip()
    for instance_name in ("wiki", "confluence"):
        try:
            page = _get_index(instance_name).get_full_page(page_id)
        except Exception:
            logger.exception("get_full_page failed instance=%s page_id=%r", instance_name, page_id)
            return {"found": False, "page_id": page_id, "error": "lookup is temporarily unavailable, please try again shortly"}
        if page is not None:
            page["found"] = True
            page["instance"] = instance_name
            logger.info("get_full_page instance=%s page_id=%s chunk_count=%d", instance_name, page_id, page["chunk_count"])
            return page
    return {"found": False, "page_id": page_id}
