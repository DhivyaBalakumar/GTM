# 2. Rate limits and retries

## What a rate limit is

A cap on how many requests you may send in a time window, for example "100 requests per 10 seconds"
(HubSpot's limits are roughly in this range and depend on the plan; check the current docs). It
exists so one customer can't overload a service shared by thousands, like a bank counter limiting
each person to a few transactions at a time.

Go over it and the server answers **429 Too Many Requests**, often with a **`Retry-After`** header
saying how many seconds to wait.

There are often several limits at once: per second, per day, per endpoint (search endpoints are often
stricter).

## Why it matters for GTM pipelines

A beginner's script sends 2,000 requests as fast as possible, hits 429 halfway, and crashes, leaving
the CRM half-updated. That's why the job post asks for "handling errors and rate limits".

## The five things good code does

1. **Wait and retry** the same request after a 429.
2. **Back off exponentially:** wait longer after each failure (1, 2, 4, 8, 16 seconds), like knocking
   on a door less often when nobody answers.
3. **Add jitter:** a small random extra wait, so many workers don't all retry at the same instant.
4. **Obey `Retry-After`** when the server sends it.
5. **Give up eventually:** after about 5 tries, stop, log it, and alert. Never loop forever.

Plus, prevent the problem in the first place:

- **Batch:** one request with 100 records instead of 100 requests.
- **Throttle:** deliberately pace yourself (e.g. a short sleep between calls).
- **Cache / only fetch what changed:** don't re-enrich companies you enriched last week.

## What to retry and what not

| Situation | Retry? | Why |
| --- | --- | --- |
| 429 | Yes | Temporary: you were too fast |
| 500, 502, 503, 504 | Yes | Temporary: server trouble |
| Connection error, timeout | Yes | Temporary: network |
| 400, 401, 403, 404, 409, 422 | **No** | Permanent: the same request will fail the same way. Retrying wastes your rate limit and hides the bug |

## The retry function (be able to write this from memory)

```python
import logging
import random
import time

import requests

log = logging.getLogger(__name__)
RETRYABLE = {429, 500, 502, 503, 504}


def request_with_retry(method, url, max_tries=5, **kwargs):
    kwargs.setdefault("timeout", 10)
    for attempt in range(1, max_tries + 1):
        wait = 2 ** (attempt - 1) + random.uniform(0, 0.5)       # 1, 2, 4, 8 s + jitter
        try:
            r = requests.request(method, url, **kwargs)
        except (requests.ConnectionError, requests.Timeout) as e:
            log.warning("Attempt %d/%d: network error %s", attempt, max_tries, e)
        else:
            if r.status_code not in RETRYABLE:
                r.raise_for_status()           # 4xx (not 429) -> raise immediately, no retry
                return r.json() if r.content else None
            if r.headers.get("Retry-After"):
                wait = float(r.headers["Retry-After"])
            log.warning("Attempt %d/%d: HTTP %d, waiting %.1fs", attempt, max_tries, r.status_code, wait)
        if attempt < max_tries:
            time.sleep(wait)
    raise RuntimeError(f"Gave up after {max_tries} tries: {method} {url}")
```

Line by line:

- `RETRYABLE` lists the temporary statuses.
- `kwargs.setdefault("timeout", 10)`: every call gets a timeout unless the caller sets one.
- `2 ** (attempt - 1)` is exponential backoff; `random.uniform` is jitter.
- `try/except` catches network problems (also temporary).
- `else:` runs only if no exception happened.
- Non-retryable status: `raise_for_status()` raises for 4xx, returns the data for 2xx.
- `Retry-After` overrides our own wait.
- After the last try, raise a clear error so the run logs it and alerts.

## Timeouts

`timeout=10` means "give up if the server doesn't answer within 10 seconds". Without it, one stuck
server can freeze your scheduled job forever, and nobody notices until leads stop arriving.

## Interview phrasing

> "Every API call goes through one retry function: exponential backoff with jitter, respects
> Retry-After, retries 429 and 5xx and network errors, never retries other 4xx because they're
> permanent, and gives up after five tries with a logged error and an alert. Batching keeps the call
> count low in the first place."

## Check yourself

1. Why add jitter?
2. Write the waits for attempts 1–5 with `2 ** (attempt - 1)`.
3. Why is retrying a 400 harmful?

Next: [03-pagination-batching-idempotency.md](03-pagination-batching-idempotency.md)
