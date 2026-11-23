"""
API lesson 1: requests basics
=============================

First start the practice API in another terminal:
    python 06-apis-and-webhooks/practice_server.py
Then run me:
    python 06-apis-and-webhooks/lessons/01_requests_basics.py

(Some calls may randomly get 503 or 429: that's the practice server being realistic.
Lesson 2 shows how to handle them. Just re-run if one fails here.)
"""
import time

import requests

BASE = "http://localhost:5050"
HEADERS = {"Authorization": "Bearer practice-key"}   # real code: read the key from .env


def pause():
    time.sleep(0.3)          # stay under the 5 requests/second limit in this simple lesson


print("=== 1. A GET request ===")
r = requests.get(f"{BASE}/companies", headers=HEADERS, timeout=10)
print("status code:", r.status_code)
print("content type:", r.headers.get("Content-Type"))
data = r.json()                                   # JSON body -> Python dict
print("keys in the body:", list(data.keys()))
print("first company:", data["results"][0])
pause()

print("\n=== 2. Query parameters with params= ===")
r = requests.get(f"{BASE}/companies", params={"limit": 2}, headers=HEADERS, timeout=10)
print("the URL requests built:", r.url)
print("names:", [c["properties"]["name"] for c in r.json()["results"]])
print("next page cursor:", r.json().get("paging", {}).get("next", {}).get("after"))
pause()

print("\n=== 3. What happens without the API key: 401 ===")
r = requests.get(f"{BASE}/companies", timeout=10)
print(r.status_code, r.json())
# 401 = your fault (missing/wrong key). Retrying won't help. Fix the key.
pause()

print("\n=== 4. A 404 from the enrichment endpoint ===")
r = requests.get(f"{BASE}/enrich", params={"domain": "unknown-company.io"}, headers=HEADERS, timeout=10)
print(r.status_code, r.json())
# For enrichment, 404 is NORMAL ("we have no data on this company"): handle it, don't crash.
pause()

print("\n=== 5. A successful enrichment ===")
r = requests.get(f"{BASE}/enrich", params={"domain": "peopleco.de"}, headers=HEADERS, timeout=10)
if r.ok:                                          # r.ok is True for any 2xx
    info = r.json()
    print(info["employees"], info["industry"], info["signals"])
pause()

print("\n=== 6. A POST with a JSON body (json= converts the dict for you) ===")
body = {"inputs": [{"id": "newco.io", "properties": {"name": "NewCo", "country": "DE", "employees": 40}}]}
r = requests.post(f"{BASE}/companies/batch/upsert", json=body, headers=HEADERS, timeout=10)
print(r.status_code, {k: r.json()[k] for k in ("created", "updated")})
pause()

print("\n=== 7. raise_for_status(): turn 4xx/5xx into an exception ===")
r = requests.get(f"{BASE}/status/400", headers=HEADERS, timeout=10)
try:
    r.raise_for_status()
except requests.HTTPError as e:
    print("HTTPError:", e)
pause()

print("\n=== 8. Timeouts and connection errors ===")
try:
    requests.get("http://localhost:5999/nothing-here", timeout=2)   # nothing listens on 5999
except requests.ConnectionError:
    print("ConnectionError: nothing is listening there (server down? wrong port?)")
# Always pass timeout=... Without it, a stuck server can freeze your script forever.

print("\n=== 9. Reading a nested response safely ===")
r = requests.get(f"{BASE}/companies", params={"limit": 5}, headers=HEADERS, timeout=10)
for item in r.json().get("results", []):
    props = item.get("properties") or {}
    print(f"{props.get('name', '?'):22} {props.get('domain', ''):20} owner={props.get('owner') or '-'}")

print("\n=== 10. The same pattern works on real public APIs ===")
print("""
    r = requests.get("https://api.github.com/users/octocat", timeout=10)
    print(r.status_code, r.json()["name"], r.json()["public_repos"])
""")

# ---------------------------------------------------------------------------
# TRY IT
# 1. Remove pause() calls and run again quickly. What status codes appear?
# 2. Upsert newco.io again with employees 45. Is it created or updated?
# 3. Call /status/503 and print the status and body.
# ---------------------------------------------------------------------------
