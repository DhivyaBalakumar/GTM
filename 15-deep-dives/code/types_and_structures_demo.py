"""
Data types and data structures, demonstrated with GTM data
==========================================================

Run me:  python 15-deep-dives/code/types_and_structures_demo.py

Read alongside 15-deep-dives/01-data-types-and-structures.md. Each section prints what it shows.
"""
import copy
import json
from collections import Counter, defaultdict

import pandas as pd


def section(title):
    print(f"\n=== {title} ===")


section("1. Types vs structures")
lead = {"name": "PeopleCo GmbH", "employees": 120, "score": 87.5, "is_customer": False,
        "owner": None, "tags": ["software", "dach"]}
for key, value in lead.items():
    print(f"{key:12} -> {type(value).__name__:8} {value!r}")
print("the whole record is a", type(lead).__name__)

section("2. The CSV text trap")
employees = "120"
print("'120' + '5' =", employees + "5")
try:
    employees >= 20
except TypeError as e:
    print("TypeError:", e)
print("int('120') >= 20 ->", int(employees) >= 20)


def safe_int(value, default=None):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


print("safe_int:", [safe_int(v) for v in ["120", "abc", None, "51-200"]])

section("3. Missing values and truthiness")
for value in [None, 0, "", " ", [], [None], "0"]:
    print(f"{value!r:8} -> {'True' if value else 'False'}")
employees = 0
print("`if not employees` treats 0 as missing:", not employees, "| `is None` doesn't:", employees is None)

section("4. NaN breaks JSON")
df = pd.DataFrame([{"name": "Mosaic HR", "owner": None, "employees": 70}])
records = df.to_dict(orient="records")
print("raw record:", records)
try:
    json.dumps(records, allow_nan=False)
except ValueError as e:
    print("ValueError:", e)
clean = df.astype(object).where(df.notna(), None).to_dict(orient="records")
clean = [{k: v for k, v in r.items() if v is not None} for r in clean]
print("clean record:", json.dumps(clean))

section("5. The copy trap")
original = {"name": "PeopleCo", "score": 80}
alias = original
alias["score"] = 95
print("after changing the alias, original score =", original["score"])
real_copy = dict(original)
real_copy["score"] = 50
print("after changing a real copy, original score =", original["score"])
nested = {"tags": ["software"]}
shallow, deep = nested.copy(), copy.deepcopy(nested)
shallow["tags"].append("dach")
print("shallow copy shares inner lists:", nested["tags"], "| deep copy doesn't:", deep["tags"])

section("6. Lists: batching")
records = [f"company_{i}" for i in range(1, 231)]
sizes = [len(records[i:i + 100]) for i in range(0, len(records), 100)]
print("230 records in batches of 100 ->", sizes)

section("7. Tuples: returning two values, and hashable keys")


def route(country, existing_owner=None):
    if existing_owner:
        return existing_owner, "existing owner"
    return ("lena", "DACH round-robin") if country in {"DE", "AT", "CH"} else ("maria", "general")


owner, reason = route("AT")
print(owner, "|", reason)
try:
    {["a", 1]: "x"}
except TypeError as e:
    print("list as a key ->", e)
print("tuple as a key works:", {("a", 1): "x"})

section("8. Dicts: lookup, counting, grouping, dedupe")
crm = [{"domain": "peopleco.de", "owner": "lena"}, {"domain": "nordbanktech.nl", "owner": "tom"}]
owner_by_domain = {c["domain"]: c["owner"] for c in crm}
print("lookup peopleco.de:", owner_by_domain.get("peopleco.de"), "| newco.io:", owner_by_domain.get("newco.io"))
countries = ["DE", "NL", "DE", "AT", "DE"]
counts = {}
for c in countries:
    counts[c] = counts.get(c, 0) + 1
print("counts:", counts, "| Counter:", Counter(countries).most_common(2))
by_owner = defaultdict(list)
for owner, company in [("lena", "PeopleCo"), ("tom", "Nordbank"), ("lena", "Solvia")]:
    by_owner[owner].append(company)
print("grouped:", dict(by_owner))
rows = [{"domain": "peopleco.de", "name": "Peopleco", "employees": ""},
        {"domain": "peopleco.de", "name": "PeopleCo GmbH", "employees": "120"}]
best = {}
for row in rows:
    filled = sum(1 for v in row.values() if v not in (None, ""))
    if row["domain"] not in best or filled > best[row["domain"]][0]:
        best[row["domain"]] = (filled, row)
print("dedupe kept:", [r["name"] for _, r in best.values()])

section("9. Sets: unique values, set maths, process-once")
crm_domains = {"peopleco.de", "opal.de"}
new_domains = {"peopleco.de", "kitelabs.io"}
print("brand new:", new_domains - crm_domains, "| already in CRM:", new_domains & crm_domains)
processed, handled = set(), 0
for event in [(101, 9001), (101, 9001), (102, 9002)]:
    if event in processed:
        print("skip duplicate", event)
        continue
    processed.add(event)
    handled += 1
print("handled", handled, "events")

section("10. Nested API data, read safely")
response = {"results": [{"id": "1", "properties": {"name": "PeopleCo", "numberofemployees": "120"}},
                        {"id": "2", "properties": {"name": "Nordbank"}},
                        {"id": "3", "properties": None}]}
for item in response.get("results", []):
    props = item.get("properties") or {}
    print(item["id"], props.get("name", "?"), safe_int(props.get("numberofemployees"), 0))
print("next cursor:", response.get("paging", {}).get("next", {}).get("after"))
rows = [{"id": item["id"], **(item.get("properties") or {})} for item in response["results"]]
print("flattened:", rows)

section("11. pandas: list of dicts <-> DataFrame, dtypes")
df = pd.DataFrame([{"name": "PeopleCo", "employees": "120"}, {"name": "Brightforge", "employees": "51-200"}])
print(df.dtypes.to_dict())
df["employees_num"] = pd.to_numeric(df["employees"], errors="coerce")
print(df)
print("back to records:", df[["name"]].to_dict(orient="records"))

section("12. Speed: list vs set membership")
import time

big_list = [f"company{i}.de" for i in range(200_000)]
big_set = set(big_list)
targets = [f"company{i}.de" for i in range(199_000, 199_500)]
start = time.perf_counter()
sum(t in big_list for t in targets)
list_time = time.perf_counter() - start
start = time.perf_counter()
sum(t in big_set for t in targets)
set_time = time.perf_counter() - start
print(f"500 lookups: list {list_time:.3f}s vs set {set_time:.5f}s")
