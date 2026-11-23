# Deep dive 2: JSON, APIs and pandas, and how this role uses them

This guide explains the three skills you'll use together every day as a GTM Engineer: **APIs** (how
your code talks to other tools), **JSON** (the format data travels in) and **pandas** (how you clean
and analyse data once it arrives). Each part covers what it is, how it works, the mistakes beginners
make, and exactly how it's used at a company like Secfix.

Run the end-to-end example yourself (no accounts needed, it uses the repo's local practice API):
[code/json_apis_pandas_demo.py](code/json_apis_pandas_demo.py).

---

## 1. How the three fit together

In one sentence: **APIs** are how your code talks to other tools, **JSON** is the language that data
travels in, and **pandas** is how you clean and analyse it once it arrives.

| | What it is | Analogy | Your job with it |
| --- | --- | --- | --- |
| **API** | A way for one program to ask another for data or actions over the internet | The waiter who takes your order to the kitchen | Call HubSpot, Apollo, Clay, Slack, Claude reliably |
| **JSON** | A text format for structured data: labels and values | The written order slip | Read responses, build request bodies, parse AI output |
| **pandas** | A Python library for tables (DataFrames) | A spreadsheet you control with code | Clean, dedupe, score, merge, summarise |

### The journey of data in one real GTM task

Task: *"Find new companies from our data provider, clean them, score them, and add the good ones to
HubSpot without duplicates."*

1. **API call (in):** your Python asks the data provider's API for companies. It answers with **JSON**.
2. **JSON → Python:** `response.json()` turns the JSON text into dicts and lists.
3. **Python → pandas:** `pd.DataFrame(rows)` turns the list of dicts into a table.
4. **pandas work:** normalise domains, drop personal emails, dedupe, score, merge with what's already in
   the CRM.
5. **pandas → Python:** `df.to_dict("records")` turns the table back into a list of dicts (fixing
   missing values on the way).
6. **Python → JSON:** `requests.post(..., json=body)` turns the dicts into JSON.
7. **API call (out):** HubSpot's batch upsert endpoint receives the JSON and creates or updates the
   companies.
8. **API call (alert):** a Slack webhook gets a JSON message: "Lena, call PeopleCo today because…"

Almost every task in this role is a version of this loop. Master the loop and you've mastered most of
the job's technical side.

---

## 2. JSON in detail

**JSON (JavaScript Object Notation)** is plain text that stores structured data as labels and values.
It's the standard format for APIs because every programming language can read and write it. Despite
the name, it has nothing to do with JavaScript in practice.

```json
{
  "name": "PeopleCo GmbH",
  "domain": "peopleco.de",
  "employees": 120,
  "score": 87.5,
  "is_customer": false,
  "owner": null,
  "tags": ["software", "dach"],
  "address": {"city": "Berlin", "country": "DE"}
}
```

### 2.1 The six building blocks, and what they become in Python

| JSON | Example | Python |
| --- | --- | --- |
| Object `{ }` | `{"name": "PeopleCo"}` | `dict` |
| Array `[ ]` | `["software", "dach"]` | `list` |
| String | `"peopleco.de"` | `str` |
| Number | `120`, `87.5` | `int`, `float` |
| Boolean | `true`, `false` | `True`, `False` |
| Null | `null` | `None` |

So if you know Python dicts and lists (deep dive 1), you already know how to work with JSON.

### 2.2 Syntax rules (where hand-written JSON breaks)

- Keys must be strings in **double quotes**: `{"name": 1}`, not `{name: 1}` or `{'name': 1}`.
- No trailing commas: `[1, 2, 3,]` is invalid.
- No comments.
- `true`, `false`, `null` are lowercase.
- Dates have no special type: they're strings like `"2026-11-20T16:40:12Z"` (ISO 8601), or numbers
  like `1763900000000` (milliseconds since 1 January 1970, "epoch milliseconds").

### 2.3 Reading and writing JSON in Python

```python
import json

# text <-> Python  (the "s" in loads/dumps means "string")
data = json.loads('{"name": "PeopleCo", "owner": null}')   # -> {'name': 'PeopleCo', 'owner': None}
text = json.dumps(data)                                      # -> '{"name": "PeopleCo", "owner": null}'
pretty = json.dumps(data, indent=2, ensure_ascii=False)      # readable; keeps ü and é as they are

# files <-> Python
with open("response.json", encoding="utf-8") as f:
    data = json.load(f)
with open("response.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)

# from an API: requests does the parsing for you
data = requests.get(url, timeout=10).json()
```

**Why save JSON to files in a pipeline?** Save the raw API response before you clean it. If your
cleaning code has a bug, you fix it and re-run from the saved file without calling the API again
(saving time and rate limit).

### 2.4 Navigating nested JSON safely

```python
for item in data.get("results", []):
    props = item.get("properties") or {}          # handles a missing key AND a null value
    name = props.get("name", "")
next_cursor = data.get("paging", {}).get("next", {}).get("after")
```

Use `.get()` with defaults at every level: real APIs leave fields out, or send `null`.

### 2.5 Errors you'll meet

| Error | Cause | Fix |
| --- | --- | --- |
| `json.JSONDecodeError: Expecting value` | The text isn't JSON: an HTML error page, an empty body, or AI prose like "Sure! Here's the JSON..." | Check `response.status_code` and `response.text` first; validate AI output |
| `Object of type int64 is not JSON serializable` | A numpy number from pandas | Convert with `int()` / `float()` |
| `Out of range float values are not JSON compliant: nan` | pandas NaN in your data | Convert NaN to None, then drop empty fields |
| `Object of type datetime is not JSON serializable` | A Python datetime | `.isoformat()` first |
| `KeyError` | Reading a key that isn't there with `["key"]` | Use `.get("key")` |

---

## 3. JSON in this role: the four kinds you'll meet every week

### 3.1 CRM API responses (reading)

A HubSpot list of companies:

```json
{
  "results": [
    {"id": "1001",
     "properties": {"name": "PeopleCo GmbH", "domain": "peopleco.de",
                    "numberofemployees": "120", "hubspot_owner_id": "lena"},
     "updatedAt": "2026-11-20T16:40:12Z"}
  ],
  "paging": {"next": {"after": "1001"}}
}
```

What to notice:

- The records are inside `results`; the fields are inside `properties`.
- Numbers arrive as **strings** (`"120"`), so convert before comparing.
- The next page's cursor is at `paging.next.after`, and `paging` is **missing on the last page** (that's
  how you know to stop).

### 3.2 Request bodies (writing)

A HubSpot batch upsert you send:

```json
{"inputs": [
  {"idProperty": "company_domain_key", "id": "peopleco.de",
   "properties": {"name": "PeopleCo GmbH", "fit_score": "95",
                  "score_reasons": "software; 120 staff; DE; hiring ISO 27001 manager"}}
]}
```

You build this as a Python dict and pass `json=body` to `requests`. Rules: only send fields you own,
never send empty values, and convert numbers to strings for HubSpot.

### 3.3 Webhook payloads (receiving)

What HubSpot POSTs to your endpoint when a deal changes stage:

```json
[{"eventId": 101, "subscriptionId": 9001, "portalId": 4455, "occurredAt": 1763900000000,
  "subscriptionType": "deal.propertyChange", "objectId": 5001,
  "propertyName": "dealstage", "propertyValue": "demo_booked", "attemptNumber": 0}]
```

What to notice:

- It's a **list**: several events can come in one request.
- It has IDs, not the full deal; you fetch details with another API call.
- `occurredAt` is milliseconds since 1970.
- The same event can arrive twice (`attemptNumber` > 0 means a retry), so dedupe on `(eventId,
  subscriptionId, occurredAt)`.

### 3.4 AI output (parsing and validating)

You ask Claude to reply with JSON only:

```json
{"industry": "Software", "sells_to_enterprise": true, "compliance_signal": true,
 "confidence": 0.93, "reason": "HR software for enterprises; hiring an ISO 27001 manager"}
```

Then you `json.loads()` it inside try/except and **validate every field** (allowed values, types,
length) before anything is written to the CRM. If parsing or validation fails: retry once, then send
the record to a review list. (Full example: [09-claude-and-ai/claude_scoring.py](../09-claude-and-ai/claude_scoring.py).)

### 3.5 Also common

- **Slack messages:** `{"text": "Lena, call PeopleCo today: ..."}` posted to an incoming-webhook URL.
- **Config files** and **saved raw API responses**.

---

## 4. APIs in detail

An **API (application programming interface)** is how one program asks another for data or actions.

**Restaurant analogy:** the API is the **menu** (what you're allowed to ask for) and the **waiter**
(who carries your request to the kitchen and brings the answer back). Your code never touches HubSpot's
database directly; it asks through HubSpot's API. Most APIs you'll use are **REST APIs** over **HTTPS**:
resources live at URLs and you use standard methods on them.

### 4.1 A request has four parts

| Part | Letter analogy | Example |
| --- | --- | --- |
| **URL** (endpoint) | The address | `https://api.hubapi.com/crm/v3/objects/companies` |
| **Method** | What you want done | `GET` |
| **Headers** | The ID card and envelope labels | `Authorization: Bearer <key>` |
| **Body** (for POST/PATCH) | The letter inside | `{"properties": {"name": "PeopleCo"}}` |

### 4.2 URLs

```
https://api.hubapi.com/crm/v3/objects/companies?limit=100&after=1001
└ scheme ┘└─── host ───┘└───── path ─────┘└── query parameters ──┘
```

Query parameters (`?key=value&key2=value2`) filter, limit or page the results. In Python you pass them
as a dict: `params={"limit": 100, "after": "1001"}`.

### 4.3 Methods

| Method | Meaning | GTM example |
| --- | --- | --- |
| `GET` | Read | List companies; get one contact |
| `POST` | Create, or send an action | Create a company; batch upsert; search; post to Slack |
| `PATCH` | Update some fields | Update a company's fit score |
| `PUT` | Replace / set | Create an association |
| `DELETE` | Remove (archive) | Delete a test record |

### 4.4 The response: status code + body

| Code | Meaning | What your code does |
| --- | --- | --- |
| 200 OK, 201 Created, 204 No content | Success | Continue |
| 400 Bad request | Your request is wrong | Log the body, fix it, **don't retry** |
| 401 Unauthorised | Missing or wrong key | Fix the key, **don't retry** |
| 403 Forbidden | Key lacks permission (scope) | Add the scope, **don't retry** |
| 404 Not found | No such record | Handle it (for enrichment: "no data") |
| 409 Conflict | Duplicate / unique value exists | Update instead of create |
| **429 Too many requests** | Rate limited | **Wait and retry** (respect `Retry-After`) |
| **500, 502, 503, 504** | Server problem | **Wait and retry** a few times |

**Rule of thumb:** 2xx fine; 4xx your fault (don't retry, except 429); 5xx their fault (retry).

### 4.5 Authentication

| Method | How it works | Example |
| --- | --- | --- |
| API key / bearer token | A secret string in the `Authorization` header | HubSpot service keys, the Anthropic API key |
| OAuth 2.0 | The user clicks "Allow"; your app gets short-lived access tokens | "Connect HubSpot" buttons in apps |
| Webhook signature | The sender signs each request with a shared secret; you verify it | HubSpot webhooks to your endpoint |

Keys live in a `.env` file, never in code or Git. **Scopes** limit what a key can do: give each key
only what it needs (least privilege, which matters at a security-compliance company).

### 4.6 Reading API documentation

For each endpoint, find:

1. The **method and URL**.
2. **Auth** and required **scopes**.
3. **Parameters and body** fields, required vs optional, with an example.
4. The **response shape**, and where the next-page cursor is.
5. **Limits**: rate limit, page size, batch size.
6. **Error codes** and what they mean.

Then try one call by hand (browser, Postman, or a five-line script) before writing the pipeline.

---

## 5. Calling APIs from Python with `requests`

`requests` is the standard Python library for HTTP (`pip install requests`).

```python
import os
import requests

TOKEN = os.getenv("HUBSPOT_TOKEN")                 # from .env, never hard-coded
HEADERS = {"Authorization": f"Bearer {TOKEN}"}
BASE = "https://api.hubapi.com"

# GET with query parameters
r = requests.get(f"{BASE}/crm/v3/objects/companies",
                 params={"limit": 100, "properties": "name,domain"},   # -> ?limit=100&properties=name,domain
                 headers=HEADERS, timeout=10)                           # ALWAYS set a timeout
print(r.status_code)          # 200
data = r.json()               # JSON body -> dict

# POST with a JSON body
body = {"properties": {"name": "PeopleCo GmbH", "domain": "peopleco.de"}}
r = requests.post(f"{BASE}/crm/v3/objects/companies", json=body, headers=HEADERS, timeout=10)

# PATCH to update
r = requests.patch(f"{BASE}/crm/v3/objects/companies/1001",
                   json={"properties": {"fit_score": "95"}}, headers=HEADERS, timeout=10)
```

### 5.1 The response object

| Attribute | What it gives you |
| --- | --- |
| `r.status_code` | `200`, `404`, `429`... |
| `r.ok` | `True` for any 2xx |
| `r.json()` | The body parsed into dicts/lists (fails if the body isn't JSON) |
| `r.text` | The raw body as text (useful for logging error messages) |
| `r.headers.get("Retry-After")` | Seconds to wait, on a 429 |
| `r.raise_for_status()` | Raises `requests.HTTPError` for 4xx/5xx |
| `r.url` | The full URL that was called (check your parameters) |

### 5.2 `params=` vs `json=` vs `data=`

- `params=` → the query string in the URL (filters, limits, cursors).
- `json=` → a JSON body (what most APIs want for POST/PATCH); also sets the `Content-Type` header.
- `data=` → raw or form data (used when you must send exact bytes, e.g. when signing a webhook).

### 5.3 Handling errors

```python
try:
    r = requests.get(url, headers=HEADERS, timeout=10)
    r.raise_for_status()
    data = r.json()
except requests.Timeout:
    ...   # server too slow: temporary, retry
except requests.ConnectionError:
    ...   # network problem or server down: temporary, retry
except requests.HTTPError as e:
    status = e.response.status_code
    ...   # 404 -> "no data"; 429/5xx -> retry; 400/401/403 -> log and stop
```

### 5.4 Sessions and SDKs

- `session = requests.Session(); session.headers.update(HEADERS)` reuses the connection and headers
  for every call: faster and tidier when making many calls to one API.
- Official libraries (`hubspot-api-client`, `anthropic`) wrap the same HTTP calls in Python functions.
  Knowing raw `requests` means you understand what the SDK does, and you can debug it.

---

## 6. Real-world API problems (what separates scripts from systems)

The job post asks for "handling errors and rate limits" and systems "that run reliably at 10x volume".
These six ideas are what that means in code.

### 6.1 Rate limits

A cap on requests per time window. HubSpot's is roughly 100–190 requests per 10 seconds depending on
plan, and its search API is stricter (check the current docs). Go over it and you get **429**, often
with `Retry-After`. A naive script that fires 2,000 calls hits 429 halfway and leaves the CRM
half-updated.

### 6.2 Retries with exponential backoff

```python
import random, time, requests

RETRYABLE = {429, 500, 502, 503, 504}

def request_with_retry(method, url, max_tries=5, **kwargs):
    kwargs.setdefault("timeout", 10)
    for attempt in range(1, max_tries + 1):
        wait = 2 ** (attempt - 1) + random.uniform(0, 0.5)    # 1, 2, 4, 8 s + jitter
        try:
            r = requests.request(method, url, **kwargs)
        except (requests.ConnectionError, requests.Timeout):
            pass                                              # temporary: retry
        else:
            if r.status_code not in RETRYABLE:
                r.raise_for_status()                          # other 4xx: fail fast, no retry
                return r.json() if r.content else None
            wait = float(r.headers.get("Retry-After", wait))  # obey the server
        if attempt < max_tries:
            time.sleep(wait)
    raise RuntimeError(f"Gave up after {max_tries} tries: {method} {url}")
```

Line by line:

- `RETRYABLE` lists the temporary statuses.
- `setdefault("timeout", 10)` gives every call a timeout unless the caller sets one.
- `2 ** (attempt - 1)` doubles the wait each time (exponential backoff); `random.uniform` adds
  **jitter** so many workers don't all retry at the same instant.
- Network errors are temporary, so they're retried too.
- Anything not retryable: `raise_for_status()` raises for 4xx and returns the data for 2xx.
- `Retry-After` overrides our own wait.
- After the last try, raise a clear error so the run logs it and alerts someone. Never loop forever.

### 6.3 Timeouts

`timeout=10` on every call, so one stuck server can't freeze a scheduled job forever.

### 6.4 Pagination

Lists come in pages. Forget to follow the cursor and you silently get only the first page (the classic
bug report: "only 100 contacts synced; we have 2,300").

```python
results, params = [], {"limit": 100}
while True:
    data = request_with_retry("GET", url, params=params, headers=HEADERS)
    results.extend(data.get("results", []))
    after = data.get("paging", {}).get("next", {}).get("after")
    if not after:
        break
    params["after"] = after
```

### 6.5 Batching

Batch endpoints take many records per call (HubSpot: up to 100). 2,000 records = 20 calls instead of
2,000, which keeps you far below the rate limit.

```python
for i in range(0, len(records), 100):
    request_with_retry("POST", batch_url, json={"inputs": records[i:i + 100]}, headers=HEADERS)
```

### 6.6 Idempotency (safe re-runs)

Pipelines get re-run after crashes and on schedules. If they *create* records, every run makes
duplicates. Instead **upsert by a unique key** (e.g. a unique domain property with HubSpot's batch
upsert): update if it exists, create if not. Running twice = running once. Same idea for webhooks
(dedupe event IDs) and alerts (remember what was sent).

Plus two data rules: **never send blank values** (they overwrite real data), and **only write fields
your pipeline owns** (never overwrite a rep's owner or deal stage).

---

## 7. APIs in this role

The job post says the GTM Engineer will "integrate tools via APIs and webhooks". These are the kinds of
APIs you'd work with at Secfix (confirm the exact tools on the intro call).

| System | Example calls | Why |
| --- | --- | --- |
| **CRM** (HubSpot is likely) | List and search companies/contacts/deals; batch upsert companies by domain; update scores; create associations; set owners | Make the CRM the single source of truth |
| **Data providers** (Apollo, Cognism, ZoomInfo…) | Search companies by ICP filters; enrich a domain; find contacts and emails | Fill gaps; build target lists |
| **Clay** | Send rows in via webhook; receive enriched rows out | Enrichment waterfalls without building every integration |
| **Signal sources** (job boards, news, Crunchbase, website-visitor tools) | Fetch recent job posts or funding news for target domains | "Why now" signals for scoring and alerts |
| **Outreach tools** (HubSpot sequences, lemlist, Outreach…) | Enrol contacts in a sequence; fetch replies | Automated, relevant outreach |
| **Slack** | POST a message to an incoming-webhook URL | "Call this account today, because…" alerts and failure alerts |
| **Claude API** | Send website or job-post text, get structured JSON back | Research, classification, briefs, drafts |
| **Your own webhook endpoint** | Receive CRM events (demo booked, contact created) | Inbound routing in seconds |

### What a day of API work looks like

- A BDR says the alert for an account didn't arrive → you check the logs, find a 401 from Slack (the
  webhook URL was rotated), update the secret, re-run.
- The Head of GTM wants hiring signals → you find an API that returns job posts, read its docs, write a
  function that fetches posts for target domains, and detect "ISO 27001" or "compliance" in them.
- The nightly sync got slower → the logs show many 429s; you switch single-record updates to batch
  upserts and only process records changed since the last run.

### How to explain API skills in an interview

> "Every API call goes through one retry function: exponential backoff with jitter, it respects
> Retry-After, retries 429s, 5xx and network errors but never other 4xx, and gives up after five tries
> with an alert. I page through results with the cursor, write in batches, and upsert by a unique key
> so re-running is always safe."

---

## 8. pandas in detail

**pandas** is a Python library for tables (`pip install pandas`; imported as `pd`). A **DataFrame** is a
table with named columns; a **Series** is one column. Think of it as Excel you control with code: one
line can clean a column of 10,000 rows.

### 8.1 Load and look (always look before you write logic)

```python
import pandas as pd

df = pd.read_csv("leads.csv", dtype=str)   # dtype=str: read everything as text; convert on purpose later
df.head()              # first 5 rows
df.shape               # (rows, columns)
df.columns             # column names
df.info()              # types and missing counts
df.isna().sum()        # missing values per column
df["country"].value_counts()   # which values exist, how often (spot "DE" vs "Germany")

df = pd.DataFrame(list_of_dicts)            # from API data
```

In live coding, say "let me look at the data first" and run `head()` and `value_counts()`. It shows you
the traps before they bite.

### 8.2 Select and filter

```python
df["domain"]                          # one column (Series)
df[["name", "domain"]]                # several columns (note the double brackets)
df[df["country"] == "DE"]             # rows matching a condition
df[(df["country"] == "DE") & (df["employees"] >= 20)]   # AND: use & with brackets around each part
df[df["country"].isin(["DE", "AT", "CH"])]              # match a list
df[df["name"].str.contains("tech", case=False, na=False)]   # text search
df.loc[df["score"] >= 75, ["name", "score"]]            # rows + columns at once
```

How a filter works: `df["country"] == "DE"` produces a column of True/False; `df[...]` keeps the rows
where it's True.

### 8.3 Clean and transform

```python
df["industry"] = df["industry"].str.strip().str.lower()          # whole column at once
df["country"] = df["country"].str.lower().map({"germany": "DE"}).fillna(df["country"])   # mapping
df["domain"] = df["website"].apply(normalize_domain)              # your own function on every value
df["employees"] = pd.to_numeric(df["employees"], errors="coerce") # text -> numbers; bad -> NaN
df = df.dropna(subset=["domain"])                                 # drop rows missing a key
df["industry"] = df["industry"].fillna("Unknown")                 # fill blanks
```

### 8.4 Dedupe, sort, group, merge

```python
# dedupe keeping the most complete row: sort best-first, then keep the first per key
df["filled"] = df.notna().sum(axis=1)
df = df.sort_values("filled", ascending=False).drop_duplicates(subset="domain", keep="first")

df.sort_values("score", ascending=False).head(10)                 # top 10
df.groupby("country")["score"].mean()                             # average per group
df.groupby("owner").agg(accounts=("domain", "count"), avg=("score", "mean"))

merged = leads.merge(crm[["domain", "owner"]], on="domain", how="left", indicator=True)
# _merge == "both": already in the CRM; "left_only": brand new
```

"Sort so the best row is first, then keep the first" is the sentence to say in interviews when asked
how you dedupe.

### 8.5 Export

```python
df.to_csv("clean.csv", index=False)
records = df.astype(object).where(df.notna(), None).to_dict(orient="records")   # list of dicts, NaN -> None
df.to_sql("accounts", con, if_exists="replace", index=False)                   # into a SQL database
```

### 8.6 pandas traps

| Trap | Fix |
| --- | --- |
| Using `and`/`or` in filters | Use `&` / `\|` with brackets around each condition |
| Numbers read as text (`object`) | `pd.to_numeric(..., errors="coerce")` |
| `NaN` in records sent to an API | Convert to `None` and drop empty fields |
| `SettingWithCopyWarning` | Use `df = df[...].copy()` or `df.loc[mask, "col"] = value` |
| An extra index column in CSVs | `to_csv(..., index=False)` |
| Slow row-by-row `apply(axis=1)` on huge data | Vectorised operations (`np.where`, `.str`, `.isin`) |

---

## 9. pandas in this role

The job post says "pull data from multiple sources, deduplicate, score and write it back". pandas is
the "deduplicate, score" part, plus most reporting.

| Task | What you do with pandas |
| --- | --- |
| Clean an exported lead list | Normalise domains, countries and industries; parse employee ranges like "51-200"; drop personal emails |
| Dedupe across sources | Combine Apollo + webinar + CRM exports, key on normalised domain, keep the most complete row |
| Match against the CRM | `merge` new leads with existing accounts: who's new, who already has an owner |
| Score | Add fit and intent columns with `np.where` or functions; tiers; reasons |
| Find data-quality problems | Duplicate domains, missing industries, accounts without owners, counts per source |
| Report to the GTM team | Leads per source per month, meeting rate by source, speed to lead, pipeline per owner |
| Prepare records for the CRM | `to_dict("records")` with NaN removed, ready for batch upsert |

### 9.1 Example: messy export → clean, scored, matched

```python
import numpy as np
import pandas as pd

leads = pd.read_csv("apollo_export.csv", dtype=str)
crm = pd.read_csv("crm_companies.csv", dtype=str)

leads["domain"] = (leads["website"].fillna(leads["email"]).fillna("").str.lower().str.strip()
                   .str.replace(r"^https?://", "", regex=True).str.replace(r"^www\.", "", regex=True)
                   .str.split("/").str[0].str.split("@").str[-1])
leads = leads[(leads["domain"] != "") & ~leads["domain"].isin(["gmail.com", "yahoo.com"])]

leads["filled"] = leads.notna().sum(axis=1)
leads = leads.sort_values("filled", ascending=False).drop_duplicates("domain")

leads["employees"] = pd.to_numeric(leads["employees"], errors="coerce")
leads["fit"] = (np.where(leads["industry"].isin(["Software", "Fintech"]), 25, 0)
                + np.where(leads["employees"].between(20, 500), 20, 0)
                + np.where(leads["country"].isin(["DE", "AT", "CH", "NL", "BE", "LU"]), 15, 0))

leads = leads.merge(crm[["domain", "owner"]], on="domain", how="left")
print(leads["owner"].isna().sum(), "new companies;", (leads["fit"] >= 50).sum(), "strong fits")
```

### 9.2 Example: a weekly report the Head of GTM might ask for

```python
inbound = pd.read_csv("inbound_leads.csv", parse_dates=["created_at", "first_contacted_at"])
inbound["minutes_to_contact"] = (inbound["first_contacted_at"] - inbound["created_at"]).dt.total_seconds() / 60
report = inbound.groupby("source").agg(
    leads=("email", "count"),
    meeting_rate=("meeting_booked", "mean"),
    median_minutes_to_contact=("minutes_to_contact", "median"),
)
```

That one table answers "which sources produce meetings, and are we responding fast enough?" (Try it on
this repo's `data/inbound_leads.csv`.)

### 9.3 pandas or plain Python?

Use pandas for **whole-table** work: cleaning, deduping, grouping, joining, reports. Use plain dicts
and lists for **record-by-record** work: API calls, routing one lead, handling a webhook. Most
pipelines do both: pandas to clean and score, then `to_dict("records")` and a loop to send.

---

## 10. All three together: an end-to-end example

[code/json_apis_pandas_demo.py](code/json_apis_pandas_demo.py) is a runnable version of the loop in
section 1, using this repo's local practice API (it rate-limits and fails randomly like a real one):

```powershell
# Terminal 1
python 06-apis-and-webhooks/practice_server.py
# Terminal 2
python 15-deep-dives/code/json_apis_pandas_demo.py
```

What it does, step by step:

1. **API + JSON:** pages through every company already in the "CRM" with a retry function, and turns
   the JSON into a DataFrame.
2. **pandas:** loads `data/leads_raw.csv`, normalises domains (website, falling back to email), drops
   personal emails, dedupes keeping the most complete row, converts employee counts, scores fit.
3. **pandas:** keeps only companies that aren't in the CRM yet.
4. **pandas → Python → JSON:** converts rows to clean records (NaN removed, blanks dropped).
5. **API:** batch-upserts them in batches of 10 (the practice API's limit), then runs the upsert again
   to prove the second run creates nothing.

The same code works against HubSpot by changing the base URL, the auth header, the endpoint paths and
the batch size (100). [07-crm-hubspot/hubspot_client.py](../07-crm-hubspot/hubspot_client.py) shows the
HubSpot-specific calls.

In a real project you'd split this into files (extract / transform / load), add logging, a summary
line, a `--dry-run` flag and tests (see [10-production-habits](../10-production-habits)).

---

## 11. Interview questions, with answers

### JSON

| Question | Answer |
| --- | --- |
| What is JSON, and why do APIs use it? | A plain-text format for structured data (objects, arrays, strings, numbers, booleans, null). Every language can read and write it, so it's the common language between systems. |
| How does JSON map to Python? | Object → dict, array → list, string → str, number → int/float, true/false → True/False, null → None. |
| How do you read a nested field that might be missing? | `.get()` with a default at each level, and `or {}` when a value may be null: `item.get("properties") or {}`. |
| An AI step sometimes returns "Sure! Here's the JSON...". What do you do? | Parse inside try/except, validate every field against allowed values, retry once, then send it to a review list. Never write unvalidated output to the CRM. |
| Your API call fails with "nan is not JSON compliant". Why? | pandas NaN in the payload. Convert NaN to None and drop empty fields before sending. |

### APIs

| Question | Answer |
| --- | --- |
| Explain an API to a sales rep | "It's how our tools talk to each other: our system asks HubSpot for data or tells it to update a company, like a waiter taking an order to the kitchen." |
| GET vs POST vs PATCH? | Read; create or send an action; update some fields. |
| What do 401, 404 and 429 mean, and what do you do? | Bad key: fix it, don't retry. Not found: handle it (no data). Rate limited: wait (Retry-After) and retry with backoff. |
| The API sometimes returns 429 and the job dies. Fix it. | One retry function: exponential backoff with jitter, respect Retry-After, retry 429/5xx/network only, max 5 tries, then log and alert. Batch requests to avoid hitting it. |
| It only gets the first 100 records. Why? | No pagination. Loop on the next-page cursor until it's missing. |
| Every run creates duplicate companies. Why? | It creates instead of upserting. Batch upsert by a unique key (domain) so re-running is safe; add a test that runs it twice. |
| How do you keep API keys safe? | `.env` + `.gitignore`, a `.env.example`, secrets in CI settings, least-privilege scopes, rotate if leaked. |
| Webhook vs polling? | Polling asks "anything new?" on a schedule; a webhook calls you the moment something happens. Webhooks for speed (inbound routing), scheduled syncs for bulk work. |

### pandas

| Question | Answer |
| --- | --- |
| How do you dedupe accounts and keep the best record? | Normalise the domain, count filled fields per row, sort so the most complete is first, then `drop_duplicates(subset="domain", keep="first")`. |
| How do you find which new leads are already in the CRM? | `merge(crm, on="domain", how="left", indicator=True)`; `_merge == "both"` means existing. |
| A numeric column shows as `object`. Why? | Some values are text ("51-200", "abc"). Use `pd.to_numeric(errors="coerce")` plus a rule for ranges. |
| Count leads per source per month | `df.groupby(["source", df["created_at"].str[:7]]).size()` |
| When would you use pandas vs plain Python? | pandas for whole-table cleaning, deduping, grouping and joins; dicts and lists for record-by-record API calls and webhooks. |
| How do you prepare a DataFrame for an API? | `df.astype(object).where(df.notna(), None).to_dict("records")`, then drop None fields and convert types the API expects. |

### The answer that ties it together

> "APIs bring data in and send it out, JSON is the format it travels in, and pandas is where I clean
> it. In practice: page through the provider and CRM APIs with retries, turn the JSON into DataFrames,
> normalise and dedupe on domain, score with reasons, then convert back to clean records and
> batch-upsert by a unique key, so the CRM stays the single source of truth and reps only see each
> company once."

### Practise

- [06-apis-and-webhooks](../06-apis-and-webhooks): lessons 1–3 and the API exercise against the local
  practice API.
- [04-pandas](../04-pandas): lessons 1–5 and the exercise.
- [03-python/lessons/10_files_csv_json.py](../03-python/lessons/10_files_csv_json.py) for JSON files.
- [code/json_apis_pandas_demo.py](code/json_apis_pandas_demo.py) for all three together.
