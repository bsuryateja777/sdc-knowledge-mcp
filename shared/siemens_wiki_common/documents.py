from __future__ import annotations

from siemens_wiki_common.models import ConfluencePage, SearchDocument


def build_search_document(
    page: ConfluencePage, chunk: str, chunk_index: int, embedding: list[float]
) -> SearchDocument:
    return SearchDocument(
        id=f"{page.id}_chunk_{chunk_index}",
        page_id=page.id,
        title=page.title,
        content=chunk,
        chunk_index=chunk_index,
        source_url=page.source_url,
        space_key=page.space_key,
        space_name=page.space_name,
        labels=page.labels,
        last_modified=page.last_modified,
        version_number=page.version_number,
        ancestors=page.ancestors,
        embedding=embedding,
    )
