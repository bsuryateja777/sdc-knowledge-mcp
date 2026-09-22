from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class WikiSource:
    space_key: str
    root_page_id: str
    label: str = ""
    instance: str = "wiki"  # which ConfluenceInstance (config.py) this source belongs to


@dataclass
class ConfluencePage:
    id: str
    title: str
    space_key: str
    space_name: str
    body_storage: str
    version_number: int
    last_modified: str | None
    labels: list[str] = field(default_factory=list)
    ancestors: list[str] = field(default_factory=list)
    source_url: str = ""  # absolute URL, built from _links.base + _links.webui


@dataclass
class SearchDocument:
    id: str
    page_id: str
    title: str
    content: str
    chunk_index: int
    source_url: str
    space_key: str
    space_name: str
    labels: list[str]
    last_modified: str | None
    version_number: int
    ancestors: list[str]
    embedding: list[float]
