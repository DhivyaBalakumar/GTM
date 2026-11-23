"""Reference solutions for core_patterns_drill.py. Compare AFTER you've written your own."""
import logging
import time

from core_patterns_drill import PermanentError, TemporaryError, _checks  # noqa: F401

log = logging.getLogger("solutions")


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


def call_with_retry(fn, max_tries=5, base_wait=0.01):
    for attempt in range(1, max_tries + 1):
        try:
            return fn()
        except TemporaryError:
            if attempt == max_tries:
                break
            time.sleep(base_wait * 2 ** (attempt - 1))
    raise RuntimeError(f"Gave up after {max_tries} tries")


def get_all(fetch_page):
    results, after = [], None
    while True:
        data = fetch_page(after)
        results.extend(data.get("results", []))
        after = data.get("paging", {}).get("next", {}).get("after")
        if not after:
            return results


def send_in_batches(records, send, size=100):
    totals = {"created": 0, "updated": 0}
    for i in range(0, len(records), size):
        result = send(records[i:i + size])
        totals["created"] += result["created"]
        totals["updated"] += result["updated"]
    return totals


def process_all(records, process):
    ok, failed = [], []
    for record in records:
        try:
            ok.append(process(record))
        except Exception as e:
            failed.append(record.get("domain"))
            log.warning("Failed on %s: %s", record.get("domain"), e)
    return ok, failed


if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.WARNING, format="%(levelname)s %(message)s")
    _checks(sys.modules[__name__])
