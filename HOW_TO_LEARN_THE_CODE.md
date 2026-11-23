# How to learn the code (don't memorise it, rebuild it)

Once the code makes sense when you read it, the natural question is: *do I have to learn it by heart?*
**No.** Blocks like normalising, loading data, retries and pagination look almost the same every time.
The goal is to know them well enough to **rebuild and adapt** them, not to recite them.

## Why memorising word for word doesn't work

- **The pattern stays the same, but the details change every time:** column names (`website` vs
  `company_url`), the shape of the API response (`results` vs `data.items`), the key (domain vs email),
  the batch size (10 vs 100). Recited code breaks the moment the details change.
- **The live round asks you to change code:** "now also handle emails", "now skip gmail", "why `>=`
  here?". You can only do that if you understand the logic.

## The three levels

| Level | What it means | For which topics |
| --- | --- | --- |
| **1. Recognise** | You can read it and say what it does | Everything in this repo |
| **2. Explain** | You can say *why* each line is there and what breaks without it | Everything you'd put in a take-home |
| **3. Rebuild** | You can write it from an empty file, in your own words, adapting the details | The 6 core patterns below |

## How to practise one pattern (the method)

1. **Read it** until you understand it.
2. **Close the file.** Write the steps as comments in plain English.
3. **Fill in the code** under each comment. Looking things up is allowed.
4. **Run the checks:** `python 15-deep-dives/code/core_patterns_drill.py`.
5. **Do it again 2–3 days later** from scratch. The second time is what makes it stick.
6. **Change the details on purpose** (the "variations" under each pattern). If you can adapt it, you
   truly know it.

Memorise the **recipe** (the steps in plain words), not the exact text. The code follows from the
recipe.

---

## The 6 core patterns

Each one is 5–15 lines. For each: the recipe, a reference version, and variations to practise. Write
your own versions in [15-deep-dives/code/core_patterns_drill.py](15-deep-dives/code/core_patterns_drill.py);
reference solutions are in [core_patterns_solutions.py](15-deep-dives/code/core_patterns_solutions.py).

### 1. Normalise a domain

**Why:** the same company arrives as `https://www.PeopleCo.de/about`, `peopleco.de` and
`anna@PeopleCo.de`. Until they're the same string, you can't dedupe or match them.

**Recipe:**

```python
# 1. if the value is empty or None, return ""
# 2. strip spaces and lowercase it
# 3. if there's an @, keep the part after it (an email)
# 4. remove https://, http:// and www. from the start
# 5. cut at the first / and keep the left part
```

**Reference:**

```python
def normalize_domain(value):
    if not value:
        return ""
    v = value.strip().lower()
    if "@" in v:
        v = v.split("@")[-1]
    for prefix in ("https://", "http://", "www."):
        if v.startswith(prefix):
            v = v[len(prefix):]
    return v.split("/")[0]
```

**Variations:** also strip a trailing dot (`peopleco.de.`); return `""` for personal domains (gmail.com);
remove a port (`peopleco.de:8080`).

### 2. Dedupe, keeping the best row

**Why:** merging lists from several sources creates duplicates; the CRM must have each company once.

**Recipe:**

```python
# 1. make an empty dict: key -> (how complete, row)
# 2. for each row: work out its key (normalised domain); skip rows with no key
# 3. count how many fields are filled in
# 4. if the key is new, or this row is more complete than the stored one, store this row
# 5. return the stored rows
```

**Reference:**

```python
def dedupe(rows):
    best = {}
    for row in rows:
        key = normalize_domain(row.get("website") or row.get("email"))
        if not key:
            continue
        filled = sum(1 for v in row.values() if v not in (None, ""))
        if key not in best or filled > best[key][0]:
            best[key] = (filled, row)
    return [row for _, row in best.values()]
```

**pandas version:** sort the best row first, then keep the first:
`df.sort_values("filled", ascending=False).drop_duplicates(subset="domain", keep="first")`.

**Variations:** keep the most *recent* row (`updated_at`) instead; dedupe contacts on lowercase email;
merge fields from the losing row into the winner instead of discarding it.

### 3. Retry with exponential backoff

**Why:** real APIs rate-limit you (429) and sometimes fail (5xx). Without retries, one blip kills the
run and leaves the CRM half-updated.

**Recipe:**

```python
# 1. loop over attempts 1..max_tries
# 2. work out the wait: base * 2 ** (attempt - 1), plus a little random jitter
# 3. try the request (with a timeout); a network error counts as a temporary failure
# 4. if the status is NOT temporary (not 429/5xx): raise for 4xx, return the JSON for 2xx
# 5. if the server sent Retry-After, use that as the wait
# 6. sleep, then try again (but not after the last attempt)
# 7. after the loop: raise an error saying we gave up
```

**Reference:**

```python
RETRYABLE = {429, 500, 502, 503, 504}

def request_with_retry(method, url, max_tries=5, **kwargs):
    kwargs.setdefault("timeout", 10)
    for attempt in range(1, max_tries + 1):
        wait = 2 ** (attempt - 1) + random.uniform(0, 0.5)
        try:
            r = requests.request(method, url, **kwargs)
        except (requests.ConnectionError, requests.Timeout):
            pass
        else:
            if r.status_code not in RETRYABLE:
                r.raise_for_status()
                return r.json() if r.content else None
            wait = float(r.headers.get("Retry-After", wait))
        if attempt < max_tries:
            time.sleep(wait)
    raise RuntimeError(f"Gave up after {max_tries} tries: {method} {url}")
```

**Variations:** count and log how many retries happened; treat 404 as "no data" (return None) for an
enrichment endpoint; cap the maximum wait at 30 seconds.

### 4. Pagination

**Why:** APIs return big lists one page at a time. Forget to follow the cursor and you silently get only
the first page ("only 100 contacts synced; we have 2,300").

**Recipe:**

```python
# 1. start with an empty results list and params = {"limit": N}
# 2. loop forever:
# 3.   call the API with the params; add this page's results to the list
# 4.   read the next-page cursor (safely, with .get at each level)
# 5.   if there's no cursor, stop and return the list
# 6.   otherwise put the cursor in params["after"] and go round again
```

**Reference:**

```python
def get_all(url, headers):
    results, params = [], {"limit": 100}
    while True:
        data = request_with_retry("GET", url, params=params, headers=headers)
        results.extend(data.get("results", []))
        after = data.get("paging", {}).get("next", {}).get("after")
        if not after:
            return results
        params["after"] = after
```

**Variations:** an API that uses `page=1, 2, 3…` and stops when a page is empty; an API that returns a
full `next` URL instead of a cursor; stop early after N records for a test run.

### 5. Batching

**Why:** batch endpoints accept many records per call (HubSpot: up to 100). Fewer calls means staying
under the rate limit and finishing faster.

**Recipe:**

```python
# 1. loop i from 0 to len(records), stepping by the batch size
# 2. slice records[i : i + size] to get one batch
# 3. send the batch; add up created/updated counts from each response
```

**Reference:**

```python
def upsert_in_batches(records, size=100):
    totals = {"created": 0, "updated": 0}
    for i in range(0, len(records), size):
        result = request_with_retry("POST", BATCH_URL, json={"inputs": records[i:i + size]}, headers=HEADERS)
        totals["created"] += result["created"]
        totals["updated"] += result["updated"]
    return totals
```

**Variations:** strip empty values from each record before sending (never write blanks); log which batch
failed and continue with the next; a pure helper `batches(items, size)` that returns a list of lists.

### 6. Per-record error handling

**Why:** real data always has a few broken rows. One bad row must not stop the other 2,000; but every
failure must be logged so someone can fix it.

**Recipe:**

```python
# 1. make empty lists for good results and failures
# 2. for each record:
# 3.   try: process it and add the result to the good list
# 4.   except: add it to failures and log WHICH record and WHY
# 5. after the loop: log a summary (how many ok, how many failed)
# 6. if too many failed (e.g. over 10%), raise an alert: it's probably a systemic problem
```

**Reference:**

```python
def process_all(records, process):
    ok, failed = [], []
    for rec in records:
        try:
            ok.append(process(rec))
        except Exception as e:
            failed.append(rec.get("domain"))
            log.warning("Failed on %s: %s", rec.get("domain"), e)
    log.info("SUMMARY ok=%d failed=%d", len(ok), len(failed))
    if records and len(failed) / len(records) > 0.10:
        log.error("ALERT: more than 10%% of records failed")
    return ok, failed
```

**Variations:** catch only `ValueError` and let other errors crash loudly; copy each record before
changing it (`dict(rec)`) so the input stays intact; write failures to a CSV for review.

---

## How these combine (the whole job in one breath)

A pipeline is these six patterns in a row: **paginate** to read everything, **normalise** and
**dedupe**, score with simple rules, then **batch** the writes, with every API call going through
**retry** and every record wrapped in **per-record error handling**. If you can rebuild the six, you can
build the take-home and handle most live-coding changes.

## A weekly rhythm that works

| Day | Do |
| --- | --- |
| Learn a pattern | Read it in the lessons until it makes sense |
| Same day | Rebuild it from comments in the drill file; run the checks |
| 2–3 days later | Rebuild it again from an empty function, without looking |
| Then | Do one variation; explain it out loud in 2 minutes |
| End of the week | Combine two or three patterns in one small script (e.g. paginate + normalise + dedupe) |

## Where else to practise

- Python exercises: [03-python/exercises](03-python/exercises)
- pandas exercise: [04-pandas/exercises](04-pandas/exercises)
- API client exercise (retry, pagination, batching against the local practice API):
  [06-apis-and-webhooks/exercises](06-apis-and-webhooks/exercises)
- 12 live-coding problems: [13-interview-prep/live_coding_practice](13-interview-prep/live_coding_practice)
