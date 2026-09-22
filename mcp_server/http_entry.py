from __future__ import annotations

from siemens_wiki_common.config import get_settings

from mcp_server.server import mcp

# For Azure Container Apps. Remote auth (API key header / Easy Auth / network
# restriction) is an open decision -- see the plan's Milestone 5 -- not yet
# wired up here.

if __name__ == "__main__":
    settings = get_settings()
    mcp.run(transport="streamable-http", host=settings.mcp_host, port=settings.mcp_port)
