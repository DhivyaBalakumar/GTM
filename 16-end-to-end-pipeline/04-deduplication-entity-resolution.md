# Step 4: Deduplication and entity resolution

**Goal:** every real person exists once, every real company exists once, each person is linked to the
right company, and the surviving record has the best value for every field.

Duplicates cause: two reps emailing the same CTO, broken scores (signals split over two records),
inflated pipeline reports and wasted enrichment credits. Full theory, level by level:
[15-deep-dives/03-deduplication.md](../15-deep-dives/03-deduplication.md).

## 4.0 Start from zero

**A duplicate** = two or more records describing the same real person or company.

**Where they come from:** the same CTO is in Apollo *and* registered for your webinar *and* already in
the CRM. Three sources, one person.

**Why they hurt:**

| Problem | Example |
| --- | --- |
| Embarrassment | Two reps email the same CTO on the same day |
| Wrong scores | The funding signal sits on record A, the job post on record B: neither scores high |
| Wasted money | You pay to enrich the same company twice |
| Wrong reports | "We have 1,200 target accounts" when it's 900 |

**The three levels:**

1. **Exact**: same key after normalising (`anna@peopleco.de` twice).
2. **Fuzzy**: similar text ("Nordbanc Tech" ≈ "Nordbank Tech", similarity 0.92; "Nordbank Tech B.V." vs "NORDBANK TECH" becomes 1.0 once the match key drops case and the legal suffix).
3. **Entity resolution**: combining clues (name + country + city + domain) to decide, with a human
   for borderline cases.

**What "similarity 0.0–1.0" means:** a score of how much two strings overlap. `difflib.SequenceMatcher`
and `rapidfuzz` compute it. 1.0 = identical, 0.5 = half the characters line up.

```python
from difflib import SequenceMatcher
SequenceMatcher(None, "nordbank tech", "nordbank tech").ratio()      # 1.0
SequenceMatcher(None, "nordbank tech", "nordbanc tech").ratio()      # ~0.92
SequenceMatcher(None, "nordbank tech", "nordic bank").ratio()        # ~0.67
```

**Merge, don't delete:** when two records are the same, you don't throw one away. You build one
**golden record** taking the best value of each field (**survivorship**) and remember where each
value came from (**lineage**).

## 4.1 Tools

| Tool | What it does | Click or code |
| --- | --- | --- |
| **pandas** `drop_duplicates`, `groupby` | Exact-key dedupe and survivorship | Code |
| **rapidfuzz** (or stdlib `difflib`) | Fuzzy string similarity (`token_sort_ratio`, `Jaro-Winkler`) | Code |
| **recordlinkage**, **dedupe.io**, **Splink** | Full entity-resolution libraries: blocking, comparison, probabilistic matching (Splink scales on Spark/DuckDB) | Code |
| **SQL** `ROW_NUMBER() OVER (PARTITION BY ...)` | Pick one survivor per key in a warehouse | Code |
| **HubSpot "Manage duplicates"** | Suggests duplicate contacts/companies, merge by click | Click |
| **Salesforce Duplicate & Matching Rules** | Block or alert on duplicates at entry | Click (config) |
| **Dedupely, Insycle, Koalify, DemandTools, RingLead (ZoomInfo Ops)** | Bulk find + merge in CRMs with rules | Click |
| **Clay** "Dedupe" table setting / lookups | Skip rows whose key already exists | Click |
| **LeanData** (Salesforce) | Lead-to-account matching | Click (config) |

## 4.2 The process

1. **Choose keys per object**:
   - Contact: normalised email (best), else LinkedIn URL, else (first name + last name + domain).
   - Company: normalised domain (best), else (name match key + country).
2. **Exact match** on the keys → groups.
3. **Fuzzy match** only what has no key, and only within a **block** (same country, same first
   letter...) so you don't compare everything with everything.
4. **Decide with thresholds**: ≥ 0.90 auto-merge, 0.75–0.90 human review, < 0.75 different.
5. **Cluster** (A=B and B=C ⇒ A, B, C are one entity): union-find.
6. **Survivorship**: build the golden record field by field, with **lineage**.
7. **Match against the CRM** so you update existing records instead of creating new ones, and detect
   duplicates already inside the CRM.
8. **Prevent** future duplicates: upsert by unique key (chapter 08), CRM duplicate rules.
9. **Measure**: duplicates found per run, precision of auto-merges (spot-check a sample).

## 4.3 Concepts

| Concept | Meaning |
| --- | --- |
| **Deterministic matching** | Same key ⇒ same entity (email, domain, external ID) |
| **Probabilistic / fuzzy matching** | Similar enough ⇒ probably same (names, addresses) |
| **Blocking** | Only compare records that share a cheap key, turning n² comparisons into a few |
| **False merge vs missed duplicate** | Merging two different companies is worse than missing a duplicate: be strict on auto-merge |
| **Survivorship rules** | Which value wins: source priority, most recent, most complete, human-edited beats machine |
| **Golden record** | The merged best version |
| **Lineage** | Which source each surviving value came from |
| **Lead-to-account matching** | Attach a person to the right company (by email domain, then fuzzy name) |
| **Parent/child accounts** | `siemens.com` vs `siemens-healthineers.com`: related, not duplicates |
| **Multi-domain companies** | `peopleco.de` and `peopleco.com`: same company, needs an alias table |

## 4.4 The code

### Exact keys

```python
contacts = clean.sort_values("source_rank").drop_duplicates(subset="email", keep="first")
```

That keeps the row from the most trusted source but **throws away** the other rows' values. Better:
survivorship.

### Survivorship with lineage

```python
SOURCE_PRIORITY = ["crm", "apollo", "clay", "webinar", "website"]   # CRM edits by humans win

def golden(records, fields):
    rank = {s: i for i, s in enumerate(SOURCE_PRIORITY)}
    ordered = sorted(records, key=lambda r: (rank.get(r["source"], 99), -filled(r, fields)))
    out, lineage = {}, {}
    for f in fields:
        for r in ordered:                       # first non-blank value from the best source
            if r.get(f) not in (None, ""):
                out[f], lineage[f] = r[f], r["source"]
                break
    out["sources"], out["lineage"] = sorted({r["source"] for r in records}), lineage
    return out
```

Other common rules: *most recent wins* for job title (people change jobs), *max* for employee count
from a fresh provider, *never overwrite a human-entered value* with a machine value.

### Fuzzy company names with blocking

```python
from rapidfuzz import fuzz          # pip install rapidfuzz ; difflib.SequenceMatcher works too
SUFFIXES = {"gmbh", "ag", "bv", "b.v.", "ltd", "inc", "sa", "se"}

def name_key(n):
    return " ".join(w for w in re.sub(r"[^\w\s.]", " ", n.lower()).split() if w not in SUFFIXES)

blocks = defaultdict(list)
for r in no_domain_rows:
    blocks[(r["country"], name_key(r["company"])[:1])].append(r)    # same country + first letter

pairs = []
for block in blocks.values():
    for a, b in itertools.combinations(block, 2):
        s = fuzz.token_sort_ratio(name_key(a["company"]), name_key(b["company"])) / 100
        if s >= 0.90:   pairs.append((a["id"], b["id"], "auto"))
        elif s >= 0.75: pairs.append((a["id"], b["id"], "review"))
```

### Clustering with union-find

```python
parent = {}
def find(x):
    parent.setdefault(x, x)
    while parent[x] != x:
        parent[x] = parent[parent[x]]          # path compression
        x = parent[x]
    return x
def union(a, b):
    parent[find(a)] = find(b)

for a, b, kind in pairs:
    if kind == "auto":
        union(a, b)
clusters = defaultdict(list)
for r in rows:
    clusters[find(r["id"])].append(r)          # each cluster -> one golden record
```

### SQL version (warehouse)

```sql
WITH ranked AS (
  SELECT *,
         ROW_NUMBER() OVER (
           PARTITION BY lower(email)
           ORDER BY CASE source WHEN 'crm' THEN 1 WHEN 'apollo' THEN 2 ELSE 3 END,
                    updated_at DESC) AS rn
  FROM stg_contacts
)
SELECT * FROM ranked WHERE rn = 1;
```

### Duplicates already inside the CRM

```python
crm_by_domain = defaultdict(list)
for c in crm_companies:
    crm_by_domain[normalise_domain(c["properties"]["domain"])].append(c["id"])
crm_dupes = {d: ids for d, ids in crm_by_domain.items() if len(ids) > 1}
# -> report them; merge via POST /crm/v3/objects/companies/merge or the HubSpot UI
```

In the demo, `dedupe()` merges 23 clean records into 22 contacts at 19 accounts (Sanne de Vries
appears in both Apollo and the webinar list) and reports that `peopleco.de` exists **twice** in the
CRM (`PeopleCo GmbH` id 1 and `PEOPLECO GMBH` id 14), which is exactly the kind of mess a first GTM
engineer finds on day one.

## 4.5 Pitfalls

- Fuzzy matching across countries ("Nordbank Tech" NL vs "Nordic Bank" NO).
- Auto-merging at a low threshold. One wrong merge destroys a real account's history.
- Using company name as the account key.
- Treating `info@` and `anna@` at the same domain as the same contact.
- Deduping only the new batch and forgetting the CRM.

## 4.6 Interview lines

> "Domain is my account key and email is my contact key. I exact-match first, fuzzy-match only what
> has no key, within blocks like same country, auto-merge only above 0.9 and send 0.75–0.9 to human
> review, because a false merge is worse than a missed duplicate. Survivorship is field by field with
> lineage, and human edits in the CRM always beat provider data."

## 4.7 Summary

- Keys: **email** for contacts, **domain** for companies (normalised first).
- **Exact match first**, fuzzy only what has no key, **inside blocks** (same country).
- Thresholds: **≥ 0.90 auto-merge, 0.75–0.90 human review, < 0.75 different**. A false merge is worse
  than a missed duplicate.
- **Cluster** chains of matches with union-find.
- **Survivorship field by field** with lineage; human CRM edits beat providers.
- Dedupe **against the CRM** too, and report duplicates already inside it.

## 4.8 Key functions to remember

| Function | Input → output |
| --- | --- |
| `name_key(name)` | `"PeopleCo GmbH"` → `"peopleco"` (match key) |
| `similarity(a, b)` | two names → 0.0–1.0 |
| `completeness(rec, fields)` | record → number of filled fields |
| `survivorship(records, fields)` | duplicate group → golden record + `sources` + `lineage` |
| `dedupe(cleaned, crm_companies)` | clean rows + CRM → `contacts, accounts, review, crm_dupes` |
| `find` / `union` | ids → cluster representative (union-find) |

## 4.9 Important logic

| Case | Decision |
| --- | --- |
| Same normalised email | Same contact |
| Same normalised domain | Same company |
| No domain, same country, name similarity ≥ 0.90 | Auto-merge into that company |
| No domain, same country, 0.75–0.90 | Human review list |
| Different countries | Never fuzzy-merge |
| Two values conflict | Source priority (`crm > apollo > clay > webinar > website`), then completeness; human edit always wins |
| Same domain twice inside the CRM | Report as CRM duplicate; merge in the CRM |

## 4.10 Check yourself

1. Why not use company name as the account key?
2. What does blocking save, and what's the risk if the block is too narrow?
3. A merges with B (0.93), B merges with C (0.91). What does union-find conclude about A and C?
4. Which wins for `jobtitle`: a rep's edit in the CRM last month, or Apollo's value today? Why?

<details><summary>Answers</summary>

1. Many spellings and legal suffixes; different companies can share names.
2. It saves comparisons (n² → small groups); too narrow and true duplicates land in different blocks and are missed.
3. A, B and C are one cluster (one entity).
4. Usually the human edit (field ownership), unless your rule says "newest wins for titles" and Apollo's data is verified newer; whatever the rule, write it down in config.
</details>
