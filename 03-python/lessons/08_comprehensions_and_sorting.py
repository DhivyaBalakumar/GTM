"""
Lesson 8: comprehensions, sorting and lambda
============================================

Run me:  python 03-python/lessons/08_comprehensions_and_sorting.py

A COMPREHENSION builds a list or dict in one line from a loop.
You'll read and write these constantly. A normal for loop always works too.
"""

leads = [
    {"name": "PeopleCo", "country": "DE", "employees": 120, "score": 95},
    {"name": "Nordbank", "country": "NL", "employees": 80, "score": 80},
    {"name": "Kite Labs", "country": "DE", "employees": 8, "score": 35},
    {"name": "Greenleaf", "country": "US", "employees": 2000, "score": 20},
    {"name": "Opal", "country": "DE", "employees": 25, "score": 72},
]

print("=== 1. List comprehension = loop + append in one line ===")
# Long way:
names = []
for lead in leads:
    names.append(lead["name"])
# Short way (same result):
names = [lead["name"] for lead in leads]
print(names)

print("\n=== 2. With a filter (if at the end) ===")
german = [lead["name"] for lead in leads if lead["country"] == "DE"]
print(german)

print("\n=== 3. Transforming values ===")
domains = ["  PeopleCo.de ", "NORDBANKTECH.NL", " opal.de"]
print([d.strip().lower() for d in domains])

print("\n=== 4. if/else INSIDE (choose a value per item) ===")
labels = ["big" if lead["employees"] >= 100 else "small" for lead in leads]
print(labels)
# Filter -> `if` at the END.  Choose a value -> `x if cond else y` at the START.

print("\n=== 5. Dict comprehension ===")
score_by_name = {lead["name"]: lead["score"] for lead in leads}
print(score_by_name)
inverted = {v: k for k, v in {"DE": "Germany", "NL": "Netherlands"}.items()}
print(inverted)

print("\n=== 6. Set comprehension ===")
print({lead["country"] for lead in leads})

print("\n=== 7. any() and all() ===")
print("any US lead?", any(lead["country"] == "US" for lead in leads))
print("all have a score?", all("score" in lead for lead in leads))

print("\n=== 8. sorted() with a key ===")
by_score = sorted(leads, key=lambda lead: lead["score"], reverse=True)
print([f"{l['name']}:{l['score']}" for l in by_score])

# lambda = a tiny unnamed function. `lambda lead: lead["score"]` is the same as:
#   def get_score(lead):
#       return lead["score"]

print("\n=== 9. Sorting by several things: country A-Z, then score high-low ===")
multi = sorted(leads, key=lambda l: (l["country"], -l["score"]))
print([(l["country"], l["name"], l["score"]) for l in multi])

print("\n=== 10. Top N ===")
top3 = sorted(leads, key=lambda l: l["score"], reverse=True)[:3]
print("top 3:", [l["name"] for l in top3])
print("best:", max(leads, key=lambda l: l["score"])["name"])

print("\n=== 11. Flattening a list of lists ===")
pages = [["a", "b"], ["c"], ["d", "e"]]
print([item for page in pages for item in page])

print("\n=== 12. When NOT to use a comprehension ===")
# If it needs try/except, several steps or logging, write a normal loop. Readability wins.

# ---------------------------------------------------------------------------
# TRY IT
# 1. Names of leads with score >= 70, sorted by score high to low, in one expression.
# 2. A dict {name: tier} using "A"/"B"/"C" thresholds 75/50.
# 3. Domains from emails: ["a@x.de", "b@y.nl"] -> ["x.de", "y.nl"]
# ---------------------------------------------------------------------------
