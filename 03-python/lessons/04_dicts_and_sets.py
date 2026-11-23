"""
Lesson 4: dictionaries and sets
===============================

Run me:  python 03-python/lessons/04_dicts_and_sets.py

A DICTIONARY maps keys (labels) to values: {"name": "PeopleCo", "employees": 120}
Every CSV row and every API response becomes dictionaries. This is the most important
data structure for GTM work.

A SET is a collection with no duplicates, built for fast "have I seen this?" checks.
"""

print("=== 1. Creating and reading ===")
company = {"name": "PeopleCo GmbH", "domain": "peopleco.de", "employees": 120}
print(company["name"])                 # read a value by key
# company["country"] -> KeyError: 'country' (the key doesn't exist)
print(company.get("country"))          # .get returns None instead of crashing
print(company.get("country", "unknown"))   # ...or a default you choose

print("\n=== 2. Adding, changing, removing ===")
company["country"] = "DE"              # add a new key
company["employees"] = 125             # change an existing one
company.update({"industry": "Software", "owner": "lena"})   # add/change several
del company["owner"]                   # remove
print(company)

print("\n=== 3. Looping ===")
for key in company:                    # loops over KEYS
    print("key:", key)
for key, value in company.items():     # keys AND values (most common)
    print(f"{key} = {value}")
print(list(company.keys()), list(company.values()))

print("\n=== 4. Checking keys ===")
print("domain" in company, "owner" in company)

print("\n=== 5. Nested data: how API responses look ===")
response = {
    "results": [
        {"id": "1", "properties": {"name": "PeopleCo", "numberofemployees": "120"}},
        {"id": "2", "properties": {"name": "Nordbank"}},
        {"id": "3"},
    ],
    "paging": {"next": {"after": "3"}},
}
for item in response["results"]:
    props = item.get("properties") or {}           # {} if missing or None
    print(item["id"], props.get("name", "?"), props.get("numberofemployees", "unknown"))

# Safe chained access: each .get(..., {}) protects the next step
next_cursor = response.get("paging", {}).get("next", {}).get("after")
print("next page cursor:", next_cursor)
no_paging = {"results": []}
print("cursor when there's no next page:", no_paging.get("paging", {}).get("next", {}).get("after"))

print("\n=== 6. Dictionaries as LOOKUP TABLES (very common) ===")
crm_companies = [
    {"domain": "peopleco.de", "owner": "lena"},
    {"domain": "nordbanktech.nl", "owner": "tom"},
]
owner_by_domain = {c["domain"]: c["owner"] for c in crm_companies}   # build once
print(owner_by_domain)
print("peopleco.de owner:", owner_by_domain.get("peopleco.de"))     # instant lookup
print("newco.io owner:", owner_by_domain.get("newco.io"))           # None = not in CRM

print("\n=== 7. Counting and grouping with dictionaries ===")
countries = ["DE", "NL", "DE", "AT", "DE", "NL"]
counts = {}
for c in countries:
    counts[c] = counts.get(c, 0) + 1        # start at 0 if new, then add 1
print(counts)

leads = [("DE", "peopleco.de"), ("NL", "nordbanktech.nl"), ("DE", "corvex.de")]
by_country = {}
for country, domain in leads:
    by_country.setdefault(country, []).append(domain)   # create list if new, then append
print(by_country)

print("\n=== 8. Sets: unique values and fast membership ===")
domains = ["peopleco.de", "corvex.de", "peopleco.de", "opal.de"]
unique = set(domains)
print(unique, "| unique count:", len(unique))

seen = set()
for d in domains:
    if d in seen:                   # very fast even with millions of items
        print("duplicate, skipping:", d)
        continue
    seen.add(d)
print("seen:", seen)

print("\n=== 9. Set maths ===")
crm = {"peopleco.de", "nordbanktech.nl", "opal.de"}
new_list = {"peopleco.de", "corvex.de", "kitelabs.io"}
print("already in CRM:", crm & new_list)    # intersection
print("brand new:", new_list - crm)         # difference
print("everything:", crm | new_list)        # union

print("\n=== 10. Set of tuples: deduplicating webhook events ===")
events = [(101, 9001), (101, 9001), (102, 9002)]
processed = set()
for key in events:
    if key in processed:
        print("already processed", key)
    else:
        processed.add(key)
        print("processing", key)

# ---------------------------------------------------------------------------
# TRY IT
# 1. Count how many leads each owner has from a list like ["lena", "tom", "lena"].
# 2. Using set maths, find domains in the CRM that are NOT in the new list.
# 3. Why use .get() instead of [] when reading API data?
# ---------------------------------------------------------------------------
