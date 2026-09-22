# Siemens Wiki/Confluence → Azure AI Search → MCP Server

Ingests content from two independent Confluence Data Center instances into
Azure AI Search, then exposes hybrid (keyword + vector) search over both
indexes as MCP tools:

- **wiki.siemens.com** ("Siemens Wikisphere", Kerberos/NTLM SSO) → `siemens-wiki-index`.
  Covers SDC product docs (SDC Marketplace, Data Products, Snowflake, dbt, ...)
  and the ai:attack Azure platform's public wiki pages. See `CLAUDE.md`.
- **confluence.ct.daai.siemens.cloud** ("DAAI Confluence", EntraID SSO) →
  `sdc-ops-l1-index`. Covers SDC Operations L1 Support runbooks, Aiattack on
  Azure internal ops docs, and Neo4j service operations. See `CLAUDE-1.md`.

## Layout

- `shared/siemens_wiki_common/` — single source of truth: multi-instance
  Confluence auth/client, parsing, chunking, embeddings, Azure AI Search index
  management, and `resilience.py` (retry-with-backoff on transient errors).
  Imported by both the ingestion Function and the MCP server.
- `ingestion/` — Azure Functions app (Python v2 model). Deployed as **two
  independent Function App resources** (one per Confluence instance) from the
  same codebase, differentiated by the `INGESTION_INSTANCE` app setting
  (`wiki` | `confluence`). Each has:
  - `sync_timer` — nightly, **incremental** (only re-crawls pages modified
    since the last run, using the index itself as the sync-state source of
    truth — see `ingest_pipeline.run_ingestion`'s docstring).
  - `sync_weekly_full` — weekly, full refresh (Sundays 02:00). Re-crawls
    everything and does delete-before-reinsert per page. **Does not** detect
    Confluence-side deletions — see "Known limitations" below.
  - `sync_http` — manual trigger (`POST /api/sync?limit=N&full=true`),
    function-key protected.
- `scripts/` — local CLI tools (no Functions runtime needed):
  - `setup_search_index.py --instance {wiki,confluence}` — create/update an index.
  - `run_ingestion_local.py --source [instance:]space_key:root_page_id [--limit N] [--dry-run] [--full]`
  - `verify_index.py "query" --instance {wiki,confluence}` — sanity-check search.
  - `build_function_zip.ps1` — assembles a self-contained deployable zip for
    the ingestion Function Apps (see "Deploying the Function Apps" below).
- `mcp_server/` — the MCP server, three tools (see "MCP tools" below).
  `tools.py` is transport-agnostic; `stdio_entry.py` runs locally,
  `http_entry.py` is what the container runs.
- `docker/` — Dockerfile for deploying `mcp_server` to Azure Container Apps.
- `config/sources.yaml` — every source to crawl, each tagged with which
  instance it belongs to (`instance: wiki` | `instance: confluence`).
  `ingest_pipeline.run_ingestion` groups sources by instance automatically.

## Prerequisites

1. Python 3.11+
2. An Azure AI Search service (Free tier is fine at current corpus size —
   ~1800 chunks across both indexes, well under Free's 10k docs/50MB caps
   per index; re-evaluate if either index grows a lot)
3. An Azure AI Foundry project with an OpenAI-family embedding model deployed
   (e.g. `text-embedding-3-small`) — note the *deployment name* and its output
   dimensions. Shared across both Confluence instances (embeddings aren't
   instance-specific). A non-OpenAI chat model (e.g. Claude) can live in the
   same Foundry project for a later chatbot phase, but that's a separate
   integration (`azure-ai-inference` SDK) — it can't do embeddings.
4. A fresh `JSESSIONID` cookie for **each** Confluence instance you're
   ingesting from (DevTools → Application → Cookies, on that instance's domain)

## Setup

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
Copy-Item .env.example .env
# edit .env with real values -- WIKI_* and CONFLUENCE_* are independent
```

## Run it end-to-end

```powershell
# Create both indexes
python scripts\setup_search_index.py --instance wiki
python scripts\setup_search_index.py --instance confluence

# Ingest everything in config/sources.yaml (both instances, all sources)
python scripts\run_ingestion_local.py

# Or target one source while testing
python scripts\run_ingestion_local.py --source confluence:SDCOPSL1:501414852 --limit 3

# Confirm search works
python scripts\verify_index.py "SDC Marketplace"
python scripts\verify_index.py "enable auto-pause on sql" --instance confluence

# Register .mcp.json's siemens-wiki server in Claude Code (auto-detected at
# session start; approve the trust prompt with `claude` if pending), then ask
# a real question and confirm it calls the tools and cites correct source_urls.
```

## MCP tools

- **`search_siemens_wiki(query, top_k=5)`** — hybrid search over `siemens-wiki-index`.
- **`search_sdc_ops_confluence(query, top_k=5)`** — hybrid search over `sdc-ops-l1-index`.
  Both return `{"results": [...], "sources": [...]}`; each result includes
  `page_id`, `chunk_index`, and `total_chunks_in_page` so a calling agent can
  tell whether a chunk is partial.
- **`get_full_page(page_id)`** — reconstructs a page's complete content from
  its stored chunks (checks both indexes automatically). Use when a search
  result's `total_chunks_in_page > 1` and one chunk isn't enough context.

All three have input guardrails (`top_k` capped at 20, query length capped at
500 chars), retry-with-backoff on transient Azure/OpenAI errors, and
structured logging (`query`, `instance`, `elapsed`, `result_count`) — see
`mcp_server/tools.py`.

## Deploying the Function Apps

One codebase, deployed as **two** Azure Function App resources (Consumption
plan, Python 3.11, Linux):

1. Create both in the Portal. Set `INGESTION_INSTANCE=wiki` as an app setting
   on one, `INGESTION_INSTANCE=confluence` on the other, plus that instance's
   `WIKI_*`/`CONFLUENCE_*`, `AZURE_SEARCH_*`, and `AI_FOUNDRY_*` settings (see
   `.env.example` / `ingestion/local.settings.json.example` for the full list).
2. Run `scripts\build_function_zip.ps1` — builds `dist\ingestion_function.zip`,
   self-contained (bundles `shared/siemens_wiki_common` and `config/sources.yaml`
   alongside the function code so it works from an isolated Oryx build).
3. Deploy that **same zip** to both apps via each app's Advanced Tools (Kudu)
   → Zip Push Deploy — no Azure CLI needed.

## Deploying the MCP server to Azure Container Apps

Not yet done from this machine (no Docker here) — pick this up wherever
Docker lives:

```powershell
# 1. Build
docker build -t mcp-siemens-wiki:latest -f docker/Dockerfile .

# 2. Tag + push to your ACR
docker tag mcp-siemens-wiki:latest <your-acr-name>.azurecr.io/mcp-siemens-wiki:latest
az acr login --name <your-acr-name>
docker push <your-acr-name>.azurecr.io/mcp-siemens-wiki:latest

# 3. Deploy to Container Apps (or update an existing revision), with the same
#    AZURE_SEARCH_*/AI_FOUNDRY_* env vars as .env. MCP_TRANSPORT=http/MCP_PORT=8080
#    are already baked into the Dockerfile.
az containerapp create \
  --name mcp-siemens-wiki --resource-group <rg> --environment <env> \
  --image <your-acr-name>.azurecr.io/mcp-siemens-wiki:latest \
  --target-port 8080 --ingress external \
  --env-vars AZURE_SEARCH_ENDPOINT=... AZURE_SEARCH_KEY=... AI_FOUNDRY_ENDPOINT=... AI_FOUNDRY_KEY=... AI_FOUNDRY_EMBED_DEPLOYMENT=...

# 4. Test: register the resulting HTTPS URL + /mcp as a remote MCP server
#    (`claude mcp add --transport http <name> https://<app>.<region>.azurecontainerapps.io/mcp`)
#    and confirm the tools respond. Remote auth is NOT configured yet -- this
#    endpoint is open once ingress is external. Decide auth (API key header /
#    Container Apps Easy Auth / network restriction) before leaving it running
#    with real access.
```

## Tests

```powershell
pytest
```

31 unit tests, no network/Azure access needed. No integration test suite yet
(everything's been verified via real end-to-end runs against live Azure/Confluence
instead — solid but slower than mocked tests would be).

## Auth notes

Both instances currently use a manually-refreshed `JSESSIONID` cookie
(`WIKI_AUTH_STRATEGY=cookie` / `CONFLUENCE_AUTH_STRATEGY=cookie`), which
expires in 8-24h. This works fine for local runs and the manual HTTP trigger,
but means the *nightly timer* will start failing whenever the cookie in that
Function App's settings goes stale — there's no automatic refresh.
Switching either instance to PAT is `*_AUTH_STRATEGY=pat` + `*_PAT=...`, no
code changes. wiki.siemens.com's PATs were reported disabled (SSO only);
confluence.ct.daai.siemens.cloud's PATs are reported likely enabled
("backdoor" local auth is on) — worth trying there first.

## Known limitations

- **No automated deletion cleanup.** Incremental sync only ever adds/updates;
  the weekly full-crawl refreshes existing pages but can't detect pages
  deleted from Confluence. Real fix requires marking `id` or `page_id` as
  `sortable: true` in `shared/siemens_wiki_common/schema.json` (needed for a
  safe, complete index scan) — Azure Search won't allow changing `sortable`
  on an existing field, so this means recreating both indexes and
  re-ingesting everything. Not done yet; needs an explicit decision since
  it's disruptive.
- **Pagination gotcha**: `search_text="*"` queries beyond ~1000 results are
  unreliable (confirmed: silently skips some documents while duplicating
  others) because no field except `last_modified` is `sortable`. Use
  `get_index_statistics()` for aggregate counts, not a paginated wildcard scan.
- **`aiattack_ops` peer MCP server** is registered but blocked on network/org
  access (403 even through its OAuth flow) — not something fixable from this
  project; needs the ai:attack team's action.
- **Remote MCP server auth** (Container Apps phase) is an open decision, not
  yet implemented — see "Deploying the MCP server" above.

## Planned, not yet built

- `chatbot/` — a conversational agent that calls the deployed MCP server as
  an HTTP client, once Container Apps deployment is proven working.
- Moving secrets from `.env`/plaintext App Settings to Azure Key Vault.
