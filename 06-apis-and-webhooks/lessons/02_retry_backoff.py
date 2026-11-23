"""
API lesson 2: rate limits, outages and a proper retry function
==============================================================

Practice API must be running:  python 06-apis-and-webhooks/practice_server.py
Run me:                         python 06-apis-and-webhooks/lessons/02_retry_backoff.py
"""
import logging
import random
import time

import requests

BASE = "http://localhost:5050"
HEADERS = {"Authorization": "Bearer practice-key"}
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)-7s %(message)s", datefmt="%H:%M:%S")
log = logging.getLogger("retry")

print("=== 1. The naive way: fire 15 requests as fast as possible ===")
statuses = []
for _ in range(15):
    r = requests.get(f"{BASE}/companies", params={"limit": 1}, headers=HEADERS, timeout=10)
    statuses.append(r.status_code)
print("statuses:", statuses)
print("429s:", statuses.count(429), "| 503s:", statuses.count(503))
print("A naive pipeline would crash or silently lose these. Let's fix it.")
time.sleep(1.5)

print("\n=== 2. The retry function ===")
RETRYABLE = {429, 500, 502, 503, 504}


def request_with_retry(method, url, max_tries=5, base_wait=0.5, **kwargs):
    """Call an API, retrying temporary failures with exponential backoff + jitter.

    - Retries: 429, 5xx, connection errors, timeouts
    - Never retries other 4xx (400, 401, 403, 404...): they're permanent
    - Respects Retry-After
    - Gives up after max_tries with a clear error
    """
    kwargs.setdefault("timeout", 10)
    for attempt in range(1, max_tries + 1):
        wait = base_wait * 2 ** (attempt - 1) + random.uniform(0, 0.25)
        try:
            r = requests.request(method, url, **kwargs)
        except (requests.ConnectionError, requests.Timeout) as e:
            log.warning("attempt %d/%d: network error (%s)", attempt, max_tries, type(e).__name__)
        else:
            if r.status_code not in RETRYABLE:
                r.raise_for_status()
                return r.json() if r.content else None
            if r.headers.get("Retry-After"):
                wait = float(r.headers["Retry-After"])
            log.warning("attempt %d/%d: HTTP %d, waiting %.2fs", attempt, max_tries, r.status_code, wait)
        if attempt < max_tries:
            time.sleep(wait)
    raise RuntimeError(f"Gave up after {max_tries} tries: {method} {url}")


print("\n=== 3. The same 15 requests through the retry function ===")
ok = 0
for i in range(15):
    request_with_retry("GET", f"{BASE}/companies", params={"limit": 1}, headers=HEADERS)
    ok += 1
print(f"{ok}/15 succeeded (slower, but nothing lost)")

print("\n=== 4. A permanent error is NOT retried ===")
try:
    request_with_retry("GET", f"{BASE}/companies", headers={"Authorization": "Bearer wrong"})
except requests.HTTPError as e:
    print("raised immediately:", e)

print("\n=== 5. A 404 from enrichment: handle it as 'no data' ===")


def enrich(domain):
    try:
        return request_with_retry("GET", f"{BASE}/enrich", params={"domain": domain}, headers=HEADERS)
    except requests.HTTPError as e:
        if e.response is not None and e.response.status_code == 404:
            return None                     # normal: the provider doesn't know this company
        raise                               # anything else is a real problem


for d in ["peopleco.de", "unknown.io"]:
    print(d, "->", enrich(d))

print("\n=== 6. Giving up: an endpoint that ALWAYS fails ===")
try:
    request_with_retry("GET", f"{BASE}/status/503", headers=HEADERS, max_tries=3, base_wait=0.2)
except RuntimeError as e:
    print("RuntimeError:", e)
    print("In a pipeline: log it, count it as failed, alert someone, carry on with other records.")

print("\n=== 7. Preventing 429s: pace yourself (throttling) ===")
start = time.perf_counter()
for _ in range(5):
    request_with_retry("GET", f"{BASE}/companies", params={"limit": 1}, headers=HEADERS)
    time.sleep(0.25)                        # max ~4 per second, under the limit of 5
print(f"5 paced calls in {time.perf_counter() - start:.1f}s with few or no 429s")

# ---------------------------------------------------------------------------
# TRY IT
# 1. Restart the server with  $env:PRACTICE_FAIL_RATE="0.4"  (PowerShell) and re-run.
# 2. Change max_tries to 1. How many of the 15 fail now?
# 3. Add a counter for how many retries happened in total, and log it at the end.
# ---------------------------------------------------------------------------
