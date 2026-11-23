"""
Practice API server: behaves like a real CRM / enrichment API, on your own laptop.
==================================================================================

Run it (and leave it running in its own terminal):
    python 06-apis-and-webhooks/practice_server.py

Base URL:  http://localhost:5050
API key:   send the header  Authorization: Bearer practice-key

What it does, on purpose:
  * 401 if the key is missing or wrong
  * Rate limit: 5 requests per second -> 429 with a Retry-After header
  * Random outages: ~5% of requests get 503 (set PRACTICE_FAIL_RATE=0 to turn off, 0.3 for chaos)
  * Pagination: at most 5 companies per page, with a cursor in paging.next.after
  * Batch limit: at most 10 records per upsert call -> 400 if you send more
  * Upserts by domain never create duplicates and never overwrite a value with a blank
  * A plain "create" endpoint that DOES create duplicates (to show why upserts matter)

Endpoints:
  GET  /companies?limit=5&after=<cursor>   list companies, page by page
  GET  /companies/count                    how many companies exist
  POST /companies                          create one (no duplicate check!)
  POST /companies/batch/upsert             {"inputs": [{"id": "<domain>", "properties": {...}}]}
  GET  /enrich?domain=peopleco.de          enrichment data (404 if unknown)
  GET  /status/<code>                      returns that status code (like httpbin.org)
  POST /admin/reset                        restore the starting data (no key needed)
"""
import csv
import os
import random
import time
from collections import deque
from pathlib import Path

from flask import Flask, jsonify, request

API_KEY = "practice-key"
RATE_LIMIT = 5             # requests ...
RATE_WINDOW = 1.0          # ... per this many seconds
FAIL_RATE = float(os.getenv("PRACTICE_FAIL_RATE", "0.05"))
PAGE_SIZE_MAX = 5
BATCH_MAX = 10

DATA = Path(__file__).resolve().parents[1] / "data"
app = Flask(__name__)
recent_requests = deque()
companies = []             # list of dicts; position in the list is the cursor

ENRICHMENT = {
    "peopleco.de": {"employees": 120, "industry": "Software", "country": "DE",
                    "signals": {"raised_recently": True, "hiring_security": True}},
    "nordbanktech.nl": {"employees": 80, "industry": "Fintech", "country": "NL",
                        "signals": {"raised_recently": False, "hiring_security": True}},
    "brightforge.io": {"employees": 140, "industry": "Software", "country": "AT",
                       "signals": {"raised_recently": True, "hiring_security": False}},
    "corvex.de": {"employees": 35, "industry": "Software", "country": "DE",
                  "signals": {"raised_recently": False, "hiring_security": False}},
    "solvia-health.de": {"employees": 95, "industry": "Healthtech", "country": "DE",
                         "signals": {"raised_recently": True, "hiring_security": True}},
    "kitelabs.io": {"employees": 8, "industry": "Software", "country": "DE",
                    "signals": {"raised_recently": False, "hiring_security": False}},
    "altamirapay.com": {"employees": 210, "industry": "Fintech", "country": "ES",
                        "signals": {"raised_recently": True, "hiring_security": False}},
}


def seed():
    companies.clear()
    with open(DATA / "crm_accounts.csv", newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["domain"].lower() == "peopleco.de" and row["name"].isupper():
                continue                       # keep the practice CRM free of duplicates at start
            companies.append({
                "id": str(len(companies) + 1),
                "properties": {
                    "name": row["name"], "domain": row["domain"].lower(), "country": row["country"],
                    "industry": row["industry"], "employees": int(row["employees"]),
                    "owner": row["owner"] or None,
                },
            })


@app.before_request
def misbehave():
    """Runs before every request: auth, rate limit and random outages, like real APIs."""
    if request.path.startswith("/admin"):
        return None
    now = time.time()
    while recent_requests and now - recent_requests[0] > RATE_WINDOW:
        recent_requests.popleft()
    if len(recent_requests) >= RATE_LIMIT:
        response = jsonify({"error": "RATE_LIMIT", "message": "Too many requests. Slow down."})
        response.headers["Retry-After"] = "1"
        return response, 429
    recent_requests.append(now)
    if request.path.startswith("/status"):
        return None
    if request.headers.get("Authorization") != f"Bearer {API_KEY}":
        return jsonify({"error": "UNAUTHORIZED", "message": "Missing or invalid API key."}), 401
    if random.random() < FAIL_RATE:
        return jsonify({"error": "UNAVAILABLE", "message": "Temporary outage, try again."}), 503
    return None


@app.get("/companies")
def list_companies():
    try:
        limit = min(int(request.args.get("limit", PAGE_SIZE_MAX)), PAGE_SIZE_MAX)
        start = int(request.args.get("after", 0))
    except ValueError:
        return jsonify({"error": "BAD_REQUEST", "message": "limit and after must be numbers"}), 400
    page = companies[start:start + limit]
    body = {"results": page}
    if start + limit < len(companies):
        body["paging"] = {"next": {"after": str(start + limit)}}
    return jsonify(body)


@app.get("/companies/count")
def count():
    domains = [c["properties"].get("domain") for c in companies]
    return jsonify({"total": len(companies), "unique_domains": len(set(domains))})


@app.post("/companies")
def create_company():
    body = request.get_json(silent=True) or {}
    props = body.get("properties")
    if not props or not props.get("name"):
        return jsonify({"error": "BAD_REQUEST", "message": "properties.name is required"}), 400
    record = {"id": str(len(companies) + 1), "properties": props}
    companies.append(record)                   # no duplicate check: this is the bug to learn from
    return jsonify(record), 201


@app.post("/companies/batch/upsert")
def batch_upsert():
    body = request.get_json(silent=True) or {}
    inputs = body.get("inputs")
    if not isinstance(inputs, list) or not inputs:
        return jsonify({"error": "BAD_REQUEST", "message": "inputs must be a non-empty list"}), 400
    if len(inputs) > BATCH_MAX:
        return jsonify({"error": "BAD_REQUEST", "message": f"max {BATCH_MAX} records per batch"}), 400
    by_domain = {c["properties"].get("domain"): c for c in companies}
    created = updated = 0
    results = []
    for item in inputs:
        domain = (item.get("id") or "").strip().lower()
        if not domain:
            return jsonify({"error": "BAD_REQUEST", "message": "every input needs an id (domain)"}), 400
        props = {k: v for k, v in (item.get("properties") or {}).items() if v not in (None, "")}
        if domain in by_domain:
            by_domain[domain]["properties"].update(props)
            updated += 1
            results.append(by_domain[domain])
        else:
            record = {"id": str(len(companies) + 1), "properties": {"domain": domain, **props}}
            companies.append(record)
            by_domain[domain] = record
            created += 1
            results.append(record)
    return jsonify({"status": "COMPLETE", "created": created, "updated": updated, "results": results})


@app.get("/enrich")
def enrich():
    domain = (request.args.get("domain") or "").lower()
    if not domain:
        return jsonify({"error": "BAD_REQUEST", "message": "domain is required"}), 400
    if domain not in ENRICHMENT:
        return jsonify({"error": "NOT_FOUND", "message": f"No data for {domain}"}), 404
    return jsonify({"domain": domain, **ENRICHMENT[domain]})


@app.get("/status/<int:code>")
def status(code):
    response = jsonify({"status": code})
    if code == 429:
        response.headers["Retry-After"] = "1"
    return response, code


@app.post("/admin/reset")
def reset():
    seed()
    return jsonify({"status": "reset", "total": len(companies)})


if __name__ == "__main__":
    seed()
    print(f"Practice API on http://localhost:5050  (key: {API_KEY}, fail rate: {FAIL_RATE:.0%})")
    app.run(port=5050, debug=False)
