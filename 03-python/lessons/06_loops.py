"""
Lesson 6: loops
===============

Run me:  python 03-python/lessons/06_loops.py

FOR loops do something for every item in a collection.
WHILE loops repeat until a condition becomes False (or you `break`).
Pipelines are loops: for every lead -> clean, enrich, score, save.
"""
import time

leads = [
    {"name": "PeopleCo", "country": "DE", "employees": 120},
    {"name": "Nordbank", "country": "NL", "employees": 80},
    {"name": "Kite Labs", "country": "DE", "employees": 8},
    {"name": "Greenleaf", "country": "US", "employees": 2000},
]

print("=== 1. for over a list ===")
for lead in leads:
    print(lead["name"])

print("\n=== 2. range(): repeat N times ===")
for i in range(3):            # 0, 1, 2
    print("attempt", i)
print(list(range(1, 6)), list(range(0, 23, 10)))   # start, stop (excluded), step

print("\n=== 3. enumerate(): index + item ===")
for i, lead in enumerate(leads, start=1):
    print(f"{i}. {lead['name']}")

print("\n=== 4. zip(): walk two lists together ===")
names = ["PeopleCo", "Nordbank"]
scores = [95, 80]
for name, score in zip(names, scores):
    print(name, score)

print("\n=== 5. Accumulating: totals, counts, filtered lists ===")
total_employees = 0
dach = []
for lead in leads:
    total_employees += lead["employees"]       # same as total = total + ...
    if lead["country"] in {"DE", "AT", "CH"}:
        dach.append(lead["name"])
print("total employees:", total_employees, "| DACH:", dach)

print("\n=== 6. continue (skip this item) and break (stop the loop) ===")
for lead in leads:
    if lead["employees"] < 20:
        print("skip (too small):", lead["name"])
        continue
    if lead["country"] == "US":
        print("found a US lead, stopping:", lead["name"])
        break
    print("process:", lead["name"])

print("\n=== 7. for ... else: runs only if the loop did NOT break ===")
for lead in leads:
    if lead["name"] == "Opal":
        print("found Opal")
        break
else:
    print("Opal not in the list")

print("\n=== 8. while: repeat until a condition changes ===")
attempt = 0
while attempt < 3:
    attempt += 1
    print("try number", attempt)

print("\n=== 9. The RETRY pattern (you'll use this with APIs) ===")
# Pretend an API fails twice then succeeds.
responses = [503, 429, 200]
for attempt in range(1, 6):                 # at most 5 tries
    status = responses.pop(0) if responses else 200
    if status == 200:
        print(f"attempt {attempt}: success")
        break
    wait = 0.1 * 2 ** (attempt - 1)         # 0.1, 0.2, 0.4... (real code: 1, 2, 4 seconds)
    print(f"attempt {attempt}: got {status}, waiting {wait:.1f}s")
    time.sleep(wait)
else:
    print("gave up after 5 tries")

print("\n=== 10. The PAGINATION pattern: keep asking until there's no next page ===")
pages = {None: (["a", "b"], "p2"), "p2": (["c", "d"], "p3"), "p3": (["e"], None)}
cursor, everything = None, []
while True:
    items, next_cursor = pages[cursor]       # real code: an API call with ?after=cursor
    everything.extend(items)
    print(f"got page {cursor!r}: {items}")
    if not next_cursor:
        break
    cursor = next_cursor
print("all items:", everything)

print("\n=== 11. Nested loops ===")
for team, reps in {"DACH": ["lena", "jonas"], "Other": ["maria", "tom"]}.items():
    for rep in reps:
        print(team, rep)

# Avoid infinite loops: `while True` must always have a reachable `break`.
# If a program hangs, press Ctrl + C to stop it.

# ---------------------------------------------------------------------------
# TRY IT
# 1. Print only leads with 20-500 employees, numbered with enumerate.
# 2. Change responses to [503, 503, 503, 503, 503, 503]. What happens?
# 3. Count leads per country with a loop and a dictionary.
# ---------------------------------------------------------------------------
