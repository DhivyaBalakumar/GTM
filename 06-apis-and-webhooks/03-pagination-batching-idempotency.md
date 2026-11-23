# 3. Pagination, batching and idempotency

## Pagination: big lists come in pages

APIs never return 50,000 records at once. They return a **page** (e.g. 100) plus a pointer to the
next page. If you forget to follow the pointer, you silently get only the first page. (Classic bug
report: "only 100 contacts sync, we have 2,300".)

| Style | How you ask for the next page | Example |
| --- | --- | --- |
| **Cursor** | Pass the `after` token from the last response | HubSpot: `paging.next.after` |
| **Offset / limit** | `?offset=100&limit=100`, then 200… | Many SQL-backed APIs |
| **Page number** | `?page=2` | Simple APIs |
| **Link header / next URL** | Follow the `next` URL given | GitHub |

Cursor pagination is the most reliable: offsets can skip or repeat records if data changes while
you're paging.

```python
def get_all(url, headers):
    results, params = [], {"limit": 100}
    while True:
        data = request_with_retry("GET", url, params=params, headers=headers)
        results.extend(data.get("results", []))
        after = data.get("paging", {}).get("next", {}).get("after")
        if not after:
            break
        params["after"] = after
    return results
```

Paging through big lists uses many requests, so it still goes through the retry function.

## Batching: many records per request

Most CRMs have batch endpoints (HubSpot batch endpoints accept up to 100 records per call). Sending
2,000 records one by one = 2,000 calls; in batches of 100 = 20 calls.

```python
for i in range(0, len(records), 100):
    batch = records[i:i + 100]
    request_with_retry("POST", BATCH_URL, json={"inputs": batch}, headers=headers)
```

Handle **partial failures**: a batch can succeed for 98 records and fail for 2 (e.g. an invalid
value). Log which ones failed and why; don't silently drop them.

## Idempotency: running twice = running once

Pipelines get re-run all the time: on a schedule, after a crash, by a human who wasn't sure it ran.
If your code just **creates** records, every run makes duplicates. An **idempotent** operation gives
the same result no matter how many times you run it.

### How to make writes idempotent

1. **Upsert by a unique key.** "Update if it exists, create if it doesn't." In HubSpot: mark a
   property (e.g. `domain`) as unique and use the batch upsert endpoint with `idProperty`. In SQL:
   `INSERT … ON CONFLICT(domain) DO UPDATE`.
2. **Search, then create or update** (slower, and search indexes can lag a few seconds, so two quick
   runs can still duplicate; batch upsert is better).
3. **Idempotency keys:** some APIs (e.g. payments) let you send a unique `Idempotency-Key` header; a
   repeated request with the same key is ignored.
4. **Remember what you've done:** for alerts and emails, store "alert sent for account X, signal Y"
   so a re-run doesn't send it again.

### Never write blanks

If a source has no employee count, don't send `employees: ""` or `null`: it would erase a good value
that a rep or another source added. Only send fields you actually have.

### Field ownership

Decide which system owns which field. Your pipeline might own `fit_score` and `score_reasons`; the
CRM (people) owns `owner` and `deal stage`. Your code never overwrites fields it doesn't own.

## Interview phrasing

> "Writes are batch upserts keyed on a unique domain property, in batches the API allows, so
> re-running is safe and recovery after a crash is just 'run it again'. I never send blank values,
> and the pipeline only writes the fields it owns, so it can't undo a rep's edits."

Next: [04-webhooks.md](04-webhooks.md)
