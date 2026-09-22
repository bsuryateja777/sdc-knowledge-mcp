# Siemens Wikisphere → Azure AI Search → MCP Server
## Full Context Document for Claude Code (VSCode)

> Generated from HAR/LOG analysis of `wiki.siemens.com`  
> Use this as the CLAUDE.md or context prompt when building the MCP server in VSCode.

---

## 1. PLATFORM IDENTIFICATION

| Property | Value |
|---|---|
| **Platform** | **Confluence Data Center (Self-Hosted)** — NOT Confluence Cloud |
| **Site Name** | Wikisphere (Siemens Internal Wiki) |
| **Base URL** | `https://wiki.siemens.com` |
| **Confluence Version** | `9.2.23` |
| **Build Number** | `9116` |
| **API Style** | Confluence Server/DC REST API v1 (`/rest/api/content/`) |
| **Context Path** | `` (empty — root mounted directly) |

> ⚠️ Do NOT use Confluence Cloud API paths (`/wiki/api/v2/`). This is Data Center — use `/rest/api/content/`.

---

## 2. TARGET SPACE & PAGE

| Property | Value |
|---|---|
| **Space Key** | `en` |
| **Space Name** | Global Wiki English |
| **Root Page Title** | Siemens Data & AI Cloud |
| **Root Page ID** | `295931756` |
| **Parent Page ID** | `688130` (Global Wiki English Home) |
| **Page Version** | 237 |
| **Page URL** | `https://wiki.siemens.com/pages/viewpage.action?pageId=295931756` |
| **Clean URL** | `https://wiki.siemens.com/spaces/en/pages/295931756/Siemens+Data+AI+Cloud` |

---

## 3. AUTHENTICATION

### 3.1 How the Browser Authenticates
The browser uses **Siemens SSO (Kerberos/NTLM)** — authentication is handled transparently at the corporate network level. No explicit cookies or Authorization headers appear in requests because the browser is pre-trusted on the Siemens intranet.

### 3.2 ✅ CONFIRMED WORKING AUTH METHOD — JSESSIONID Cookie

**The API is fully accessible using the browser's JSESSIONID session cookie.**

Confirmed working:
```
Cookie: JSESSIONID=<REDACTED_SEE_.env>
```

Confirmed test:
```http
GET https://wiki.siemens.com/rest/api/content/295931756?expand=body.storage&os_authType=basic
Cookie: JSESSIONID=<REDACTED_SEE_.env>
```
→ Returns **200 OK** with full page body. ✅

#### ⚠️ JSESSIONID Limitations
- Expires after ~8–24 hours (browser session)
- **NOT suitable for long-running Function Apps** — need a stable auth method
- Good for local testing and MCP server dev on your machine

### 3.3 Recommended Auth for Production Function App

**Option A — PAT (Preferred, if enabled):**
> PAT URL returned 404 — PATs may be disabled by Wikisphere admins.  
> Email `wikisphere@siemens.com` to request PAT access or a service account.

```http
Authorization: Bearer <PAT_TOKEN>
Accept: application/json
```

**Option B — Session Cookie (works now, use for dev/testing):**
```http
Cookie: JSESSIONID=<value_from_browser>
Accept: application/json
```

**How to get a fresh JSESSIONID from your browser:**
1. Open Chrome/Edge DevTools (F12) → Application → Cookies → `wiki.siemens.com`
2. Copy the `JSESSIONID` value
3. Use it in requests — valid until your browser session expires

**Option C — Basic Auth (try if SSO allows it):**
```http
Authorization: Basic <base64(z0056wjr:YourPassword)>
```

### 3.4 Authenticated User Context (from HAR)
| Field | Value |
|---|---|
| Username | `<REDACTED>` |
| Full Name | `<REDACTED>` |
| User Key | `<REDACTED>` |
| Org Unit | IT DA |
| Access Mode | READ_WRITE |

---

## 3.5 DISCOVERED SDC SUB-SECTION PAGE IDs (from root page cards)

These are the **30 direct Confluence wiki pages** linked from the SDC root page.  
Each has its own sub-tree of child pages to crawl.

| # | Title | Page ID | API URL |
|---|---|---|---|
| 1 | SDC Bespoke | 651703733 | `/rest/api/content/651703733?expand=body.storage` |
| 2 | SDC Marketplace | 510188347 | `/rest/api/content/510188347?expand=body.storage` |
| 3 | Data Governance Platform | 730397238 | `/rest/api/content/730397238?expand=body.storage` |
| 4 | SDC FAQs | 821407151 | `/rest/api/content/821407151?expand=body.storage` |
| 5 | SDC Terms of Use | 821412645 | `/rest/api/content/821412645?expand=body.storage` |
| 6 | Data Products | 709407613 | `/rest/api/content/709407613?expand=body.storage` |
| 7 | Data Architecture | 409175100 | `/rest/api/content/409175100?expand=body.storage` |
| 8 | dbt Cloud | 404794087 | `/rest/api/content/404794087?expand=body.storage` |
| 9 | Community | 367810427 | `/rest/api/content/367810427?expand=body.storage` |
| 10 | SDC Download Center | 472760211 | `/rest/api/content/472760211?expand=body.storage` |
| 11 | Support | 517064938 | `/rest/api/content/517064938?expand=body.storage` |
| 12 | Datalake 2 Go | 184153553 | `/rest/api/content/184153553?expand=body.storage` |
| 13 | Gemini Enterprise | 1033668050 | `/rest/api/content/1033668050?expand=body.storage` |
| 14 | Ai Attack | 575068159 | `/rest/api/content/575068159?expand=body.storage` |
| 15 | Datadog | 510165523 | `/rest/api/content/510165523?expand=body.storage` |
| 16 | SDC SnapLogic | 742408364 | `/rest/api/content/742408364?expand=body.storage` |
| 17 | KNIME | 747014391 | `/rest/api/content/747014391?expand=body.storage` |
| 18 | SDC Streaming | 742408376 | `/rest/api/content/742408376?expand=body.storage` |
| 19 | SDC Mendix DevOps Center | 375746200 | `/rest/api/content/375746200?expand=body.storage` |
| 20 | Talend | 225150767 | `/rest/api/content/225150767?expand=body.storage` |
| 21 | Tableau | 69468620 | `/rest/api/content/69468620?expand=body.storage` |
| 22 | pulse.cloud analytics | 874640176 | `/rest/api/content/874640176?expand=body.storage` |
| 23 | SDC Starter Guides | 805749252 | `/rest/api/content/805749252?expand=body.storage` |
| 24 | SAP Analytics Cloud (SAC) | 253887372 | `/rest/api/content/253887372?expand=body.storage` |
| 25 | SiemensGPT | 733453170 | `/rest/api/content/733453170?expand=body.storage` |
| 26 | SDC Lake | 745804570 | `/rest/api/content/745804570?expand=body.storage` |
| 27 | SDCC (SDC China) | 178788693 | `/rest/api/content/178788693?expand=body.storage` |
| 28 | PMDS | 622972625 | `/rest/api/content/622972625?expand=body.storage` |
| 29 | SDC Project | 847234381 | `/rest/api/content/847234381?expand=body.storage` |
| 30 | Talk 2 Data | 986480098 | `/rest/api/content/986480098?expand=body.storage` |

**CQL to get ALL descendants of root in one query (recommended):**
```
space="en" AND type=page AND ancestor=295931756
```

---

## 4. CONFLUENCE REST API ENDPOINTS

### Base URL for all API calls:
```
https://wiki.siemens.com/rest/api/content
```

---

### 4.1 Get a Single Page with Full Body Content ⭐ PRIMARY ENDPOINT
```http
GET https://wiki.siemens.com/rest/api/content/{pageId}
    ?expand=body.storage,version,space,ancestors,metadata.labels
Authorization: Bearer <PAT>
Accept: application/json
```

**Example — Get the root SDC page:**
```http
GET https://wiki.siemens.com/rest/api/content/295931756?expand=body.storage,version,space,ancestors
```

**Key response fields:**
```json
{
  "id": "295931756",
  "title": "Siemens Data & AI Cloud",
  "type": "page",
  "space": { "key": "en", "name": "Global Wiki English" },
  "version": { "number": 237, "when": "2024-11-15T10:00:00.000Z" },
  "body": {
    "storage": {
      "value": "<p>HTML content here...</p>",
      "representation": "storage"
    }
  },
  "_links": {
    "webui": "/spaces/en/pages/295931756/Siemens+Data+AI+Cloud",
    "self": "https://wiki.siemens.com/rest/api/content/295931756"
  }
}
```

---

### 4.2 Get ALL Descendant Pages Under Root (CQL Search) ⭐ BEST FOR INGESTION
```http
GET https://wiki.siemens.com/rest/api/content/search
    ?cql=space="en" AND type=page AND ancestor=295931756
    &expand=body.storage,version,space,ancestors
    &limit=50
    &start=0
Authorization: Bearer <PAT>
Accept: application/json
```

**Pagination:** Increment `start` by `limit` until `start + limit >= totalSize`.

---

### 4.3 Get Direct Child Pages Only
```http
GET https://wiki.siemens.com/rest/api/content/295931756/child/page
    ?expand=body.storage,version
    &limit=50
    &start=0
Authorization: Bearer <PAT>
```

---

### 4.4 Get All Pages in a Space (no ancestor filter)
```http
GET https://wiki.siemens.com/rest/api/content
    ?spaceKey=en
    &type=page
    &expand=body.storage,version,space
    &limit=50
    &start=0
Authorization: Bearer <PAT>
```

---

### 4.5 CQL Search — Advanced Queries
```http
GET https://wiki.siemens.com/rest/api/content/search
    ?cql=<CQL_QUERY>
    &expand=body.storage,version
    &limit=50
Authorization: Bearer <PAT>
```

**Useful CQL queries:**
```sql
-- All pages under SDC root (recursive)
space="en" AND type=page AND ancestor=295931756

-- Pages modified in last 7 days (for incremental sync)
space="en" AND type=page AND ancestor=295931756 AND lastModified > "2024-01-01"

-- Pages with specific label
space="en" AND type=page AND label="snowflake"

-- Full space crawl
space="en" AND type=page ORDER BY lastModified DESC
```

---

### 4.6 Get Page Attachments (if needed)
```http
GET https://wiki.siemens.com/rest/api/content/295931756/child/attachment
    ?expand=version,metadata
Authorization: Bearer <PAT>
```

---

### 4.7 List All Spaces
```http
GET https://wiki.siemens.com/rest/api/space
    ?limit=50
    &start=0
Authorization: Bearer <PAT>
```

---

## 5. CONTENT FORMAT & PARSING

The `body.storage.value` field returns **Confluence Storage Format** (XHTML-like XML).

### Sample raw content:
```xml
<p>This is a paragraph.</p>
<ac:structured-macro ac:name="info">
  <ac:rich-text-body><p>Info box content</p></ac:rich-text-body>
</ac:structured-macro>
<h2>Section Title</h2>
<table>...</table>
```

### Python parsing recipe:
```python
import re, html
from bs4 import BeautifulSoup

def parse_confluence_storage(storage_html: str) -> str:
    """Convert Confluence storage format to clean plain text."""
    soup = BeautifulSoup(storage_html, 'html.parser')
    
    # Remove macro wrappers but keep their text content
    for macro in soup.find_all('ac:structured-macro'):
        macro.unwrap()
    
    # Remove purely structural tags
    for tag in soup.find_all(['ac:parameter', 'ac:plain-text-body']):
        tag.decompose()
    
    # Get text with spacing
    text = soup.get_text(separator=' ', strip=True)
    
    # Decode HTML entities and collapse whitespace
    text = html.unescape(text)
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text
```

---

## 6. AZURE AI SEARCH INDEX SCHEMA

```json
{
  "name": "siemens-wiki-index",
  "fields": [
    { "name": "id",              "type": "Edm.String",                    "key": true,  "searchable": false },
    { "name": "page_id",         "type": "Edm.String",                    "filterable": true,  "retrievable": true },
    { "name": "title",           "type": "Edm.String",                    "searchable": true,  "retrievable": true },
    { "name": "content",         "type": "Edm.String",                    "searchable": true,  "retrievable": true },
    { "name": "chunk_index",     "type": "Edm.Int32",                     "filterable": true,  "retrievable": true },
    { "name": "source_url",      "type": "Edm.String",                    "searchable": false, "retrievable": true },
    { "name": "space_key",       "type": "Edm.String",                    "filterable": true,  "retrievable": true },
    { "name": "space_name",      "type": "Edm.String",                    "retrievable": true },
    { "name": "labels",          "type": "Collection(Edm.String)",         "filterable": true,  "retrievable": true },
    { "name": "last_modified",   "type": "Edm.DateTimeOffset",            "filterable": true,  "sortable": true,  "retrievable": true },
    { "name": "version_number",  "type": "Edm.Int32",                     "retrievable": true },
    { "name": "ancestors",       "type": "Collection(Edm.String)",         "filterable": true,  "retrievable": true },
    { "name": "embedding",       "type": "Collection(Edm.Single)",
      "dimensions": 1536,
      "vectorSearchProfile": "hnsw-profile",
      "retrievable": false }
  ],
  "vectorSearch": {
    "profiles": [{ "name": "hnsw-profile", "algorithm": "hnsw-config" }],
    "algorithms": [{ "name": "hnsw-config", "kind": "hnsw" }]
  }
}
```

---

## 7. AZURE FUNCTION INGESTION SCRIPT (Python)

```python
import os, re, html, time, requests
from bs4 import BeautifulSoup
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from openai import AzureOpenAI

# ── Config ────────────────────────────────────────────────────────────────────
WIKI_BASE_URL   = "https://wiki.siemens.com"
WIKI_PAT        = os.environ["WIKI_PAT"]                   # Personal Access Token
ROOT_PAGE_ID    = "295931756"
SPACE_KEY       = "en"

SEARCH_ENDPOINT = os.environ["AZURE_SEARCH_ENDPOINT"]     # e.g. https://xxx.search.windows.net
SEARCH_KEY      = os.environ["AZURE_SEARCH_KEY"]
SEARCH_INDEX    = "siemens-wiki-index"

AOAI_ENDPOINT   = os.environ["AZURE_OPENAI_ENDPOINT"]
AOAI_KEY        = os.environ["AZURE_OPENAI_KEY"]
AOAI_EMBED_DEP  = "text-embedding-ada-002"                 # your deployment name

CHUNK_SIZE      = 500    # tokens approx (chars / 4)
CHUNK_OVERLAP   = 100

# ── Clients ───────────────────────────────────────────────────────────────────
wiki_headers = {
    "Authorization": f"Bearer {WIKI_PAT}",
    "Accept": "application/json",
    "X-Atlassian-Token": "no-check"
}

search_client = SearchClient(
    endpoint=SEARCH_ENDPOINT,
    index_name=SEARCH_INDEX,
    credential=AzureKeyCredential(SEARCH_KEY)
)

aoai_client = AzureOpenAI(
    azure_endpoint=AOAI_ENDPOINT,
    api_key=AOAI_KEY,
    api_version="2024-02-01"
)

# ── Step 1: Fetch all pages under root ────────────────────────────────────────
def get_all_pages(ancestor_id: str, space_key: str) -> list[dict]:
    pages = []
    start, limit = 0, 50
    while True:
        resp = requests.get(
            f"{WIKI_BASE_URL}/rest/api/content/search",
            headers=wiki_headers,
            params={
                "cql": f'space="{space_key}" AND type=page AND ancestor={ancestor_id}',
                "expand": "body.storage,version,space,ancestors,metadata.labels",
                "limit": limit,
                "start": start
            }
        )
        resp.raise_for_status()
        data = resp.json()
        pages.extend(data.get("results", []))
        if start + limit >= data.get("totalSize", 0):
            break
        start += limit
        time.sleep(0.3)  # be polite to the server
    return pages

# ── Step 2: Parse Confluence storage format ───────────────────────────────────
def parse_content(storage_html: str) -> str:
    soup = BeautifulSoup(storage_html, 'html.parser')
    for tag in soup.find_all(['ac:parameter', 'ac:plain-text-body', 'ac:image']):
        tag.decompose()
    for macro in soup.find_all('ac:structured-macro'):
        macro.unwrap()
    text = soup.get_text(separator=' ', strip=True)
    text = html.unescape(text)
    return re.sub(r'\s+', ' ', text).strip()

# ── Step 3: Chunk text ────────────────────────────────────────────────────────
def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    words = text.split()
    chunks, i = [], 0
    while i < len(words):
        chunk = ' '.join(words[i:i + chunk_size])
        chunks.append(chunk)
        i += chunk_size - overlap
    return chunks

# ── Step 4: Embed ─────────────────────────────────────────────────────────────
def embed(text: str) -> list[float]:
    resp = aoai_client.embeddings.create(input=text, model=AOAI_EMBED_DEP)
    return resp.data[0].embedding

# ── Step 5: Build search document ────────────────────────────────────────────
def build_doc(page: dict, chunk: str, chunk_idx: int, embedding: list[float]) -> dict:
    page_id = page["id"]
    labels = [l["name"] for l in page.get("metadata", {}).get("labels", {}).get("results", [])]
    ancestors = [a["title"] for a in page.get("ancestors", [])]
    return {
        "id": f"{page_id}_chunk_{chunk_idx}",
        "page_id": page_id,
        "title": page.get("title", ""),
        "content": chunk,
        "chunk_index": chunk_idx,
        "source_url": f"{WIKI_BASE_URL}/spaces/{SPACE_KEY}/pages/{page_id}/{page.get('title','').replace(' ', '+')}",
        "space_key": page.get("space", {}).get("key", ""),
        "space_name": page.get("space", {}).get("name", ""),
        "labels": labels,
        "last_modified": page.get("version", {}).get("when"),
        "version_number": page.get("version", {}).get("number", 0),
        "ancestors": ancestors,
        "embedding": embedding
    }

# ── Main ingestion function ───────────────────────────────────────────────────
def run_ingestion():
    print("Fetching pages...")
    pages = get_all_pages(ROOT_PAGE_ID, SPACE_KEY)
    print(f"Found {len(pages)} pages")

    batch = []
    for page in pages:
        storage_html = page.get("body", {}).get("storage", {}).get("value", "")
        if not storage_html:
            continue
        
        clean_text = parse_content(storage_html)
        if not clean_text:
            continue
        
        chunks = chunk_text(clean_text)
        
        for i, chunk in enumerate(chunks):
            embedding = embed(chunk)
            doc = build_doc(page, chunk, i, embedding)
            batch.append(doc)
            
            if len(batch) >= 100:
                search_client.upload_documents(documents=batch)
                print(f"  Uploaded {len(batch)} chunks")
                batch = []
        
        time.sleep(0.1)
    
    if batch:
        search_client.upload_documents(documents=batch)
        print(f"  Uploaded final {len(batch)} chunks")
    
    print("Ingestion complete!")

if __name__ == "__main__":
    run_ingestion()
```

---

## 8. MCP SERVER TOOL (Python — for VSCode Claude Code)

```python
# mcp_server.py
import os
from mcp.server.fastmcp import FastMCP
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery
from azure.core.credentials import AzureKeyCredential
from openai import AzureOpenAI

mcp = FastMCP("siemens-wiki-search")

search_client = SearchClient(
    endpoint=os.environ["AZURE_SEARCH_ENDPOINT"],
    index_name="siemens-wiki-index",
    credential=AzureKeyCredential(os.environ["AZURE_SEARCH_KEY"])
)

aoai_client = AzureOpenAI(
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    api_key=os.environ["AZURE_OPENAI_KEY"],
    api_version="2024-02-01"
)

@mcp.tool()
def search_siemens_wiki(query: str, top_k: int = 5) -> list[dict]:
    """
    Search the Siemens Wikisphere (wiki.siemens.com) knowledge base.
    Returns relevant page chunks with titles, content, and source URLs.
    
    Args:
        query: Natural language search query
        top_k: Number of results to return (default 5)
    """
    # Embed the query
    embedding = aoai_client.embeddings.create(
        input=query,
        model="text-embedding-ada-002"
    ).data[0].embedding
    
    # Hybrid search: vector + keyword
    vector_query = VectorizedQuery(
        vector=embedding,
        k_nearest_neighbors=top_k,
        fields="embedding"
    )
    
    results = search_client.search(
        search_text=query,           # keyword search
        vector_queries=[vector_query], # vector search
        select=["title", "content", "source_url", "space_name", "labels", "last_modified"],
        top=top_k
    )
    
    return [
        {
            "title": r["title"],
            "content": r["content"],
            "source_url": r["source_url"],
            "space": r.get("space_name", ""),
            "labels": r.get("labels", []),
            "last_modified": str(r.get("last_modified", ""))
        }
        for r in results
    ]

if __name__ == "__main__":
    mcp.run()
```

---

## 9. ENVIRONMENT VARIABLES (.env)

```env
# Siemens Wiki
WIKI_BASE_URL=https://wiki.siemens.com
WIKI_PAT=<generate from https://wiki.siemens.com/plugins/personalaccesstokens/usertokens.action>
WIKI_ROOT_PAGE_ID=295931756
WIKI_SPACE_KEY=en

# Azure AI Search
AZURE_SEARCH_ENDPOINT=https://<your-search-service>.search.windows.net
AZURE_SEARCH_KEY=<your-search-admin-key>
AZURE_SEARCH_INDEX=siemens-wiki-index

# Azure OpenAI
AZURE_OPENAI_ENDPOINT=https://<your-aoai>.openai.azure.com
AZURE_OPENAI_KEY=<your-aoai-key>
AZURE_OPENAI_EMBED_DEPLOYMENT=text-embedding-ada-002
```

---

## 10. MCP SERVER CONFIG (`.vscode/mcp.json`)

```json
{
  "servers": {
    "siemens-wiki": {
      "type": "stdio",
      "command": "python",
      "args": ["mcp_server.py"],
      "env": {
        "AZURE_SEARCH_ENDPOINT": "${env:AZURE_SEARCH_ENDPOINT}",
        "AZURE_SEARCH_KEY": "${env:AZURE_SEARCH_KEY}",
        "AZURE_OPENAI_ENDPOINT": "${env:AZURE_OPENAI_ENDPOINT}",
        "AZURE_OPENAI_KEY": "${env:AZURE_OPENAI_KEY}"
      }
    }
  }
}
```

---

## 11. KEY FACTS SUMMARY (paste this into Claude Code chat)

```
Platform: Confluence Data Center (Self-Hosted) v9.2.23
Site: Wikisphere — https://wiki.siemens.com
API Base: https://wiki.siemens.com/rest/api/content
Auth: Bearer PAT token (generate at /plugins/personalaccesstokens/usertokens.action)
Auth Header: Authorization: Bearer <PAT>
CSRF Header: X-Atlassian-Token: no-check  (for POST/PUT only)
Space: en (Global Wiki English)
Root Page ID: 295931756 (Siemens Data & AI Cloud)
Content Field: body.storage.value (Confluence XHTML storage format)
Pagination: ?limit=50&start=0, increment start until start+limit >= totalSize
Best ingestion query: CQL → space="en" AND type=page AND ancestor=295931756
```

---

*Generated by Astra ⚡ — SiemensGPT | Based on HAR analysis of wiki.siemens.com*
