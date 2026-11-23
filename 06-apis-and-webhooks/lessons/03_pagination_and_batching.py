"""
API lesson 3: pagination, batching, and proving idempotency
===========================================================

Practice API must be running:  python 06-apis-and-webhooks/practice_server.py
Run me:                         python 06-apis-and-webhooks/lessons/03_pagination_and_batching.py
"""
import logging
import random
import time

import requests

BASE = "http://localhost:5050"
HEADERS = {"Authorization": "Bearer practice-key"}
logging.basicConfig(level=logging.WARNING, format="%(levelname)s %(message)s")
log = logging.getLogger("lesson3")
RETRYABLE = {429, 500, 502, 503, 504}


def request_with_retry(method, url, max_tries=5, **kwargs):
    kwargs.setdefault("timeout", 10)
    for attempt in range(1, max_tries + 1):
        wait = 0.5 * 2 ** (attempt - 1) + random.uniform(0, 0.25)
        try:
            r = requests.request(method, url, **kwargs)
        except (requests.ConnectionError, requests.Timeout):
            pass
        else:
            if r.status_code not in RETRYABLE:
                r.raise_for_status()
                return r.json() if r.content else None
            wait = float(r.headers.get("Retry-After", wait))
            log.warning("HTTP %d, retrying in %.1fs", r.status_code, wait)
        if attempt < max_tries:
            time.sleep(wait)
    raise RuntimeError(f"Gave up: {method} {url}")


requests.post(f"{BASE}/admin/reset", timeout=10)          # start from known data

print("=== 1. The pagination BUG: only reading the first page ===")
first = request_with_retry("GET", f"{BASE}/companies", headers=HEADERS)
print("companies from one call:", len(first["results"]), "(but there are more!)")
print("total on the server:", request_with_retry("GET", f"{BASE}/companies/count", headers=HEADERS)["total"])

print("\n=== 2. The fix: follow the cursor until there's no next page ===")


def get_all_companies():
    results, params, pages = [], {"limit": 5}, 0
    while True:
        data = request_with_retry("GET", f"{BASE}/companies", params=params, headers=HEADERS)
        results.extend(data.get("results", []))
        pages += 1
        after = data.get("paging", {}).get("next", {}).get("after")
        if not after:
            break
        params["after"] = after
    print(f"  fetched {len(results)} companies in {pages} pages")
    return results


crm = get_all_companies()
by_domain = {c["properties"]["domain"]: c for c in crm}      # lookup table for later

print("\n=== 3. Batching: the API allows max 10 records per call ===")
records = [{"id": f"batchco{i}.io", "properties": {"name": f"BatchCo {i}", "employees": 20 + i}}
           for i in range(1, 24)]                              # 23 new companies
try:
    request_with_retry("POST", f"{BASE}/companies/batch/upsert", json={"inputs": records}, headers=HEADERS)
except requests.HTTPError as e:
    print("sending all 23 at once ->", e.response.status_code, e.response.json()["message"])


def upsert_in_batches(records, size=10):
    totals = {"created": 0, "updated": 0}
    for start in range(0, len(records), size):
        batch = records[start:start + size]
        result = request_with_retry("POST", f"{BASE}/companies/batch/upsert",
                                    json={"inputs": batch}, headers=HEADERS)
        totals["created"] += result["created"]
        totals["updated"] += result["updated"]
        print(f"  batch {start // size + 1}: {len(batch)} records -> created {result['created']}, "
              f"updated {result['updated']}")
    return totals


print("first run:", upsert_in_batches(records))

print("\n=== 4. IDEMPOTENCY: run the exact same upsert again ===")
print("second run:", upsert_in_batches(records))
print("count:", request_with_retry("GET", f"{BASE}/companies/count", headers=HEADERS))
print("-> created 0 on the second run. Re-running is safe.")

print("\n=== 5. Compare: the plain CREATE endpoint makes duplicates ===")
for _ in range(2):
    request_with_retry("POST", f"{BASE}/companies",
                       json={"properties": {"name": "Dupe GmbH", "domain": "dupe.de"}}, headers=HEADERS)
    time.sleep(0.2)
print("count after creating dupe.de twice:", request_with_retry("GET", f"{BASE}/companies/count", headers=HEADERS))
print("-> total is now higher than unique_domains: duplicates. This is the classic bug report.")

print("\n=== 6. Never overwrite with blanks ===")
request_with_retry("POST", f"{BASE}/companies/batch/upsert",
                   json={"inputs": [{"id": "peopleco.de", "properties": {"employees": "", "owner": None}}]},
                   headers=HEADERS)
after = {c["properties"]["domain"]: c for c in get_all_companies()}["peopleco.de"]["properties"]
print("peopleco.de after sending blanks:", after["employees"], after["owner"])
print("-> blanks were ignored, real values kept. (Real CRMs may NOT do this for you: strip blanks yourself.)")

requests.post(f"{BASE}/admin/reset", timeout=10)

# ---------------------------------------------------------------------------
# TRY IT
# 1. Change the batch size to 7. How many calls for 23 records?
# 2. Write a function that strips None/"" values from a dict before sending.
# 3. Count how many pages you'd need for 2,300 records at 100 per page.
# ---------------------------------------------------------------------------
