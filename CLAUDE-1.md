# DAAI Confluence → Azure AI Search → MCP Server
## Full Context Document for Claude Code (VSCode)

> Generated from HAR/LOG analysis of `confluence.ct.daai.siemens.cloud`
> Page visited: 38. SDC Lake | Space: SDCOPSL1

---

## 1. PLATFORM IDENTIFICATION

| Property | Value |
|---|---|
| **Platform** | **Confluence Data Center (Self-Hosted)** |
| **Site Title** | DAAI Confluence |
| **Base URL** | `https://confluence.ct.daai.siemens.cloud` |
| **Confluence Version** | `9.2.23` |
| **Build Number** | `9116` |
| **API Style** | Confluence Server/DC REST API v1 (`/rest/api/content/`) |
| **Context Path** | `` (empty — root mounted directly) |
| **Synchrony Proxy** | `https://confluence.ct.daai.siemens.cloud/synchrony-proxy/` |

> ⚠️ This is a **DIFFERENT** Confluence instance from `wiki.siemens.com`.
> - `wiki.siemens.com` = Public Siemens Wikisphere (SSO/Kerberos auth)
> - `confluence.ct.daai.siemens.cloud` = DAAI internal Confluence (EntraID/OAuth SSO)

---

## 2. AUTHENTICATION

### 2.1 SSO Method — Microsoft EntraID (Azure AD)
From the OAuth config endpoint:
```json
{
  "configured": true,
  "autoRedirectToIDP": false,
  "ssoButtonText": "Use EntraID-Login",
  "backdoorEnabled": true,
  "baseUrl": "https://confluence.ct.daai.siemens.cloud"
}
```

This instance uses **Microsoft EntraID (Azure AD) SSO** — NOT Kerberos/NTLM.
`backdoorEnabled: true` means local username/password login is also available as a fallback.

### 2.2 Auth for Your Function App / MCP Server

**Option A — Personal Access Token (PAT) — Try first:**
```
https://confluence.ct.daai.siemens.cloud/plugins/personalaccesstokens/usertokens.action
```
Or via Profile → Settings → Personal Access Tokens

```http
Authorization: Bearer <PAT_TOKEN>
Accept: application/json
X-Atlassian-Token: no-check
```

**Option B — Basic Auth with local account (backdoor is enabled!):**
```http
Authorization: Basic <base64(username:password)>
Accept: application/json
```

**Option C — Session Cookie (works from browser, for dev/testing):**
Extract from browser DevTools → Application → Cookies → `confluence.ct.daai.siemens.cloud`

**Option D — EntraID OAuth2 Service Principal:**
Since it uses EntraID, you can authenticate via Azure AD OAuth2 client credentials flow
if a service principal is registered. Contact DAAI admins.

### 2.3 Authenticated User Context
| Field | Value |
|---|---|
| Username | `<REDACTED>` |
| Full Name | `<REDACTED>` |
| User Key | `<REDACTED>` |
| Locale | en_US |
| Access Mode | READ_WRITE |
| ATL Token | `<REDACTED_SEE_.env>` |

### 2.4 Test Auth Right Now
Open browser on DAAI Confluence, paste this URL:
```
https://confluence.ct.daai.siemens.cloud/rest/api/content/595283402?expand=body.storage
```
If you get JSON → API works. Then extract session cookie for dev use.

---

## 3. SPACE & PAGE HIERARCHY

### 3.1 Space Details
| Property | Value |
|---|---|
| **Space Key** | `SDCOPSL1` |
| **Space Name** | SDC Operations - L1 Support |
| **Space URL** | `https://confluence.ct.daai.siemens.cloud/spaces/SDCOPSL1` |

### 3.2 Page Hierarchy (from sidebar tree)

```
SDCOPSL1 (Root: 501385522)
├── 01. Platforms / Services in Scope         [501391219]
├── 02. Support Coverage                      [501391227]
├── 03. Roster                                [501391229]
├── 04. Recognition and Appreciation          [506923620]
├── First Line Support                        [501414852]  ← PARENT
│   ├── 1. Ai-Attack-Azure                   [501414883]
│   ├── 2. Ai-Attack-AWS                     [555819292]
│   ├── 3. Data Product Sharing              [504248825]
│   ├── 4. ERP Data Ingest                   [504247372]
│   ├── 5. Neo4j                             [504247415]
│   ├── 6. PowerBI                           [501414856]
│   ├── 7. Qlik                              [504245466]
│   ├── 8. Siemens GPT v1.0                  [555819297]
│   ├── 9. Snowflake                         [506932176]
│   ├── 10. Tableau                          [506928865]
│   ├── 11. DBT Cloud                        [555819312]
│   ├── 13. SDC Marketplace                  [555819317]
│   ├── 15. SDC Project                      [555817205]
│   ├── 16. Snaplogic                        [555817210]
│   ├── 17. SDC Orchestration (Airflow)      [555819327]
│   ├── 18. Datadog                          [555819331]
│   ├── 19. SAC                              [555819335]
│   ├── 20. Datalake2GO                      [555819339]
│   ├── 21. Pulse                            [555817199]
│   ├── 22. SDC Altair AI Cloud              [555819343]
│   ├── 23. Altair Graph Studio              [555819347]
│   ├── 24. OpenAI                           [555819351]
│   ├── 25. BW4HANA (F1P)                   [555819355]
│   ├── 26. Celonis                          [555819360]
│   ├── 27. Talend                           [555819364]
│   ├── 28. SDC Streaming                    [555819368]
│   ├── 29. Alteryx                          [555819372]
│   ├── 30. Knime Business Hub               [555819376]
│   ├── 31. Common Data                      [555819381]
│   ├── 32. xDS: Cross-Account Data Sharing  [555819385]
│   ├── 33. Uniorgdb                         [555819390]
│   ├── 34. ARIZE_AI                         [570170349]
│   ├── 35. GEMINI_ENTERPRISE & LLM_GATEWAY  [570170354]
│   ├── 36. Data Governance Platform         [574824152]
│   ├── 37. Ellie.AI                         [579410456]  ← Previous page
│   └── 38. SDC Lake                         [595283402]  ← Current page
└── Ticket Assignment                         [521546566]
```

### 3.3 Key Page IDs Summary

| Page | ID | Direct URL |
|---|---|---|
| **Space Root** | `501385522` | `/spaces/SDCOPSL1` |
| **First Line Support** (parent) | `501414852` | `/spaces/SDCOPSL1/pages/501414852/First+Line+Support` |
| 01. Platforms / Services in Scope | `501391219` | `/spaces/SDCOPSL1/pages/501391219` |
| 02. Support Coverage | `501391227` | `/spaces/SDCOPSL1/pages/501391227` |
| 03. Roster | `501391229` | `/spaces/SDCOPSL1/pages/501391229` |
| 1. Ai-Attack-Azure | `501414883` | `/spaces/SDCOPSL1/pages/501414883` |
| 2. Ai-Attack-AWS | `555819292` | `/spaces/SDCOPSL1/pages/555819292` |
| 3. Data Product Sharing | `504248825` | `/spaces/SDCOPSL1/pages/504248825` |
| 4. ERP Data Ingest | `504247372` | `/spaces/SDCOPSL1/pages/504247372` |
| 5. Neo4j | `504247415` | `/spaces/SDCOPSL1/pages/504247415` |
| 6. PowerBI | `501414856` | `/spaces/SDCOPSL1/pages/501414856` |
| 7. Qlik | `504245466` | `/spaces/SDCOPSL1/pages/504245466` |
| 8. Siemens GPT v1.0 | `555819297` | `/spaces/SDCOPSL1/pages/555819297` |
| 9. Snowflake | `506932176` | `/spaces/SDCOPSL1/pages/506932176` |
| 10. Tableau | `506928865` | `/spaces/SDCOPSL1/pages/506928865` |
| 11. DBT Cloud | `555819312` | `/spaces/SDCOPSL1/pages/555819312` |
| 13. SDC Marketplace | `555819317` | `/spaces/SDCOPSL1/pages/555819317` |
| 15. SDC Project | `555817205` | `/spaces/SDCOPSL1/pages/555817205` |
| 16. Snaplogic | `555817210` | `/spaces/SDCOPSL1/pages/555817210` |
| 17. SDC Orchestration (Airflow) | `555819327` | `/spaces/SDCOPSL1/pages/555819327` |
| 18. Datadog | `555819331` | `/spaces/SDCOPSL1/pages/555819331` |
| 19. SAC | `555819335` | `/spaces/SDCOPSL1/pages/555819335` |
| 20. Datalake2GO | `555819339` | `/spaces/SDCOPSL1/pages/555819339` |
| 21. Pulse | `555817199` | `/spaces/SDCOPSL1/pages/555817199` |
| 22. SDC Altair AI Cloud | `555819343` | `/spaces/SDCOPSL1/pages/555819343` |
| 23. Altair Graph Studio | `555819347` | `/spaces/SDCOPSL1/pages/555819347` |
| 24. OpenAI | `555819351` | `/spaces/SDCOPSL1/pages/555819351` |
| 25. BW4HANA (F1P) | `555819355` | `/spaces/SDCOPSL1/pages/555819355` |
| 26. Celonis | `555819360` | `/spaces/SDCOPSL1/pages/555819360` |
| 27. Talend | `555819364` | `/spaces/SDCOPSL1/pages/555819364` |
| 28. SDC Streaming | `555819368` | `/spaces/SDCOPSL1/pages/555819368` |
| 29. Alteryx | `555819372` | `/spaces/SDCOPSL1/pages/555819372` |
| 30. Knime Business Hub | `555819376` | `/spaces/SDCOPSL1/pages/555819376` |
| 31. Common Data | `555819381` | `/spaces/SDCOPSL1/pages/555819381` |
| 32. xDS: Cross-Account Data Sharing | `555819385` | `/spaces/SDCOPSL1/pages/555819385` |
| 33. Uniorgdb | `555819390` | `/spaces/SDCOPSL1/pages/555819390` |
| 34. ARIZE_AI | `570170349` | `/spaces/SDCOPSL1/pages/570170349` |
| 35. GEMINI_ENTERPRISE & LLM_GATEWAY | `570170354` | `/spaces/SDCOPSL1/pages/570170354` |
| 36. Data Governance Platform | `574824152` | `/spaces/SDCOPSL1/pages/574824152` |
| 37. Ellie.AI | `579410456` | `/spaces/SDCOPSL1/pages/579410456` |
| **38. SDC Lake** (current) | `595283402` | `/spaces/SDCOPSL1/pages/595283402` |
| Ticket Assignment | `521546566` | `/spaces/SDCOPSL1/pages/521546566` |

---

## 4. CONNECTED ECOSYSTEM (from App Switcher)

| App | URL |
|---|---|
| **DAAI Confluence** (this) | `https://confluence.ct.daai.siemens.cloud` |
| **DAAI Jira** | `https://jira.ct.daai.siemens.cloud/secure/MyJiraHome.jspa` |
| **DAAI Dev Help Center** | `https://jira.ct.daai.siemens.cloud/servicedesk/customer/portal/2` |
| **DAAI DEV Distribution** (Artifactory) | `https://artifactory.ct.daai.siemens.cloud/` |
| **DAAI Disclaimer** | `https://confluence.ct.daai.siemens.cloud/display/DAAIHOME/Disclaimer` |
| **Group Admin** | `https://confluence.ct.daai.siemens.cloud/pages/viewpage.action?pageId=524616681` |

---

## 5. REST API ENDPOINTS

### Base URL:
```
https://confluence.ct.daai.siemens.cloud/rest/api/content
```

### 5.1 Get a Single Page with Full Content ⭐
```http
GET https://confluence.ct.daai.siemens.cloud/rest/api/content/{pageId}
    ?expand=body.storage,version,space,ancestors,metadata.labels
Authorization: Bearer <PAT>
Accept: application/json
```

**Example — current page (SDC Lake):**
```http
GET https://confluence.ct.daai.siemens.cloud/rest/api/content/595283402?expand=body.storage,version,space,ancestors
```

### 5.2 Get ALL Descendants Under "First Line Support" ⭐ BEST FOR INGESTION
```http
GET https://confluence.ct.daai.siemens.cloud/rest/api/content/search
    ?cql=space="SDCOPSL1" AND type=page AND ancestor=501414852
    &expand=body.storage,version,space,ancestors
    &limit=50
    &start=0
Authorization: Bearer <PAT>
```

### 5.3 Get ALL Pages in SDCOPSL1 Space
```http
GET https://confluence.ct.daai.siemens.cloud/rest/api/content/search
    ?cql=space="SDCOPSL1" AND type=page
    &expand=body.storage,version,space
    &limit=50
    &start=0
Authorization: Bearer <PAT>
```

### 5.4 Get Direct Children of a Page
```http
GET https://confluence.ct.daai.siemens.cloud/rest/api/content/{pageId}/child/page
    ?expand=body.storage,version
    &limit=50
Authorization: Bearer <PAT>
```

**Get all children of "First Line Support":**
```http
GET https://confluence.ct.daai.siemens.cloud/rest/api/content/501414852/child/page?expand=body.storage,version&limit=50
```

### 5.5 Incremental Sync (pages modified after date)
```http
GET https://confluence.ct.daai.siemens.cloud/rest/api/content/search
    ?cql=space="SDCOPSL1" AND type=page AND lastModified > "2024-01-01"
    &expand=body.storage,version
    &limit=50
Authorization: Bearer <PAT>
```

### 5.6 Get Space Info
```http
GET https://confluence.ct.daai.siemens.cloud/rest/api/space/SDCOPSL1
Authorization: Bearer <PAT>
```

### 5.7 Get Page Ancestors (breadcrumb)
```http
GET https://confluence.ct.daai.siemens.cloud/rest/api/content/595283402?expand=ancestors
Authorization: Bearer <PAT>
```
Returns: `SDC Lake → First Line Support → [Space Root]`

### 5.8 Search by Title
```http
GET https://confluence.ct.daai.siemens.cloud/rest/api/content/search
    ?cql=space="SDCOPSL1" AND type=page AND title="SDC Lake"
    &expand=body.storage
Authorization: Bearer <PAT>
```

---

## 6. URL PATTERNS FOR NAVIGATION

```
# Page by ID (canonical)
https://confluence.ct.daai.siemens.cloud/spaces/{spaceKey}/pages/{pageId}/{title}

# Page by ID (legacy)
https://confluence.ct.daai.siemens.cloud/pages/viewpage.action?pageId={pageId}

# Space home
https://confluence.ct.daai.siemens.cloud/spaces/{spaceKey}

# REST API self link
https://confluence.ct.daai.siemens.cloud/rest/api/content/{pageId}

# Page tree sidebar (AJAX)
https://confluence.ct.daai.siemens.cloud/plugins/pagetree/naturalchildren.action
    ?pageId={rootPageId}&treePageId={currentPageId}&ancestors={parentId}&ancestors={grandparentId}
```

---

## 7. KEY INGESTION CQL QUERIES

```sql
-- All pages in SDCOPSL1 space
space="SDCOPSL1" AND type=page

-- All L1 Support pages (under "First Line Support")
space="SDCOPSL1" AND type=page AND ancestor=501414852

-- All pages under space root
space="SDCOPSL1" AND type=page AND ancestor=501385522

-- Specific platform page
space="SDCOPSL1" AND type=page AND title="38. SDC Lake"

-- Recently modified (incremental sync)
space="SDCOPSL1" AND type=page AND lastModified > "2024-01-01" ORDER BY lastModified DESC
```

---

## 8. COMPLETE IDENTITY SUMMARY (paste into Claude Code)

```
Platform: Confluence Data Center (Self-Hosted) v9.2.23
Site: DAAI Confluence
Base URL: https://confluence.ct.daai.siemens.cloud
API Base: https://confluence.ct.daai.siemens.cloud/rest/api/content
Auth: EntraID SSO (OAuth2) | backdoor basic auth also available
PAT URL: https://confluence.ct.daai.siemens.cloud/plugins/personalaccesstokens/usertokens.action
Auth Header: Authorization: Bearer <PAT>
CSRF Header: X-Atlassian-Token: no-check (for POST/PUT)
Space Key: SDCOPSL1 (SDC Operations - L1 Support)
Space Root Page ID: 501385522
Parent Page (First Line Support): 501414852
Current Page (38. SDC Lake): 595283402
Total L1 Support Pages: 38 platform pages + 4 meta pages
Content Field: body.storage.value (Confluence XHTML storage format)
Pagination: ?limit=50&start=0, increment start until start+limit >= totalSize
Best ingestion CQL: space="SDCOPSL1" AND type=page AND ancestor=501414852
Connected: DAAI Jira (jira.ct.daai.siemens.cloud), Artifactory (artifactory.ct.daai.siemens.cloud)
```

---

## 9. DIFFERENCES vs wiki.siemens.com

| Property | wiki.siemens.com | confluence.ct.daai.siemens.cloud |
|---|---|---|
| **Purpose** | Public Siemens Wikisphere | DAAI Internal Ops |
| **Auth** | Kerberos/NTLM SSO | EntraID (Azure AD) OAuth2 |
| **Space** | `en` (Global Wiki English) | `SDCOPSL1` (SDC Ops L1) |
| **Root Page** | 295931756 | 501385522 |
| **Content** | SDC product docs | L1 Support runbooks |
| **Locale** | en_GB | en_US |
| **Attachment Max** | 10 MB | 100 MB |
| **PAT** | Disabled (SSO only) | Likely enabled (backdoor on) |

---

*Generated by Astra ⚡ — SiemensGPT | Based on HAR analysis of confluence.ct.daai.siemens.cloud*
