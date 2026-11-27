"""
The whole GTM data pipeline in one file, step by step
=====================================================

Run me (from the repo root):

    python 16-end-to-end-pipeline/code/pipeline_end_to_end.py            # full run, prints every step
    python 16-end-to-end-pipeline/code/pipeline_end_to_end.py --twice    # run twice: proves idempotency

Standard library only. No API keys, nothing is sent anywhere. Every "API" here is a local fake that
behaves like the real one (pages, cursors, 429 rate limits, credits), so the code you read is the code
you would write against Apollo, Clay, an enrichment provider and HubSpot. Swap the fake for a real
`requests` call and the rest stays the same.

Read alongside 16-end-to-end-pipeline/README.md. Each STEP below matches one chapter:

    STEP 1  Collect        chapter 01 + 02   (sources, pagination, rate limits, retries)
    STEP 2  Map + clean    chapter 03        (one schema, normalise, validate, quarantine)
    STEP 3  Dedupe         chapter 04        (keys, fuzzy match, clusters, survivorship)
    STEP 4  Enrich         chapter 05        (waterfall, cache, credit budget, email checks)
    STEP 5  Suppress       chapter 06        (customers, open deals, competitors, unsubscribes)
    STEP 6  Score          chapter 07        (fit + intent, reasons, tiers)
    STEP 7  Segment        chapter 07        (industry x size x persona -> sequence)
    STEP 8  Route          chapter 06        (keep existing owner, else territory round robin)
    STEP 9  CRM write-back chapter 08        (batch upsert by unique key, field ownership)
    STEP 10 Outreach       chapter 09        (draft-only sequence enrolments)
    STEP 11 Report         chapter 11 + 12   (counts, fill rates, credits, quality checks)

The 6 core patterns (HOW_TO_LEARN_THE_CODE.md) all run here; chapter 15 maps each one:
    1 normalise    -> normalise_domain, normalise_country, parse_employees, classify_title
    2 dedupe       -> dedupe, survivorship
    3 retry        -> call_with_retry
    4 pagination   -> fetch_all_pages_page_number, fetch_all_pages_cursor
    5 batching     -> batches, write_back
    6 per-record error handling -> process_all (used by the map and enrich steps)
"""
from __future__ import annotations

import argparse
import csv
import json
import random
import re
import time
from collections import Counter, defaultdict
from difflib import SequenceMatcher
from itertools import cycle
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DATA = REPO / "data"
OUT = Path(__file__).resolve().parent / "output"

# --------------------------------------------------------------------------------------------- #
# CONFIG: every business rule lives here, so changing the ICP never means changing code.
# --------------------------------------------------------------------------------------------- #
CONFIG = {
    "icp": {
        "countries": {"DE", "AT", "CH", "NL", "BE", "LU", "FR", "ES", "NO", "UK"},
        "core_countries": {"DE", "AT", "CH"},                       # DACH = best fit
        "industries": {"software", "fintech", "healthtech", "insurtech", "hr tech", "saas"},
        "employees_min": 20, "employees_max": 500,
        "buyer_functions": {"engineering", "security", "it", "executive"},
    },
    "weights": {"country": 15, "core_country_bonus": 5, "industry": 20, "size": 15,
                "persona": 10, "senior": 5, "signal_funding": 20, "signal_hiring": 15,
                "signal_inbound": 15},
    "tiers": [(80, "A"), (60, "B"), (40, "C"), (0, "D")],
    "territories": {"DACH": {"DE", "AT", "CH"}, "BENELUX": {"NL", "BE", "LU"},
                    "REST_EU": {"FR", "ES", "NO", "UK"}},
    "reps": {"DACH": ["lena", "jonas"], "BENELUX": ["tom"], "REST_EU": ["maria"]},
    "source_priority": ["crm", "apollo", "clay", "webinar", "website"],   # survivorship order
    "competitor_domains": {"vanta.com", "drata.com"},
    "unsubscribed_emails": {"paul.lang@mosaichr.de"},
    "personal_domains": {"gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "gmx.de", "web.de"},
    "role_prefixes": {"info", "sales", "hello", "contact", "admin", "support", "office"},
    "credit_budget": 40,
    "crm_batch_size": 5,           # HubSpot allows 100; small here so you can see the batching
    "apollo_per_page": 3,          # Apollo allows up to 100; small here so you can see pagination
    "fuzzy_auto_merge": 0.90, "fuzzy_review": 0.75,
}

COUNTRY_ALIASES = {"germany": "DE", "deutschland": "DE", "austria": "AT", "österreich": "AT",
                   "switzerland": "CH", "netherlands": "NL", "the netherlands": "NL", "holland": "NL",
                   "belgium": "BE", "luxembourg": "LU", "france": "FR", "spain": "ES",
                   "norway": "NO", "united kingdom": "UK", "gb": "UK", "great britain": "UK",
                   "united states": "US", "usa": "US"}
INDUSTRY_ALIASES = {"health tech": "healthtech", "computer_software": "software",
                    "financial_services": "fintech"}
LEGAL_SUFFIXES = {"gmbh", "ag", "bv", "b.v.", "ltd", "inc", "sa", "se", "llc"}


def log(msg=""):
    print(msg)


# =============================================================================================== #
# STEP 1: COLLECT  (chapters 01 + 02)
# =============================================================================================== #
class RateLimited(Exception):
    """What a 429 Too Many Requests looks like once your client raises it."""

    def __init__(self, retry_after):
        super().__init__(f"429, retry after {retry_after}s")
        self.retry_after = retry_after


def call_with_retry(fn, *, max_attempts=5, base_delay=0.5, sleep=time.sleep, stats=None):
    """Retry on 429 / 5xx with exponential backoff + jitter, honouring Retry-After.

    Real version: catch requests' HTTPError, check resp.status_code in {429, 500, 502, 503, 504},
    read resp.headers.get("Retry-After"). Never retry 400/401/403/404: those won't fix themselves.
    """
    for attempt in range(1, max_attempts + 1):
        try:
            return fn()
        except RateLimited as e:
            if attempt == max_attempts:
                raise
            delay = e.retry_after or base_delay * (2 ** (attempt - 1))
            delay += random.uniform(0, delay * 0.1)                # jitter: don't retry in lockstep
            if stats is not None:
                stats["retries"] += 1
            sleep(delay)


class FakeApolloPeopleSearch:
    """Behaves like POST /api/v1/mixed_people/api_search: page-number pagination
    (page, per_page <= 100, max 500 pages), nested organization object, the occasional 429.
    Search returns no emails (in real Apollo you get those from people/bulk_match)."""

    def __init__(self, rows, fail_every=2):
        self.rows, self.calls, self.fail_every = rows, 0, fail_every

    def search(self, page, per_page):
        self.calls += 1
        if self.fail_every and self.calls % self.fail_every == 0:
            raise RateLimited(retry_after=0.01)
        start = (page - 1) * per_page
        chunk = self.rows[start:start + per_page]
        people = [{
            "id": f"ap_{start + i}",
            "first_name": r["contact_name"].split(" ")[0] if r["contact_name"] else None,
            "last_name": " ".join(r["contact_name"].split(" ")[1:]) or None,
            "title": r["title"] or None,
            "email": r["contact_email"],          # pretend we already ran bulk_match for brevity
            "city": r["city"], "country": r["country"],
            "organization": {"name": r["company"], "website_url": r["website"],
                             "estimated_num_employees": r["employees"] or None,
                             "industry": r["industry"]},
        } for i, r in enumerate(chunk)]
        total_pages = max(1, -(-len(self.rows) // per_page))
        return {"people": people, "pagination": {"page": page, "per_page": per_page,
                                                 "total_entries": len(self.rows),
                                                 "total_pages": total_pages}}


class FakeHubSpotCompanies:
    """Behaves like GET /crm/v3/objects/companies: cursor pagination via paging.next.after."""

    def __init__(self, rows, limit=4):
        self.rows, self.limit = rows, limit

    def list(self, after=None):
        start = int(after or 0)
        chunk = self.rows[start:start + self.limit]
        body = {"results": [{"id": r["id"], "properties": {
            "name": r["name"], "domain": r["domain"], "country": r["country"],
            "industry": r["industry"], "numberofemployees": r["employees"],
            "hubspot_owner_id": r["owner"] or None}} for r in chunk]}
        if start + self.limit < len(self.rows):
            body["paging"] = {"next": {"after": str(start + self.limit)}}
        return body


def fetch_all_pages_page_number(api, per_page, stats):
    """Page-number pagination: keep asking for page+1 until page == total_pages."""
    page = 1
    while True:
        body = call_with_retry(lambda: api.search(page, per_page), sleep=lambda s: None, stats=stats)
        stats["apollo_pages"] += 1
        yield from body["people"]
        if page >= body["pagination"]["total_pages"]:
            break
        page += 1


def fetch_all_pages_cursor(api, stats):
    """Cursor pagination: follow paging.next.after until it disappears."""
    after = None
    while True:
        body = api.list(after)
        stats["crm_pages"] += 1
        yield from body["results"]
        after = body.get("paging", {}).get("next", {}).get("after")
        if not after:
            break


def read_csv(path):
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def collect():
    stats = Counter()
    leads = read_csv(DATA / "leads_raw.csv")
    apollo_rows = [r for r in leads if r["source"] == "apollo"]
    file_rows = [r for r in leads if r["source"] != "apollo"]     # Clay export, webinar, web forms

    apollo = list(fetch_all_pages_page_number(FakeApolloPeopleSearch(apollo_rows),
                                              CONFIG["apollo_per_page"], stats))
    crm = list(fetch_all_pages_cursor(FakeHubSpotCompanies(read_csv(DATA / "crm_accounts.csv")), stats))
    raw = {"apollo_api": apollo, "files": file_rows, "crm_companies": crm,
           "crm_deals": read_csv(DATA / "crm_deals.csv")}
    return raw, stats


# =============================================================================================== #
# STEP 2: MAP + CLEAN + VALIDATE  (chapter 03)
# =============================================================================================== #
def map_apollo(p):
    org = p.get("organization") or {}
    return {"source": "apollo", "company": org.get("name"), "website": org.get("website_url"),
            "first_name": p.get("first_name"), "last_name": p.get("last_name"),
            "email": p.get("email"), "title": p.get("title"), "country": p.get("country"),
            "city": p.get("city"), "employees": org.get("estimated_num_employees"),
            "industry": org.get("industry")}


def map_file(r):
    name = (r.get("contact_name") or "").strip()
    first, _, last = name.partition(" ")
    return {"source": r["source"], "company": r["company"], "website": r["website"],
            "first_name": first or None, "last_name": last or None, "email": r["contact_email"],
            "title": r["title"], "country": r["country"], "city": r["city"],
            "employees": r["employees"], "industry": r["industry"]}


def blank(v):
    return v is None or (isinstance(v, str) and not v.strip())


def normalise_domain(value):
    if blank(value):
        return None
    v = value.strip().lower()
    if "@" in v:
        v = v.split("@")[-1]
    v = re.sub(r"^https?://", "", v)
    v = re.sub(r"^www\.", "", v)
    return v.split("/")[0].split("?")[0] or None


def normalise_country(value):
    if blank(value):
        return None
    v = value.strip()
    return COUNTRY_ALIASES.get(v.lower(), v.upper() if len(v) == 2 else None)


def parse_employees(value):
    """'120' -> 120, '51-200' -> 125 (midpoint), 'abc' / '' -> None."""
    if blank(value):
        return None
    s = str(value).replace(",", "").strip()
    if re.fullmatch(r"\d+", s):
        return int(s)
    m = re.fullmatch(r"(\d+)\s*-\s*(\d+)", s)
    if m:
        lo, hi = int(m.group(1)), int(m.group(2))
        return (lo + hi) // 2
    return None


def clean_person_name(value):
    if blank(value):
        return None
    v = re.sub(r"^(dr|prof|mr|mrs|ms)\.?\s+", "", value.strip(), flags=re.I)
    return v[:1].upper() + v[1:]


EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+'-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")


def classify_title(title):
    """Title -> (seniority, function). Order matters: check 'intern'/'student' FIRST so
    'Software Engineer Intern' isn't read as an engineer."""
    t = (title or "").lower()
    if not t:
        return None, None
    if any(w in t for w in ("intern", "student", "trainee", "working student")):
        seniority = "junior"
    elif re.search(r"\b(ceo|cto|coo|cfo|ciso|cio|chief|founder|owner)\b", t) and "product owner" not in t:
        seniority = "c_level"
    elif re.search(r"\b(vp|vice president|head of|director)\b", t):
        seniority = "vp_head"
    elif "manager" in t or "lead" in t:
        seniority = "manager"
    else:
        seniority = "ic"
    if re.search(r"\b(ciso|security)\b", t):
        function = "security"
    elif re.search(r"\b(cto|engineering|engineer|developer|chief technology)\b", t):
        function = "engineering"
    elif re.search(r"\b(it|cio)\b", t):
        function = "it"
    elif re.search(r"\b(ceo|coo|founder|chief executive|chief operating)\b", t) or \
            (re.search(r"\bowner\b", t) and "product owner" not in t):     # "Product Owner" is not an exec
        function = "executive"
    elif re.search(r"\b(cfo|finance)\b", t):
        function = "finance"
    elif "sales" in t:
        function = "sales"
    else:
        function = "other"
    return seniority, function


def clean_and_validate(records):
    cleaned, quarantine = [], []
    for r in records:
        c = dict(r)
        c["email"] = (r["email"] or "").strip().lower() or None
        c["email_domain"] = c["email"].split("@")[-1] if c["email"] and "@" in c["email"] else None
        c["domain"] = normalise_domain(r["website"])
        c["company"] = (r["company"] or "").strip() or None
        c["country"] = normalise_country(r["country"])
        c["employees"] = parse_employees(r["employees"])
        ind = (r["industry"] or "").strip().lower() or None
        c["industry"] = INDUSTRY_ALIASES.get(ind, ind)
        c["first_name"] = clean_person_name(r["first_name"])
        c["last_name"] = (r["last_name"] or "").strip() or None
        c["title"] = (r["title"] or "").strip() or None
        c["seniority"], c["function"] = classify_title(c["title"])
        c["is_personal_email"] = c["email_domain"] in CONFIG["personal_domains"]
        c["is_role_email"] = bool(c["email"]) and c["email"].split("@")[0] in CONFIG["role_prefixes"]

        # No website but a WORK email? The email domain is the company domain.
        if not c["domain"] and c["email_domain"] and not c["is_personal_email"]:
            c["domain"] = c["email_domain"]
            c["domain_from_email"] = True

        problems = []
        if not c["email"] or not EMAIL_RE.match(c["email"]):
            problems.append("invalid_email")
        if c["is_personal_email"] and not c["company"]:
            problems.append("personal_email_no_company")
        if c["seniority"] == "junior" or (c["title"] or "").lower() in {"student", "freelancer"}:
            problems.append("not_a_buyer")
        if problems:
            quarantine.append({**c, "reasons": problems})
        else:
            cleaned.append(c)
    return cleaned, quarantine


# =============================================================================================== #
# STEP 3: DEDUPE  (chapter 04)
# =============================================================================================== #
def name_key(name):
    words = re.sub(r"[^\w\s.]", " ", (name or "").lower()).split()
    return " ".join(w for w in words if w not in LEGAL_SUFFIXES)


def similarity(a, b):
    return SequenceMatcher(None, name_key(a), name_key(b)).ratio()


def completeness(rec, fields):
    return sum(not blank(rec.get(f)) for f in fields)


def survivorship(records, fields):
    """Golden record: for each field, take the value from the highest-priority source that has one;
    tie-break on the more complete record. Keep lineage so you can explain every value."""
    prio = {s: i for i, s in enumerate(CONFIG["source_priority"])}
    ordered = sorted(records, key=lambda r: (prio.get(r["source"], 99), -completeness(r, fields)))
    golden, lineage = {}, {}
    for f in fields:
        for r in ordered:
            if not blank(r.get(f)):
                golden[f], lineage[f] = r[f], r["source"]
                break
        else:
            golden[f] = None
    golden["sources"] = sorted({r["source"] for r in records})
    golden["lineage"] = lineage
    return golden


def dedupe(cleaned, crm_companies):
    # 3a. Contacts: exact key = normalised email.
    by_email = defaultdict(list)
    for r in cleaned:
        by_email[r["email"]].append(r)
    contact_fields = ["email", "first_name", "last_name", "title", "seniority", "function",
                      "country", "city", "domain", "company", "employees", "industry",
                      "is_role_email"]
    contacts = [survivorship(group, contact_fields) for group in by_email.values()]

    # 3b. Accounts: key = domain. Blocking + fuzzy name for records that have no domain.
    crm_by_domain = {}
    for c in crm_companies:
        d = normalise_domain(c["properties"]["domain"])
        crm_by_domain.setdefault(d, []).append(c)             # >1 = duplicate already in the CRM!
    groups, review = defaultdict(list), []
    for c in contacts:
        if c["domain"]:
            groups[c["domain"]].append(c)
    no_domain = [c for c in contacts if not c["domain"] and c["company"]]
    for c in no_domain:                                       # fuzzy within the same country only
        best, best_score = None, 0.0
        for d, members in groups.items():
            if members[0]["country"] != c["country"]:
                continue
            s = similarity(c["company"], members[0]["company"])
            if s > best_score:
                best, best_score = d, s
        if best and best_score >= CONFIG["fuzzy_auto_merge"]:
            c["domain"] = best
            groups[best].append(c)
        elif best and best_score >= CONFIG["fuzzy_review"]:
            review.append((c["company"], groups[best][0]["company"], round(best_score, 2)))

    account_fields = ["domain", "company", "country", "employees", "industry"]
    accounts = {}
    for d, members in groups.items():
        recs = [{**m, "source": m["sources"][0]} for m in members]
        for crm in crm_by_domain.get(d, []):
            p = crm["properties"]
            recs.append({"source": "crm", "domain": d, "company": p["name"],
                         "country": normalise_country(p["country"]),
                         "employees": parse_employees(p["numberofemployees"]),
                         "industry": (p["industry"] or "").lower() or None})
        golden = survivorship(recs, account_fields)
        crm_ids = [x["id"] for x in crm_by_domain.get(d, [])]
        golden["crm_ids"] = crm_ids
        golden["existing_owner"] = next((x["properties"]["hubspot_owner_id"] for x in crm_by_domain.get(d, [])
                                         if x["properties"]["hubspot_owner_id"]), None)
        accounts[d] = golden
    crm_dupes = {d: [x["id"] for x in v] for d, v in crm_by_domain.items() if len(v) > 1}
    return contacts, accounts, review, crm_dupes


# =============================================================================================== #
# STEP 4: ENRICH  (chapter 05)
# =============================================================================================== #
class FakeProvider:
    """One enrichment provider: costs credits only when it returns data (like Apollo/Clay).
    `broken` domains make it raise, like a real API returning a malformed body for one record."""

    def __init__(self, name, data, cost, broken=()):
        self.name, self.data, self.cost, self.broken = name, data, cost, set(broken)

    def lookup(self, domain):
        if domain in self.broken:
            raise ValueError(f"{self.name}: malformed response for {domain}")
        return self.data.get(domain)


PROVIDER_A = FakeProvider("provider_a", {           # cheap, partial coverage
    "peopleco.de": {"employees": 120, "industry": "software"},
    "kranich-logistik.de": {"company": "Kranich Logistik GmbH", "country": "DE"},
    "altamirapay.com": {"employees": 140},
}, cost=1)
PROVIDER_B = FakeProvider("provider_b", {           # expensive, better coverage + signals
    "kranich-logistik.de": {"employees": 180, "industry": "logistics"},
    "corvex.de": {"signals": ["hiring_security"]},
    "peopleco.de": {"signals": ["funding_series_a", "hiring_security"]},
    "opalanalytics.de": {"signals": ["funding_seed"]},
    "vektorcloud.nl": {"signals": ["hiring_security"]},
    "kitelabs.io": {"employees": 9},
}, cost=3, broken={"greenleafretail.com"})
WATERFALL = [PROVIDER_A, PROVIDER_B]
ENRICH_FIELDS = ["company", "country", "employees", "industry"]


def process_all(records, process, label, max_fail_rate=0.10):
    """Core pattern 6: per-record error handling. One bad record must not stop the others,
    but every failure is recorded (which record, why) and a high failure rate raises an alert."""
    ok, failed = [], []
    for key, rec in records:
        try:
            ok.append(process(key, rec))
        except Exception as e:                                  # noqa: BLE001 - we log and continue
            failed.append({"key": key, "error": f"{e.__class__.__name__}: {e}"})
    rate = len(failed) / len(records) if records else 0
    alert = rate > max_fail_rate
    return ok, failed, {"step": label, "ok": len(ok), "failed": len(failed),
                        "fail_rate": round(rate, 3), "alert": alert}


def enrich_one(domain, acc, cache, budget_state, stats):
    """Waterfall for ONE account: cache -> budget check -> provider -> fill only missing fields."""
    acc.setdefault("signals", [])
    missing = [f for f in ENRICH_FIELDS if blank(acc.get(f))]
    for provider in WATERFALL:
        key = (provider.name, domain)
        if key in cache:                                   # never pay twice for the same lookup
            hit = cache[key]
            stats["cache_hits"] += 1
        else:
            if budget_state["used"] + provider.cost > budget_state["budget"]:
                stats["skipped_budget"] += 1
                break
            hit = provider.lookup(domain)                  # may raise -> handled by process_all
            cache[key] = hit                               # cache misses too (None)
            if hit:
                budget_state["used"] += provider.cost      # pay only when data comes back
                stats[f"{provider.name}_hits"] += 1
        if hit:
            for f in list(missing):
                if not blank(hit.get(f)):
                    acc[f] = hit[f]
                    acc["lineage"][f] = provider.name
                    missing.remove(f)
            acc["signals"] = sorted(set(acc["signals"]) | set(hit.get("signals", [])))
        # We keep going to the last provider even when nothing is missing, because it is also
        # our signal source. A pure firmographic waterfall would `break` as soon as missing == [].
    return domain


def enrich(accounts, cache, budget):
    budget_state, stats = {"used": 0, "budget": budget}, Counter()
    _, failed, summary = process_all(
        list(accounts.items()),
        lambda d, acc: enrich_one(d, acc, cache, budget_state, stats), "enrich")
    stats["failed"] = len(failed)
    return budget_state["used"], stats, failed, summary


def guess_email_patterns(first, last, domain):
    """When you have name + domain but no email: generate candidates, then VERIFY before use
    (ZeroBounce / NeverBounce / MillionVerifier). Never send to an unverified guess."""
    f, l = (first or "").lower(), (last or "").lower().replace(" ", "")
    return [f"{f}@{domain}", f"{f}.{l}@{domain}", f"{f[:1]}{l}@{domain}", f"{f[:1]}.{l}@{domain}"]


# =============================================================================================== #
# STEP 5: SUPPRESS  (chapter 06)
# =============================================================================================== #
def suppress(contacts, accounts, crm_deals, crm_companies):
    id_to_domain = {c["id"]: normalise_domain(c["properties"]["domain"]) for c in crm_companies}
    customers, open_deal = set(), set()
    for deal in crm_deals:
        d = id_to_domain.get(deal["account_id"])
        if deal["stage"] == "closed_won":
            customers.add(d)
        elif deal["stage"] != "closed_lost":
            open_deal.add(d)
    keep, suppressed = [], []
    for c in contacts:
        reason = None
        if c["email"] in CONFIG["unsubscribed_emails"]:
            reason = "unsubscribed"
        elif c["domain"] in CONFIG["competitor_domains"]:
            reason = "competitor"
        elif c["domain"] in customers:
            reason = "existing_customer"        # -> expansion motion, not cold outbound
        elif c["domain"] in open_deal:
            reason = "open_deal"                # -> tell the deal owner, don't cold-email
        elif c.get("is_role_email"):
            reason = "role_email"
        (suppressed if reason else keep).append({**c, "suppress_reason": reason} if reason else c)
    return keep, suppressed


# =============================================================================================== #
# STEP 6 + 7: SCORE + SEGMENT  (chapter 07)
# =============================================================================================== #
def tier_for(score):
    return next(t for floor, t in CONFIG["tiers"] if score >= floor)


def score_contact(c, acc):
    icp, w = CONFIG["icp"], CONFIG["weights"]
    fit, intent, reasons = 0, 0, []
    country, emp, ind = acc.get("country"), acc.get("employees"), acc.get("industry")
    if country in icp["countries"]:
        fit += w["country"]
        reasons.append(f"{country} in target region")
        if country in icp["core_countries"]:
            fit += w["core_country_bonus"]
    if ind in icp["industries"]:
        fit += w["industry"]
        reasons.append(f"{ind}")
    if emp and icp["employees_min"] <= emp <= icp["employees_max"]:
        fit += w["size"]
        reasons.append(f"{emp} staff")
    if c.get("function") in icp["buyer_functions"]:
        fit += w["persona"]
        reasons.append(f"{c['function']} buyer")
    if c.get("seniority") in {"c_level", "vp_head"}:
        fit += w["senior"]
    sig = acc.get("signals", [])
    if any(s.startswith("funding") for s in sig):
        intent += w["signal_funding"]
        reasons.append("recent funding")
    if "hiring_security" in sig:
        intent += w["signal_hiring"]
        reasons.append("hiring for security")
    if "webinar" in c.get("sources", []) or "website" in c.get("sources", []):
        intent += w["signal_inbound"]
        reasons.append("engaged inbound")
    score = min(100, fit + intent)
    return {"fit": fit, "intent": intent, "score": score, "tier": tier_for(score), "reasons": reasons}


def segment(c, acc):
    emp = acc.get("employees") or 0
    size = "smb" if emp < 50 else "mid" if emp <= 250 else "upper_mid"
    ind = acc.get("industry") or "other"
    vertical = "fintech" if ind in {"fintech", "insurtech"} else "health" if ind == "healthtech" \
        else "software" if ind in {"software", "saas", "hr tech"} else "other"
    persona = {"security": "security_lead", "engineering": "tech_lead", "it": "tech_lead",
               "executive": "founder_exec"}.get(c.get("function"), "other")
    return {"vertical": vertical, "size_band": size, "persona": persona,
            "segment": f"{vertical}:{size}:{persona}"}


SEQUENCES = {"fintech": "seq_fintech_dora_soc2", "health": "seq_health_iso27001",
             "software": "seq_saas_iso27001_fast", "other": "seq_generic_nurture"}


# =============================================================================================== #
# STEP 8: ROUTE  (chapter 06)
# =============================================================================================== #
def territory_for(country):
    return next((t for t, cs in CONFIG["territories"].items() if country in cs), None)


def route(scored, accounts):
    rr = {t: cycle(reps) for t, reps in CONFIG["reps"].items()}   # round robin per territory
    assigned_per_domain = {}
    for c in scored:
        acc = accounts[c["domain"]]
        if acc.get("existing_owner"):
            c["owner"], c["route_reason"] = acc["existing_owner"], "kept existing CRM owner"
        elif c["domain"] in assigned_per_domain:                  # one owner per account
            c["owner"], c["route_reason"] = assigned_per_domain[c["domain"]], "same account as colleague"
        elif c["tier"] == "D":
            c["owner"], c["route_reason"] = None, "tier D: marketing nurture, no rep"
        else:
            t = territory_for(acc.get("country"))
            c["owner"] = next(rr[t]) if t else None
            c["route_reason"] = f"round robin in {t}" if t else "no territory"
        if c["owner"]:
            assigned_per_domain.setdefault(c["domain"], c["owner"])
    return scored


# =============================================================================================== #
# STEP 9: CRM WRITE-BACK  (chapter 08)
# =============================================================================================== #
class FakeCRM:
    """Behaves like HubSpot batch/upsert with idProperty: same key -> update, new key -> create."""

    def __init__(self):
        self.companies, self.contacts, self.calls = {}, {}, 0

    def batch_upsert(self, object_type, inputs):
        assert len(inputs) <= 100, "HubSpot batch endpoints accept at most 100 inputs"
        self.calls += 1
        store = self.companies if object_type == "companies" else self.contacts
        created = updated = 0
        for item in inputs:
            key = item["id"]
            if key in store:
                updated += 1
                # field ownership: never overwrite a value a human set (owner) with the pipeline's
                for k, v in item["properties"].items():
                    if k == "hubspot_owner_id" and store[key].get(k):
                        continue
                    store[key][k] = v
            else:
                created += 1
                store[key] = dict(item["properties"])
        return {"created": created, "updated": updated}


def batches(items, size):
    for i in range(0, len(items), size):
        yield items[i:i + size]


def to_payloads(scored, accounts):
    """Only send fields the pipeline OWNS, and never send blanks (they'd wipe good data)."""
    companies = []
    for d in sorted({c["domain"] for c in scored}):
        a = accounts[d]
        props = {"domain": d, "name": a.get("company"), "country": a.get("country"),
                 "numberofemployees": a.get("employees"), "industry": a.get("industry"),
                 "gtm_signals": ";".join(a.get("signals", [])) or None}
        companies.append({"idProperty": "domain", "id": d,
                          "properties": {k: v for k, v in props.items() if not blank(v)}})
    contacts = []
    for c in scored:
        props = {"email": c["email"], "firstname": c["first_name"], "lastname": c["last_name"],
                 "jobtitle": c["title"], "gtm_fit_score": c["fit"], "gtm_intent_score": c["intent"],
                 "gtm_score": c["score"], "gtm_tier": c["tier"], "gtm_segment": c["segment"],
                 "gtm_score_reasons": "; ".join(c["reasons"]), "hubspot_owner_id": c["owner"],
                 "company_domain": c["domain"]}            # -> association to the company
        contacts.append({"idProperty": "email", "id": c["email"],
                         "properties": {k: v for k, v in props.items() if not blank(v)}})
    return companies, contacts


def write_back(crm, companies, contacts, dry_run=False):
    totals = Counter()
    for obj, payload in (("companies", companies), ("contacts", contacts)):
        for batch in batches(payload, CONFIG["crm_batch_size"]):
            if dry_run:
                totals[f"{obj}_would_send"] += len(batch)
                continue
            res = call_with_retry(lambda: crm.batch_upsert(obj, batch), sleep=lambda s: None)
            totals[f"{obj}_created"] += res["created"]
            totals[f"{obj}_updated"] += res["updated"]
    return totals


# =============================================================================================== #
# STEP 10: OUTREACH DRAFTS  (chapter 09) - drafts only, nothing is ever sent
# =============================================================================================== #
def draft_first_touch(c, acc):
    hook = ("congrats on the recent raise" if any(s.startswith("funding") for s in acc.get("signals", []))
            else "saw you're hiring for security" if "hiring_security" in acc.get("signals", [])
            else f"noticed {acc.get('company')} is growing in {acc.get('country')}")
    return {"to": c["email"], "owner": c["owner"], "sequence": SEQUENCES[c["vertical"]],
            "subject": f"{acc.get('company')} + ISO 27001",
            "body": f"Hi {c['first_name']}, {hook}. Teams like yours usually get asked for ISO 27001 "
                    f"or SOC 2 by their first enterprise customers. Worth a 15-minute look?",
            "status": "DRAFT - needs human approval"}


# =============================================================================================== #
# RUN
# =============================================================================================== #
def run(crm=None, cache=None, verbose=True):
    say = log if verbose else (lambda *_: None)
    crm = crm or FakeCRM()
    cache = {} if cache is None else cache
    report = {}

    say("\n=== STEP 1: Collect (paginate, retry on 429) ===")
    raw, cstats = collect()
    say(f"apollo api (page-number pagination): {len(raw['apollo_api'])} people over "
        f"{cstats['apollo_pages']} pages, {cstats['retries']} retries after 429s")
    say(f"hubspot api (cursor pagination): {len(raw['crm_companies'])} companies over {cstats['crm_pages']} pages")
    say(f"files (clay export, webinar list, website forms): {len(raw['files'])} rows")
    items = [(f"apollo:{p['id']}", ("apollo", p)) for p in raw["apollo_api"]] + \
            [(f"file:{i}", ("file", r)) for i, r in enumerate(raw["files"])]
    mapped, map_failed, map_summary = process_all(
        items, lambda k, x: map_apollo(x[1]) if x[0] == "apollo" else map_file(x[1]), "map")
    say(f"mapping: {map_summary}")
    report["collected"] = len(mapped)

    say("\n=== STEP 2: Map to one schema, clean, validate ===")
    cleaned, quarantine = clean_and_validate(mapped)
    for q in quarantine:
        say(f"  quarantined {q['email']!r:32} {q['reasons']}")
    say(f"clean: {len(cleaned)} | quarantined: {len(quarantine)}")
    report["clean"], report["quarantined"] = len(cleaned), len(quarantine)

    say("\n=== STEP 3: Dedupe (email key, domain key, fuzzy name, survivorship) ===")
    contacts, accounts, review, crm_dupes = dedupe(cleaned, raw["crm_companies"])
    say(f"{len(cleaned)} records -> {len(contacts)} unique contacts at {len(accounts)} accounts")
    for a, b, s in review:
        say(f"  needs human review: {a!r} vs {b!r} (similarity {s})")
    for d, ids in crm_dupes.items():
        say(f"  duplicate already in CRM: {d} has company ids {ids} -> merge in CRM")
    report.update(contacts=len(contacts), accounts=len(accounts), crm_duplicates=crm_dupes)

    say("\n=== STEP 4: Enrich (waterfall, cache, credit budget) ===")
    before = {f: sum(not blank(a.get(f)) for a in accounts.values()) for f in ENRICH_FIELDS}
    used, estats, efailed, esummary = enrich(accounts, cache, CONFIG["credit_budget"])
    after = {f: sum(not blank(a.get(f)) for a in accounts.values()) for f in ENRICH_FIELDS}
    for f in ENRICH_FIELDS:
        say(f"  {f:10} filled {before[f]:>2} -> {after[f]:>2} of {len(accounts)}")
    say(f"credits used: {used}/{CONFIG['credit_budget']} | {dict(estats)}")
    for f in efailed:
        say(f"  enrichment failed for {f['key']}: {f['error']} (logged, run continues, retried next run)")
    say(f"  per-record summary: {esummary}")
    report["enrich_failures"] = efailed
    for c in contacts:                                       # push account data back onto contacts
        a = accounts.get(c["domain"])
        if a:
            for f in ENRICH_FIELDS:
                c[f] = a.get(f) if a.get(f) is not None else c.get(f)
    report["credits_used"] = used

    say("\n=== STEP 5: Suppress ===")
    keep, suppressed = suppress([c for c in contacts if c["domain"] in accounts],
                                accounts, raw["crm_deals"], raw["crm_companies"])
    for s in suppressed:
        say(f"  suppressed {s['email']:32} {s['suppress_reason']}")
    report["suppressed"] = Counter(s["suppress_reason"] for s in suppressed)

    say("\n=== STEP 6+7: Score + segment ===")
    scored = []
    for c in keep:
        acc = accounts[c["domain"]]
        scored.append({**c, **score_contact(c, acc), **segment(c, acc)})
    scored.sort(key=lambda x: -x["score"])
    for c in scored:
        say(f"  {c['tier']} {c['score']:>3} (fit {c['fit']:>2}, intent {c['intent']:>2})  "
            f"{c['email']:30} {c['segment']}")
    report["tiers"] = Counter(c["tier"] for c in scored)

    say("\n=== STEP 8: Route ===")
    route(scored, accounts)
    for c in scored:
        say(f"  {c['email']:30} -> {str(c['owner']):6} ({c['route_reason']})")

    say("\n=== STEP 9: CRM write-back (batch upsert, field ownership) ===")
    companies, contact_payloads = to_payloads(scored, accounts)
    say(f"  dry run: {dict(write_back(crm, companies, contact_payloads, dry_run=True))}")
    totals = write_back(crm, companies, contact_payloads)
    say(f"  real run: {dict(totals)} in {crm.calls} API calls so far")
    report["crm"] = dict(totals)

    say("\n=== STEP 10: Outreach drafts (A and B tiers, never sent) ===")
    drafts = [draft_first_touch(c, accounts[c["domain"]]) for c in scored if c["tier"] in {"A", "B"} and c["owner"]]
    for d in drafts[:3]:
        say(f"  [{d['sequence']}] to {d['to']}: {d['body'][:90]}...")
    say(f"  {len(drafts)} drafts created")
    report["drafts"] = len(drafts)

    say("\n=== STEP 11: Report + quality checks ===")
    checks = {
        "every routed contact has a score": all("score" in c for c in scored),
        "no blank values sent to CRM": all(not blank(v) for p in contact_payloads for v in p["properties"].values()),
        "no suppressed contact in drafts": not ({d["to"] for d in drafts} & {s["email"] for s in suppressed}),
        "batches within limit": CONFIG["crm_batch_size"] <= 100,
    }
    for name, ok in checks.items():
        say(f"  [{'PASS' if ok else 'FAIL'}] {name}")
    report["checks"] = checks

    OUT.mkdir(exist_ok=True)
    with open(OUT / "scored_contacts.csv", "w", newline="", encoding="utf-8") as f:
        cols = ["email", "first_name", "last_name", "title", "domain", "company", "country", "employees",
                "industry", "fit", "intent", "score", "tier", "segment", "owner", "route_reason"]
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(scored)
    (OUT / "outreach_drafts.json").write_text(json.dumps(drafts, indent=2, ensure_ascii=False), encoding="utf-8")
    (OUT / "quarantine.json").write_text(json.dumps(quarantine, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    (OUT / "run_report.json").write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    say(f"\nOutputs written to {OUT.relative_to(REPO)}/")
    return report, crm, cache


if __name__ == "__main__":
    random.seed(7)
    ap = argparse.ArgumentParser()
    ap.add_argument("--twice", action="store_true", help="run again to prove re-runs create nothing new")
    args = ap.parse_args()
    report, crm, cache = run()
    if args.twice:
        print("\n\n########## SECOND RUN (same CRM, same cache) ##########")
        report2, _, _ = run(crm=crm, cache=cache, verbose=False)
        print(f"second run CRM result: {report2['crm']}  | credits used: {report2['credits_used']}")
        print("-> 0 created and 0 credits: the pipeline is idempotent and never pays twice.")
