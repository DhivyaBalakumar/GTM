"""Solutions to the 12 live-coding practice problems, with the explanation you'd say out loud."""
import time
from itertools import cycle

from fakes import BadRequest, FakeCRM, FakeFlakyAPI, FakePagedAPI, RateLimited  # noqa: F401


# P1 "Lowercase and trim, take the part after @ for emails, strip the protocol and www, drop the path."
def normalize_domain(value):
    if not value:
        return ""
    v = str(value).strip().lower()
    if "@" in v:
        v = v.split("@")[-1]
    for prefix in ("https://", "http://", "www."):
        if v.startswith(prefix):
            v = v[len(prefix):]
    return v.split("/")[0]


# P2 "One pass with a dict keyed by domain; replace the kept row only if the new one is more complete."
def dedupe(rows):
    best = {}
    for r in rows:
        key = normalize_domain(r.get("website") or r.get("email"))
        if not key:
            continue
        filled = sum(1 for v in r.values() if v not in (None, ""))
        if key not in best or filled > best[key][0]:
            best[key] = (filled, r)
    return [r for _, r in best.values()]


# P3 Cause: it always creates. Fix: upsert by the unique key (find, then update or create).
#    "In HubSpot I'd use the batch upsert endpoint on a unique domain property instead of search-then-
#    create, because the search index can lag. I'd add a test that runs the sync twice."
def sync_companies(crm, companies):
    for c in companies:
        existing = crm.find_by_domain(c["domain"])
        if existing:
            crm.update(existing, c)
        else:
            crm.create(c)


# P4 Cause: it only reads the first page. Fix: follow paging.next.after until there's none.
def fetch_all_contacts(api):
    results, after = [], None
    while True:
        data = api.list_contacts(after=after)
        results.extend(data.get("results", []))
        after = data.get("paging", {}).get("next", {}).get("after")
        if not after:
            return results


# P5 "Retry only the temporary error, back off exponentially, never retry a permanent error, and give up."
def enrich_with_retry(api, domain, max_tries=5):
    for attempt in range(max_tries):
        try:
            return api.enrich(domain)
        except RateLimited as e:
            if attempt == max_tries - 1:
                break
            time.sleep(e.retry_after * 2 ** attempt)
    raise RuntimeError(f"Gave up enriching {domain} after {max_tries} tries")


# P6 "Use .get with defaults at every level; convert numbers inside try/except."
def parse_companies(data):
    out = []
    for item in data.get("results", []):
        p = item.get("properties") or {}
        try:
            employees = int(p.get("numberofemployees") or 0)
        except ValueError:
            employees = 0
        out.append({"name": p.get("name") or "", "domain": p.get("domain") or "", "employees": employees})
    return out


# P7 "try/except per record, count and log failures, never mutate the caller's data."
def enrich_rows(rows, enrich):
    new_rows, failed = [], 0
    for row in rows:
        new = dict(row)
        try:
            new.update(enrich(row["domain"]) or {})
        except Exception:
            failed += 1
        new_rows.append(new)
    return new_rows, failed


# P8 Cause: `> 20` should be `>= 20`. "I'd add a boundary test: segment(20) == 'Mid-market'."
def segment(employees):
    if employees >= 500:
        return "Enterprise"
    if employees >= 20:
        return "Mid-market"
    return "Small"


# P9 "The month is the first 7 characters of the ISO date; count with a dict keyed by (source, month)."
def leads_per_source_month(leads):
    counts = {}
    for lead in leads:
        key = (lead["source"], lead["created_at"][:7])
        counts[key] = counts.get(key, 0) + 1
    return counts
# pandas: df.groupby(["source", df["created_at"].str[:7]]).size()


# P10 "Rules in priority order; round-robin with cycle; always a fallback so nothing is unassigned."
GERMAN_TEAM = ["lena", "jonas"]
GENERAL_TEAM = ["maria", "tom", "sara"]


def make_router():
    german, general = cycle(GERMAN_TEAM), cycle(GENERAL_TEAM)

    def route(lead, owners_by_domain):
        domain = normalize_domain(lead.get("email"))
        if domain in owners_by_domain:
            return owners_by_domain[domain], "existing owner"
        if lead.get("country") in {"DE", "AT", "CH"}:
            return next(german), "DACH round-robin"
        if lead.get("country"):
            return next(general), "general round-robin"
        return "head_of_sales", "fallback"

    return route


# P11 "Events can arrive twice; a stable key in a set (a DB table in production) makes handling idempotent."
def process_events(events, processed, handle):
    handled = 0
    for e in events:
        key = (e.get("eventId"), e.get("subscriptionId"), e.get("occurredAt"))
        if key in processed:
            continue
        processed.add(key)
        handle(e)
        handled += 1
    return handled


# P12
SQL_DUPLICATE_DOMAINS = """
SELECT LOWER(domain) AS domain, COUNT(*) AS copies
FROM accounts GROUP BY LOWER(domain) HAVING COUNT(*) > 1
"""
SQL_ACCOUNTS_WITHOUT_CONTACTS = """
SELECT a.name FROM accounts a LEFT JOIN contacts c ON c.account_id = a.id
WHERE c.id IS NULL ORDER BY a.name
"""
SQL_MEETING_RATE_BY_SOURCE = """
SELECT source, COUNT(*) AS leads, ROUND(100.0 * SUM(meeting_booked) / COUNT(*), 1) AS meeting_pct
FROM leads GROUP BY source ORDER BY meeting_pct DESC
"""


if __name__ == "__main__":
    import sys
    from checks import run
    run(sys.modules[__name__])
