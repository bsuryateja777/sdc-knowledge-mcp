from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml
from pydantic_settings import BaseSettings, SettingsConfigDict

from siemens_wiki_common.models import WikiSource

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SOURCES_PATH = REPO_ROOT / "config" / "sources.yaml"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    wiki_base_url: str = "https://wiki.siemens.com"
    wiki_auth_strategy: str = "cookie"  # cookie | pat
    wiki_jsessionid: str = ""
    wiki_pat: str = ""

    # Second, independent Confluence Data Center instance (DAAI internal ops).
    # Different base URL, different SSO (EntraID vs Kerberos), own session
    # cookie/PAT, and its own target Azure AI Search index.
    confluence_base_url: str = "https://confluence.ct.daai.siemens.cloud"
    confluence_auth_strategy: str = "cookie"  # cookie | pat
    confluence_jsessionid: str = ""
    confluence_pat: str = ""
    confluence_search_index: str = "sdc-ops-l1-index"

    azure_search_endpoint: str = ""
    azure_search_key: str = ""
    azure_search_index: str = "siemens-wiki-index"

    # Azure AI Foundry project (services.ai.azure.com) hosting the embedding
    # deployment. Foundry-hosted OpenAI-family models are reachable through
    # the same AzureOpenAI SDK client and api_version scheme as a classic
    # Azure OpenAI resource; non-OpenAI models (e.g. Claude) are not and use
    # a different SDK entirely (azure-ai-inference), not modeled here yet.
    ai_foundry_endpoint: str = ""
    ai_foundry_key: str = ""
    ai_foundry_embed_deployment: str = ""
    ai_foundry_api_version: str = "2024-02-01"
    ai_foundry_embed_dimensions: int = 1536

    mcp_transport: str = "stdio"
    mcp_host: str = "0.0.0.0"
    mcp_port: int = 8080

    # Which instance a deployed Function App should sync. Empty = all
    # instances (used for local ad-hoc runs); set to "wiki" or "confluence"
    # per-deployment so the same codebase can be deployed as two independent
    # Function Apps, each owning only its own instance's schedule/failures.
    ingestion_instance: str = ""


@dataclass(frozen=True)
class ConfluenceInstance:
    name: str
    base_url: str
    auth_strategy: str
    jsessionid: str
    pat: str
    index_name: str


def get_instance(settings: Settings, name: str) -> ConfluenceInstance:
    """Look up connection details for a named Confluence instance.
    Each source in sources.yaml points at one of these by name."""
    if name == "wiki":
        return ConfluenceInstance(
            name="wiki",
            base_url=settings.wiki_base_url,
            auth_strategy=settings.wiki_auth_strategy,
            jsessionid=settings.wiki_jsessionid,
            pat=settings.wiki_pat,
            index_name=settings.azure_search_index,
        )
    if name == "confluence":
        return ConfluenceInstance(
            name="confluence",
            base_url=settings.confluence_base_url,
            auth_strategy=settings.confluence_auth_strategy,
            jsessionid=settings.confluence_jsessionid,
            pat=settings.confluence_pat,
            index_name=settings.confluence_search_index,
        )
    raise ValueError(f"Unknown Confluence instance: {name!r} (expected 'wiki' or 'confluence')")


def load_sources(path: Path = DEFAULT_SOURCES_PATH) -> list[WikiSource]:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return [
        WikiSource(
            space_key=entry["space_key"],
            root_page_id=str(entry["root_page_id"]),
            label=entry.get("label", ""),
            instance=entry.get("instance", "wiki"),
        )
        for entry in data.get("sources", [])
    ]


def get_settings() -> Settings:
    return Settings()
