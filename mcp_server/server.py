from __future__ import annotations

from mcp.server.mcpserver import MCPServer

from mcp_server.tools import get_full_page as _get_full_page_impl
from mcp_server.tools import search_sdc_ops_confluence as _search_confluence_impl
from mcp_server.tools import search_siemens_wiki as _search_wiki_impl

mcp = MCPServer("siemens-wiki-search")


@mcp.tool()
def search_siemens_wiki(query: str, top_k: int = 5) -> dict:
    """Search the Siemens Wikisphere (wiki.siemens.com) knowledge base.

    Covers SDC product/end-user documentation: how to order/create SDC
    resources (SDC Projects, Data Products, SDC Marketplace), Snowflake, dbt,
    and the ai:attack Azure platform's public wiki pages. This and
    search_sdc_ops_confluence (DAAI internal L1 support/ops runbooks) often
    have COMPLEMENTARY coverage of the same topic -- e.g. "how do I order an
    SDC project" is answered here from the requester's side, while the ops
    index has the support team's internal process for the same request. For
    "how do I order/create/get X" or general how-to questions, check BOTH
    tools rather than assuming one is authoritative; don't skip this one just
    because a question also sounds operational.

    Returns {"results": [...], "sources": [...]} -- results are the matched
    page chunks (title, content, page_id, chunk_index, total_chunks_in_page,
    source_url, ...); sources is a deduplicated list of {title, source_url}
    for just the pages those chunks came from, intended to be shown to the
    user as "explore more" links. If a result's total_chunks_in_page is
    greater than 1 and this chunk isn't enough context, call
    get_full_page(page_id) to get that page's complete content.

    IMPORTANT: when citing source_url to the user, paste it EXACTLY as
    returned -- do not shorten, truncate, or drop the title slug at the end.
    These wiki URLs 404 without the full path; a trimmed-looking URL is a
    broken URL here, not a cosmetic simplification.

    Args:
        query: Natural language search query
        top_k: Number of results to return (default 5)
    """
    return _search_wiki_impl(query, top_k)


@mcp.tool()
def search_sdc_ops_confluence(query: str, top_k: int = 5) -> dict:
    """Search the DAAI internal Confluence knowledge base
    (confluence.ct.daai.siemens.cloud).

    Covers SDC Operations L1 Support runbooks (per-platform troubleshooting
    and internal ordering/provisioning process: Snowflake, PowerBI, Neo4j,
    ERP Data Ingest, SDC Project/Standard Account requests, etc.), the
    Aiattack on Azure platform's internal ops docs (including concrete
    admin/config guides like enabling Azure SQL auto-pause), and Neo4j
    service operations. This and search_siemens_wiki (public SDC product
    docs) often have COMPLEMENTARY coverage of the same topic -- e.g. "how do
    I order an SDC project" is answered here from the support team's internal
    process side, while the wiki has the requester-facing steps. For "how do
    I order/create/get X" or general how-to questions, check BOTH tools
    rather than assuming this one alone is enough, even though the phrasing
    may sound operational.

    Returns {"results": [...], "sources": [...]} in the same shape as
    search_siemens_wiki, including page_id/chunk_index/total_chunks_in_page
    per result -- call get_full_page(page_id) if a chunk isn't enough.

    IMPORTANT: when citing source_url to the user, paste it EXACTLY as
    returned -- do not shorten, truncate, or drop the title slug at the end.
    These Confluence URLs 404 without the full path; a trimmed-looking URL is
    a broken URL here, not a cosmetic simplification.

    Args:
        query: Natural language search query
        top_k: Number of results to return (default 5)
    """
    return _search_confluence_impl(query, top_k)


@mcp.tool()
def get_full_page(page_id: str) -> dict:
    """Fetch a page's complete content by page_id, reassembled from its
    stored chunks in order.

    Use this after search_siemens_wiki or search_sdc_ops_confluence returns a
    result where total_chunks_in_page > 1 and the single chunk shown isn't
    enough to fully answer the question -- pass that result's page_id here to
    get the whole page instead of just the one matched chunk. Checks both
    knowledge bases automatically. Returns {"found": false} if the ID doesn't
    exist in either.

    Args:
        page_id: The page_id field from a search result
    """
    return _get_full_page_impl(page_id)
