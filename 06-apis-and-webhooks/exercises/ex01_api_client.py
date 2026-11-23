"""
API exercise: write a reliable API client
=========================================

Start the practice API first:  python 06-apis-and-webhooks/practice_server.py
Fill in the functions, then:   python 06-apis-and-webhooks/exercises/ex01_api_client.py

Write these WITHOUT copying from the lessons. This is exactly what live coding asks for.
"""
import random
import time

import requests

BASE = "http://localhost:5050"
HEADERS = {"Authorization": "Bearer practice-key"}
RETRYABLE = {429, 500, 502, 503, 504}


def request_with_retry(method, url, max_tries=5, base_wait=0.3, **kwargs):
    """Make an HTTP request and return the parsed JSON (or None if the body is empty).

    - default timeout of 10 seconds unless the caller passes one
    - retry 429, 500, 502, 503, 504 and connection errors/timeouts
    - wait base_wait * 2 ** (attempt - 1) plus a little random jitter; use Retry-After if present
    - any other 4xx: raise requests.HTTPError immediately (no retry)
    - after max_tries failures: raise RuntimeError
    """
    raise NotImplementedError


def enrich(domain):
    """GET /enrich?domain=... -> dict, or None if the API says 404. Other errors propagate."""
    raise NotImplementedError


def get_all_companies():
    """Return every company from GET /companies by following paging.next.after (limit=5)."""
    raise NotImplementedError


def clean_properties(props):
    """Return a copy of props without keys whose value is None or "" (never write blanks)."""
    raise NotImplementedError


def upsert_in_batches(records, batch_size=10):
    """POST records to /companies/batch/upsert in batches of batch_size.
    Each record looks like {"id": "<domain>", "properties": {...}}; clean its properties first.
    Return {"created": total_created, "updated": total_updated}."""
    raise NotImplementedError


# --------------------------------------------------------------------------- checks
def _checks():
    failures = []

    def check(label, got, expected):
        if got != expected:
            failures.append(f"{label}: expected {expected!r}, got {got!r}")

    try:
        requests.post(f"{BASE}/admin/reset", timeout=5)
    except requests.ConnectionError:
        return ["The practice API isn't running. Start it: python 06-apis-and-webhooks/practice_server.py"]

    check("enrich known", (enrich("peopleco.de") or {}).get("employees"), 120)
    check("enrich unknown -> None", enrich("unknown-company.io"), None)
    try:
        request_with_retry("GET", f"{BASE}/companies", headers={"Authorization": "Bearer wrong"})
        failures.append("401 should raise requests.HTTPError")
    except requests.HTTPError:
        pass
    try:
        request_with_retry("GET", f"{BASE}/status/503", headers=HEADERS, max_tries=2, base_wait=0.05)
        failures.append("an endpoint that always returns 503 should end in RuntimeError")
    except RuntimeError:
        pass
    statuses_ok = 0
    for _ in range(12):                       # fast enough to hit 429s: must still all succeed
        request_with_retry("GET", f"{BASE}/companies", params={"limit": 1}, headers=HEADERS)
        statuses_ok += 1
    check("12 quick calls all succeed", statuses_ok, 12)
    total = request_with_retry("GET", f"{BASE}/companies/count", headers=HEADERS)["total"]
    check("get_all_companies count", len(get_all_companies()), total)
    check("clean_properties", clean_properties({"a": 1, "b": "", "c": None, "d": 0}), {"a": 1, "d": 0})
    records = [{"id": f"exco{i}.io", "properties": {"name": f"ExCo {i}", "owner": None}} for i in range(23)]
    check("first upsert", upsert_in_batches(records), {"created": 23, "updated": 0})
    check("second upsert (idempotent)", upsert_in_batches(records), {"created": 0, "updated": 23})
    requests.post(f"{BASE}/admin/reset", timeout=5)
    return failures


if __name__ == "__main__":
    try:
        problems = _checks()
    except NotImplementedError:
        print("Some functions still raise NotImplementedError. Fill them in and run again.")
    else:
        print("\n".join(problems) if problems else "All checks passed")
