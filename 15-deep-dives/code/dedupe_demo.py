"""
Deduplication, level by level
=============================

Run me:  python 15-deep-dives/code/dedupe_demo.py

Read alongside 15-deep-dives/03-deduplication.md. Uses data/leads_raw.csv (25 rows with planted
duplicates) and data/crm_accounts.csv.
"""
import sqlite3
from difflib import SequenceMatcher
from pathlib import Path

import pandas as pd

DATA = Path(__file__).resolve().parents[2] / "data"
PERSONAL = {"gmail.com", "yahoo.com", "outlook.com", "hotmail.com"}
SUFFIXES = {"gmbh", "ag", "b.v.", "bv", "ltd", "inc", "sa", "se"}


def section(title):
    print(f"\n=== {title} ===")


def normalize_domain(value):
    if not isinstance(value, str) or not value.strip():
        return ""
    v = value.strip().lower()
    if "@" in v:
        v = v.split("@")[-1]
    for prefix in ("https://", "http://", "www."):
        if v.startswith(prefix):
            v = v[len(prefix):]
    return v.split("/")[0]


section("Level 1: exact duplicates")
domains = ["peopleco.de", "opal.de", "peopleco.de"]
print("set():          ", set(domains))
print("dict.fromkeys():", list(dict.fromkeys(domains)), "(keeps order)")

section("Level 2: normalise first")
raw = ["https://www.PeopleCo.de/about", "peopleco.de", "anna@PeopleCo.de", "  www.peopleco.de  "]
print("before:", len(set(raw)), "distinct values")
print("after: ", {normalize_domain(v) for v in raw})

section("Level 3: the key (website, else work-email domain; personal domains excluded)")
with open(DATA / "leads_raw.csv", encoding="utf-8") as f:
    import csv
    rows = list(csv.DictReader(f))
keyed, dropped = [], []
for r in rows:
    key = normalize_domain(r["website"]) or normalize_domain(r["contact_email"])
    (dropped if not key or key in PERSONAL else keyed).append({**r, "domain": key})
print(f"{len(rows)} rows -> {len(keyed)} with a usable key, {len(dropped)} dropped:",
      [d["contact_email"] for d in dropped])

section("Level 4: survivorship (keep the most complete row)")
best = {}
for r in keyed:
    filled = sum(1 for v in r.values() if v not in (None, ""))
    if r["domain"] not in best or filled > best[r["domain"]][0]:
        best[r["domain"]] = (filled, r)
print(f"{len(keyed)} rows -> {len(best)} unique companies")
for domain in ["peopleco.de", "nordbanktech.nl", "brightforge.io", "vektorcloud.nl"]:
    group = [r["company"] for r in keyed if r["domain"] == domain]
    print(f"  {domain:16} {group} -> kept {best[domain][1]['company']!r}")

section("Level 5: merge into a golden record (fill gaps, CRM wins for owner/name)")
crm_row = {"name": "PeopleCo GmbH", "owner": "lena", "employees": None, "industry": "Software"}
provider_row = {"name": "Peopleco", "owner": None, "employees": 120, "industry": "SaaS"}
golden = {
    "name": crm_row["name"] or provider_row["name"],
    "owner": crm_row["owner"] or provider_row["owner"],
    "employees": provider_row["employees"] or crm_row["employees"],
    "industry": crm_row["industry"] or provider_row["industry"],
}
print(golden)

section("Level 6a: pandas")
df = pd.read_csv(DATA / "leads_raw.csv", dtype=str)
site, email = df["website"].apply(normalize_domain), df["contact_email"].apply(normalize_domain)
df["domain"] = site.where(site != "", email)
df = df[(df["domain"] != "") & ~df["domain"].isin(PERSONAL)].copy()
print("rows with a duplicate:")
print(df[df.duplicated(subset="domain", keep=False)].sort_values("domain")[["company", "domain", "employees"]]
      .to_string(index=False))
df["filled"] = df.notna().sum(axis=1)
unique = df.sort_values("filled", ascending=False, kind="stable").drop_duplicates(subset="domain", keep="first")
print(f"{len(df)} rows -> {len(unique)} unique")

section("Level 6b: SQL")
con = sqlite3.connect(":memory:")
pd.read_csv(DATA / "crm_accounts.csv").to_sql("accounts", con, index=False)
print(pd.read_sql("""SELECT LOWER(domain) AS domain, COUNT(*) AS copies, GROUP_CONCAT(name, ' | ') AS names
                     FROM accounts GROUP BY LOWER(domain) HAVING COUNT(*) > 1""", con).to_string(index=False))
kept = pd.read_sql("""WITH ranked AS (
                        SELECT *, ROW_NUMBER() OVER (PARTITION BY LOWER(domain) ORDER BY created_at DESC) AS rn
                        FROM accounts)
                      SELECT name, domain, created_at FROM ranked WHERE rn = 1 AND LOWER(domain) = 'peopleco.de'""", con)
print("kept (most recent):", kept.to_dict("records"))
print("note: 'most recent' kept the ALL-CAPS copy. Survivorship rules have trade-offs; the CRM-trusted name may be better.")

section("Level 7: fuzzy matching with thresholds")


def name_key(name):
    return " ".join(w for w in name.lower().split() if w not in SUFFIXES)


def decide(a, b, same_country=True):
    score = SequenceMatcher(None, name_key(a), name_key(b)).ratio()
    if not same_country:
        return score, "different (country differs)"
    if score >= 0.9:
        return score, "same company"
    if score >= 0.75:
        return score, "HUMAN REVIEW"
    return score, "different"


for a, b, same in [("Nordbank Tech B.V.", "NORDBANK TECH", True),
                   ("Nordbank Tech B.V.", "Nordbanc Tech", True),
                   ("Nordbank Tech B.V.", "Nordbank Technologies", True),
                   ("Nordbank Tech B.V.", "Nordic Bank Solutions", True),
                   ("Nordbank Tech B.V.", "Nordbank Tech", False)]:
    score, verdict = decide(a, b, same)
    print(f"  {a!r:22} vs {b!r:24} {score:.2f} -> {verdict}")
print("note: 'Nordbanc' scored 0.92 and would auto-merge. If it's a different company, that's a false merge:")
print("      tune thresholds on real examples, and require a second signal (city, website) before merging.")

section("Level 9: prevent duplicates with an upsert (run twice, same row count)")
con.execute("CREATE TABLE companies (domain TEXT PRIMARY KEY, name TEXT, employees INTEGER)")
batch = [("peopleco.de", "PeopleCo GmbH", 120), ("opal.de", "Opal Analytics", 25)]
for run in (1, 2):
    con.executemany("""INSERT INTO companies VALUES (?, ?, ?)
                       ON CONFLICT(domain) DO UPDATE SET name = excluded.name, employees = excluded.employees""",
                    batch)
    print(f"  after run {run}: {con.execute('SELECT COUNT(*) FROM companies').fetchone()[0]} rows")

section("Level 10: the checks to log after every run")
dupes = con.execute("SELECT COUNT(*) FROM (SELECT domain FROM companies GROUP BY domain HAVING COUNT(*) > 1)").fetchone()[0]
print(f"SUMMARY read={len(rows)} keyed={len(keyed)} unique={len(best)} dropped={len(dropped)} | duplicates={dupes}")
