"""
JSON + APIs + pandas together: the core loop of GTM engineering
===============================================================

Terminal 1:  python 06-apis-and-webhooks/practice_server.py
Terminal 2:  python 15-deep-dives/code/json_apis_pandas_demo.py

Steps:
  1. API + JSON  : page through every company already in the "CRM" (with retries)
  2. pandas      : clean, dedupe and score data/leads_raw.csv
  3. pandas      : keep only companies not already in the CRM
  4. pandas->JSON: convert to clean records (NaN removed, blanks dropped)
  5. API         : batch upsert, then run it again to prove nothing is duplicated

Read alongside 15-deep-dives/02-json-apis-and-pandas.md.
"""
import random
import time
from pathlib import Path

import numpy as np
import pandas as pd
import requests

BASE = "http://localhost:5050"
HEADERS = {"Authorization": "Bearer practice-key"}   # real code: os.getenv("HUBSPOT_TOKEN")
BATCH_SIZE = 10                                       # the practice API's limit (HubSpot: 100)
RETRYABLE = {429, 500, 502, 503, 504}
LEADS = Path(__file__).resolve().parents[2] / "data" / "leads_raw.csv"
PERSONAL = {"gmail.com", "yahoo.com", "outlook.com", "hotmail.com"}


# ----------------------------------------------------------------------------- API
def call(method, path, max_tries=5, **kwargs):
    """Every API call goes through here: timeout, retries with backoff + jitter, Retry-After."""
    kwargs.setdefault("timeout", 10)
    retries = 0
    for attempt in range(1, max_tries + 1):
        wait = 0.5 * 2 ** (attempt - 1) + random.uniform(0, 0.25)
        try:
            r = requests.request(method, BASE + path, headers=HEADERS, **kwargs)
        except (requests.ConnectionError, requests.Timeout):
            r = None
        if r is not None and r.status_code not in RETRYABLE:
            r.raise_for_status()                      # other 4xx: permanent, fail fast
            call.retries += retries
            return r.json() if r.content else None    # JSON text -> Python dicts/lists
        if r is not None:
            wait = float(r.headers.get("Retry-After", wait))
        retries += 1
        if attempt < max_tries:
            time.sleep(wait)
    raise RuntimeError(f"Gave up after {max_tries} tries: {method} {path}")


call.retries = 0


def crm_companies():
    """Pagination: follow paging.next.after until it's missing. Returns a DataFrame."""
    rows, params = [], {"limit": 5}
    while True:
        data = call("GET", "/companies", params=params)
        rows += [item.get("properties") or {} for item in data.get("results", [])]
        after = data.get("paging", {}).get("next", {}).get("after")
        if not after:
            return pd.DataFrame(rows)                 # list of dicts -> DataFrame
        params["after"] = after


# ----------------------------------------------------------------------------- pandas
def clean_and_score(path):
    leads = pd.read_csv(path, dtype=str)
    normalise = (lambda s: s.fillna("").str.strip().str.lower()
                 .str.replace(r"^https?://", "", regex=True).str.replace(r"^www\.", "", regex=True)
                 .str.split("/").str[0].str.split("@").str[-1])
    site, email = normalise(leads["website"]), normalise(leads["contact_email"])
    leads["domain"] = site.where(site != "", email)                       # website, else email domain
    leads = leads[(leads["domain"] != "") & ~leads["domain"].isin(PERSONAL)].copy()

    leads["filled"] = leads.notna().sum(axis=1)                           # dedupe: most complete wins
    leads = leads.sort_values("filled", ascending=False, kind="stable").drop_duplicates("domain")

    leads["employees"] = pd.to_numeric(leads["employees"], errors="coerce")
    country = leads["country"].fillna("").str.strip().str.upper().replace(
        {"GERMANY": "DE", "NETHERLANDS": "NL", "AUSTRIA": "AT"})
    industry = leads["industry"].fillna("").str.lower()
    leads["fit_score"] = (np.where(industry.isin(["software", "saas", "fintech", "health tech"]), 25, 0)
                          + np.where(leads["employees"].between(20, 500), 20, 0)
                          + np.where(country.isin(["DE", "AT", "CH", "NL", "BE", "LU"]), 15, 0))
    return leads.sort_values("fit_score", ascending=False)


def to_api_inputs(df):
    """DataFrame -> clean list of dicts -> the JSON shape the batch endpoint expects."""
    cols = ["domain", "company", "country", "employees", "fit_score"]
    sub = df[cols]
    records = sub.astype(object).where(sub.notna(), None).to_dict(orient="records")   # NaN -> None
    inputs = []
    for r in records:
        props = {"name": r["company"], "country": r["country"],
                 "employees": int(r["employees"]) if r["employees"] is not None else None,
                 "fit_score": int(r["fit_score"])}
        inputs.append({"id": r["domain"],
                       "properties": {k: v for k, v in props.items() if v not in (None, "")}})  # no blanks
    return inputs


def upsert(inputs):
    totals = {"created": 0, "updated": 0}
    for i in range(0, len(inputs), BATCH_SIZE):
        result = call("POST", "/companies/batch/upsert", json={"inputs": inputs[i:i + BATCH_SIZE]})
        totals["created"] += result["created"]
        totals["updated"] += result["updated"]
    return totals


def main():
    try:
        requests.post(f"{BASE}/admin/reset", timeout=5)
    except requests.ConnectionError:
        raise SystemExit("Start the practice API first: python 06-apis-and-webhooks/practice_server.py")

    crm = crm_companies()
    print(f"1. CRM has {len(crm)} companies (read page by page)")

    leads = clean_and_score(LEADS)
    print(f"2. leads: {len(pd.read_csv(LEADS))} raw rows -> {len(leads)} unique companies after cleaning")
    print(leads[["company", "domain", "employees", "fit_score"]].head(5).to_string(index=False))

    new = leads[~leads["domain"].isin(crm["domain"])]
    print(f"3. {len(new)} are new (not in the CRM): {', '.join(new['domain'])}")

    inputs = to_api_inputs(new)
    print(f"4. first API input: {inputs[0] if inputs else None}")

    print(f"5. first upsert:  {upsert(inputs)}")
    print(f"   second upsert: {upsert(inputs)}  <- nothing created: idempotent")
    print(f"   CRM now: {call('GET', '/companies/count')}")
    print(f"   (retries absorbed along the way: {call.retries})")
    requests.post(f"{BASE}/admin/reset", timeout=5)


if __name__ == "__main__":
    main()
