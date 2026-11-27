# Step 1 (continued): Pagination, rate limits, retries, batching, checkpoints

APIs never give you 50,000 rows in one response, never let you call as fast as you like, and
sometimes fail for no reason. This chapter is the "plumbing" that makes collection (step 1) and
write-back (step 9) reliable. Interviewers ask about it constantly.

## 2.0 Start from zero

These are the three facts of life of every API:

1. **It answers in pages** (pagination). You must keep asking for the next page.
2. **It has a speed limit** (rate limit). Go too fast and it says 429 "slow down".
3. **It sometimes fails for no reason** (timeouts, 500s). Usually it works if you try again a bit later.

And one way to be efficient: **send many records per call** (batching).

| Idea | One-line picture |
| --- | --- |
| Pagination | Reading a long catalogue one page at a time, following "continued on page 2" |
| Rate limit | A coffee shop that serves 10 people per minute |
| Backoff | Waiting 1 s, then 2 s, then 4 s before trying again |
| Jitter | Adding a random few hundred milliseconds so everyone doesn't retry together |
| Batching | Posting 100 letters in one parcel |
| Checkpoint | A bookmark so a crash resumes instead of restarting |
| Idempotency | Pressing the lift button twice doesn't call two lifts |

**Why this chapter decides whether a pipeline is "real":** the logic of scoring is easy. What breaks in
production is the plumbing: the sync that silently stopped after page 1, the run that died on one
429, the retry that created a duplicate. Interviewers probe exactly here.

**How to read the code:** every snippet is one of the 6 core patterns (normalise, dedupe, retry,
paginate, batch, per-record errors), see [chapter 15](15-the-6-core-patterns-in-the-pipeline.md).

## 2.1 Pagination: the four styles

| Style | How you ask | How you know there's more | Who uses it | Gotcha |
| --- | --- | --- | --- | --- |
| **Page number** | `page=1&per_page=100` | `pagination.total_pages` or a short page | Apollo, many SaaS APIs | Rows shift if data changes mid-pull; hard caps (Apollo: 500 pages × 100) |
| **Offset / limit** | `offset=200&limit=100` | fewer than `limit` rows returned | SQL-style APIs, Clay HTTP source | Slow at deep offsets; same shifting problem |
| **Cursor** | `after=<token from last response>` | `paging.next.after` present | HubSpot, Stripe, Slack | Cursor is opaque: store it, don't compute it |
| **Link header / next URL** | follow `next` URL | `Link: <...>; rel="next"` or `next` field | GitHub, many REST APIs | Use the full URL as given |
| **Keyset (seek)** | `updated_after=<last seen timestamp>` | empty page | Incremental syncs | Need a stable sort + tie-breaker (timestamp + id) |

### Page number (Apollo style)

```python
def fetch_all_pages(fetch_page, per_page=100, max_pages=500):
    page = 1
    while page <= max_pages:
        body = call_with_retry(lambda: fetch_page(page, per_page))
        rows = body.get("people", [])
        yield from rows                                   # a generator: memory stays flat
        total_pages = body["pagination"]["total_pages"]
        if page >= total_pages or not rows:
            break
        page += 1
```

### Cursor (HubSpot style)

```python
def fetch_all_companies(session):
    after = None
    while True:
        params = {"limit": 100, "properties": "name,domain,hubspot_owner_id"}
        if after:
            params["after"] = after
        resp = call_with_retry(lambda: session.get(
            "https://api.hubapi.com/crm/v3/objects/companies", params=params, timeout=30))
        body = resp.json()
        yield from body["results"]
        after = body.get("paging", {}).get("next", {}).get("after")
        if not after:                                     # no next cursor = last page
            break
```

### Beating a hard cap: slice the query

Apollo shows at most 50,000 results per search. If your filters match 120,000 people, you can't page
past row 50,000. Split the search into slices that are each under the cap, then dedupe the union:

```python
slices = [{"organization_locations": [c]} for c in ["Germany", "Austria", "Switzerland"]]
size_bands = ["20,50", "51,200", "201,500"]
for loc in slices:
    for band in size_bands:
        filters = {**base_filters, **loc, "organization_num_employees_ranges": [band]}
        for person in fetch_all_pages(lambda p, n: apollo_people_search(p, n, **filters)):
            land(person)
```

### Incremental pulls (only what changed)

```python
last_sync = state.get("companies_last_sync", "1970-01-01T00:00:00Z")
body = {"filterGroups": [{"filters": [{"propertyName": "hs_lastmodifieddate",
                                       "operator": "GTE", "value": last_sync}]}],
        "sorts": [{"propertyName": "hs_lastmodifieddate", "direction": "ASCENDING"}],
        "limit": 100}
# ... page through the search, then save the max hs_lastmodifieddate seen as the new last_sync
```

Full runs weekly (to catch deletes and drift), incremental runs hourly or daily.

## 2.2 Rate limits

| Term | Meaning |
| --- | --- |
| **Rate limit** | Max requests per time window (e.g. per 10 s, per minute, per hour, per day). Several can apply at once. |
| **429 Too Many Requests** | "Slow down." Often with a `Retry-After` header (seconds) |
| **Burst vs sustained** | Some APIs allow short bursts above the average |
| **Quota / credits** | A separate budget (daily calls, monthly credits); hitting it isn't fixed by waiting a few seconds |
| **Per-endpoint limits** | Search endpoints are often stricter than CRUD endpoints (HubSpot search ≈ 5 req/s) |

### Proactive: throttle so you rarely see a 429

```python
import time

class Throttle:
    """Simple token bucket: at most `rate` calls per second on average."""
    def __init__(self, rate):
        self.interval, self.next_ok = 1.0 / rate, 0.0
    def wait(self):
        now = time.monotonic()
        if now < self.next_ok:
            time.sleep(self.next_ok - now)
        self.next_ok = max(now, self.next_ok) + self.interval

hubspot_search = Throttle(rate=4)        # stay under ~5/s
hubspot_search.wait(); resp = session.post(url, json=body, timeout=30)
```

### Reactive: retry with exponential backoff + jitter

```python
import random, time, requests

RETRYABLE = {429, 500, 502, 503, 504}

def call_with_retry(make_request, max_attempts=5, base=1.0, cap=60):
    for attempt in range(1, max_attempts + 1):
        try:
            resp = make_request()
        except (requests.ConnectionError, requests.Timeout):
            resp = None                                    # network blip: retryable
        if resp is not None and resp.status_code not in RETRYABLE:
            resp.raise_for_status()                        # 400/401/403/404: fail fast, don't retry
            return resp
        if attempt == max_attempts:
            raise RuntimeError(f"gave up after {attempt} attempts")
        retry_after = resp.headers.get("Retry-After") if resp is not None else None
        delay = float(retry_after) if retry_after else min(cap, base * 2 ** (attempt - 1))
        time.sleep(delay + random.uniform(0, delay * 0.25))   # jitter
```

Why each piece:
- **Exponential** (1, 2, 4, 8 s): gives the server room to recover.
- **Cap**: never wait forever on one call.
- **Jitter**: if 10 workers all got a 429 at once, they shouldn't all retry at the same millisecond.
- **Only retry retryable errors**: a 400 (bad request) will fail the same way every time; a 401
  means your key is wrong.
- **Libraries that do this for you:** `tenacity` (decorator), `urllib3.Retry` mounted on a requests
  `HTTPAdapter`, `backoff`.

```python
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
retry = Retry(total=5, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504],
              allowed_methods=["GET", "POST"], respect_retry_after_header=True)
session.mount("https://", HTTPAdapter(max_retries=retry))
```

Careful with retrying **POSTs that create things**: if the first attempt actually succeeded and only
the response was lost, a retry creates a duplicate. That's why writes use **upserts** (chapter 08) or
idempotency keys.

## 2.3 Batching

Batch endpoints take many records per call: fewer calls, fewer 429s, faster runs.

| API | Batch size |
| --- | --- |
| HubSpot `batch/create`, `batch/update`, `batch/upsert`, `batch/read` | up to 100 |
| Apollo `people/bulk_match`, `organizations/bulk_enrich` | up to 10 |
| Salesforce Composite / sObject Collections | up to 200 records; Bulk API 2.0 for millions |

```python
def chunks(items, size):
    for i in range(0, len(items), size):
        yield items[i:i + size]

for batch in chunks(payloads, 100):
    call_with_retry(lambda: session.post(
        "https://api.hubapi.com/crm/v3/objects/contacts/batch/upsert",
        json={"inputs": batch}, timeout=60))
```

Partial failures: some batch APIs return `207 Multi-Status` with per-record errors. Log each failed
record with its reason and retry only those, don't resend the whole batch blindly.

## 2.4 Concurrency (only when needed)

```python
from concurrent.futures import ThreadPoolExecutor
with ThreadPoolExecutor(max_workers=4) as pool:          # small pool, shared Throttle
    results = list(pool.map(enrich_one_domain, domains))
```

More workers ≠ faster once you hit the rate limit; it just means more 429s. Start sequential.

## 2.5 Checkpoints and resume

A 40-minute pull that dies at minute 39 shouldn't restart from page 1.

```python
import json, pathlib
STATE = pathlib.Path("state/apollo_pull.json")

state = json.loads(STATE.read_text()) if STATE.exists() else {"page": 1}
page = state["page"]
while True:
    body = call_with_retry(lambda: apollo_people_search(page))
    land(body["people"])
    STATE.write_text(json.dumps({"page": page + 1}))   # save AFTER landing the page
    if page >= body["pagination"]["total_pages"]:
        STATE.unlink(); break
    page += 1
```

## 2.6 Credit budgets

```python
budget, used = 500, 0
for person in candidates:
    if used + COST_PER_ENRICH > budget:
        log.warning("credit budget reached, %d people left for the next run", remaining)
        break
    result = cached_or_enrich(person)       # cache first (chapter 05)
    if result.charged:
        used += COST_PER_ENRICH
```

In the demo: `call_with_retry`, `fetch_all_pages_page_number`, `fetch_all_pages_cursor`, `batches`,
and the credit budget in `enrich` ([code/pipeline_end_to_end.py](code/pipeline_end_to_end.py)).
The local practice API in [06-apis-and-webhooks](../06-apis-and-webhooks) rate-limits and fails like
a real one, so you can test all of this for real.

## 2.7 Interview lines

> "On a 429 I back off exponentially with jitter and respect Retry-After; I don't retry 4xx errors
> other than 429. Writes go through batch upserts so a retry can't create duplicates."

> "If a search is capped, like Apollo's 50,000 rows, I slice the query by country or size band so
> each slice is under the cap, then dedupe the union."

> "Long pulls checkpoint after each page so a crash resumes instead of restarting, and enrichment
> has a credit budget per run."

## 2.8 Summary

- Know the four pagination styles; **always loop until there's no next page**, and slice queries that
  hit hard caps.
- **Throttle proactively, retry reactively**: exponential backoff + jitter, obey `Retry-After`, only
  retry 429/5xx/network errors, cap attempts.
- **Batch** writes and enrichment (HubSpot 100, Apollo 10); handle partial failures per record.
- Long pulls **checkpoint**; enrichment has a **credit budget**.
- Retried *writes* must be idempotent (upserts), or a lost response becomes a duplicate.

## 2.9 Key functions to remember

| Function | Input → output | Core pattern |
| --- | --- | --- |
| `fetch_all_pages(fetch_page)` / `fetch_all_pages_page_number` | page fetcher → generator of records | 4 pagination |
| `fetch_all_companies` / `fetch_all_pages_cursor` | session → generator of records | 4 pagination |
| `call_with_retry(make_request)` | a zero-argument function → its result, or a clear error | 3 retry |
| `Throttle(rate).wait()` | — → sleeps just enough | (proactive limit) |
| `chunks(items, size)` / `batches` | list → list slices | 5 batching |

## 2.10 Important logic

| Response | Retry? | Why |
| --- | --- | --- |
| 200/201/204 | No, done | Success |
| 400, 422 | No | Your payload is wrong; it fails every time |
| 401, 403 | No | Key or permission problem; alert a human |
| 404 | No (enrichment: treat as "no data") | Doesn't exist |
| 409 | No; switch to upsert | Duplicate unique value |
| 429 | **Yes**, wait `Retry-After` or backoff | Temporary |
| 500/502/503/504, timeout, connection error | **Yes**, with backoff | Usually temporary |
| Still failing after max attempts | Stop, raise, alert | Don't loop forever |

## 2.11 Check yourself

1. Your HubSpot sync always ends with exactly 100 companies. What's the bug?
2. Why add jitter if you already have exponential backoff?
3. A POST create timed out and you retried it. What could go wrong, and how do you prevent it?
4. 120,000 people match a search capped at 50,000. What do you do?

<details><summary>Answers</summary>

1. It reads only the first page and never follows `paging.next.after`.
2. Many workers that failed together would otherwise retry at the same instants and collide again.
3. The first call may have succeeded; the retry creates a duplicate. Use upsert by a unique key (or an idempotency key).
4. Split into slices under the cap (country × size band), pull each, then dedupe the union.
</details>
