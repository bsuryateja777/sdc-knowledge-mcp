from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from itertools import groupby

from siemens_wiki_common.auth.factory import get_auth_provider
from siemens_wiki_common.chunking import chunk_text
from siemens_wiki_common.confluence_client import ConfluenceClient
from siemens_wiki_common.config import Settings, get_instance
from siemens_wiki_common.documents import build_search_document
from siemens_wiki_common.embeddings import FoundryEmbedder
from siemens_wiki_common.models import WikiSource
from siemens_wiki_common.parsing import parse_confluence_storage
from siemens_wiki_common.search_index import SearchIndexClient

logger = logging.getLogger(__name__)


@dataclass
class IngestionSummary:
    pages_processed: int = 0
    pages_skipped_empty: int = 0
    chunks_indexed: int = 0


def run_ingestion(
    sources: list[WikiSource],
    settings: Settings,
    limit: int | None = None,
    dry_run: bool = False,
    force_full: bool = False,
) -> IngestionSummary:
    """Fetch pages for each source, parse/chunk/embed/upsert into Azure AI Search.

    Sources are grouped by their `instance` (see config.get_instance) so each
    Confluence instance uses its own base URL, auth, and target search index.
    Has zero azure.functions imports so it can be called directly from a local
    CLI (scripts/run_ingestion_local.py) or from the Function App's triggers.

    Incremental by default: for each source, only pages modified since the
    latest last_modified already indexed for that space are re-crawled (the
    index itself is the source of truth for "what have we already ingested" --
    no separate state file/storage needed). Pass force_full=True to bypass
    this and re-crawl everything, which is also what happens automatically
    the first time a space has nothing indexed yet.

    NOTE: incremental sync only catches additions/edits, not deletions -- a
    page removed from Confluence stays in the index until a force_full run
    (or a future explicit reconciliation) removes it. Run force_full
    periodically to catch drift.
    """
    embedder = None if dry_run else FoundryEmbedder(settings)
    summary = IngestionSummary()

    sorted_sources = sorted(sources, key=lambda s: s.instance)
    for instance_name, group in groupby(sorted_sources, key=lambda s: s.instance):
        instance = get_instance(settings, instance_name)
        auth = get_auth_provider(instance)
        client = ConfluenceClient(
            base_url=instance.base_url, auth=auth, cql_timezone=instance.cql_timezone
        )
        index = None if dry_run else SearchIndexClient(settings, index_name=instance.index_name)

        for source in group:
            modified_since = None
            if not force_full and index is not None:
                modified_since = index.get_latest_modified(source.space_key)
            logger.info(
                "crawling source instance=%s space=%s root=%s mode=%s",
                instance_name, source.space_key, source.root_page_id,
                "full" if not modified_since else f"incremental since {modified_since}",
            )

            pages = client.search_descendants(
                source.space_key, source.root_page_id, modified_since=modified_since
            )
            if limit is not None:
                pages = pages[:limit]

            for page in pages:
                text = parse_confluence_storage(page.body_storage)
                if not text:
                    summary.pages_skipped_empty += 1
                    continue

                if index is not None:
                    # Clear any prior chunks for this page first -- otherwise a
                    # page that now chunks into fewer pieces than before would
                    # leave stale extra chunks behind (upload_documents only
                    # upserts by id, it never removes documents on its own).
                    index.delete_page(page.id)

                for i, chunk in enumerate(chunk_text(text)):
                    if dry_run:
                        summary.chunks_indexed += 1
                        continue
                    embedding = embedder.embed(chunk)
                    doc = build_search_document(page, chunk, i, embedding)
                    index.stage(doc)
                    summary.chunks_indexed += 1

                summary.pages_processed += 1
                time.sleep(0.1)

        if index is not None:
            index.flush()

    return summary
