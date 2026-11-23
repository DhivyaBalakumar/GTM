"""Solution to the API exercise."""
import random
import time

import requests

BASE = "http://localhost:5050"
HEADERS = {"Authorization": "Bearer practice-key"}
RETRYABLE = {429, 500, 502, 503, 504}


def request_with_retry(method, url, max_tries=5, base_wait=0.3, **kwargs):
    kwargs.setdefault("timeout", 10)
    for attempt in range(1, max_tries + 1):
        wait = base_wait * 2 ** (attempt - 1) + random.uniform(0, 0.1)
        try:
            r = requests.request(method, url, **kwargs)
        except (requests.ConnectionError, requests.Timeout):
            pass
        else:
            if r.status_code not in RETRYABLE:
                r.raise_for_status()
                return r.json() if r.content else None
            if r.headers.get("Retry-After"):
                wait = float(r.headers["Retry-After"])
        if attempt < max_tries:
            time.sleep(wait)
    raise RuntimeError(f"Gave up after {max_tries} tries: {method} {url}")


def enrich(domain):
    try:
        return request_with_retry("GET", f"{BASE}/enrich", params={"domain": domain}, headers=HEADERS)
    except requests.HTTPError as e:
        if e.response is not None and e.response.status_code == 404:
            return None
        raise


def get_all_companies():
    results, params = [], {"limit": 5}
    while True:
        data = request_with_retry("GET", f"{BASE}/companies", params=params, headers=HEADERS)
        results.extend(data.get("results", []))
        after = data.get("paging", {}).get("next", {}).get("after")
        if not after:
            return results
        params["after"] = after


def clean_properties(props):
    return {k: v for k, v in props.items() if v is not None and v != ""}


def upsert_in_batches(records, batch_size=10):
    totals = {"created": 0, "updated": 0}
    cleaned = [{"id": r["id"], "properties": clean_properties(r.get("properties", {}))} for r in records]
    for start in range(0, len(cleaned), batch_size):
        result = request_with_retry("POST", f"{BASE}/companies/batch/upsert",
                                    json={"inputs": cleaned[start:start + batch_size]}, headers=HEADERS)
        totals["created"] += result["created"]
        totals["updated"] += result["updated"]
    return totals


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
    for _ in range(12):
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
    problems = _checks()
    print("\n".join(problems) if problems else "All checks passed")
