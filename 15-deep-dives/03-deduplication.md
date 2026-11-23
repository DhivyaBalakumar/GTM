# Deep dive 3: Deduplication, from zero to advanced

**Dedupe** is short for **deduplication**: finding records that refer to the same real thing and keeping
only one. This guide builds it up level by level, from the idea to how it's done in production at a
company like Secfix.

Run every level yourself: [code/dedupe_demo.py](code/dedupe_demo.py).

---

## Level 0: what it is and why it matters

A **duplicate** is two or more records about the same real-world thing. Say your CRM has:

| name | domain | owner |
| --- | --- | --- |
| PeopleCo GmbH | peopleco.de | lena |
| PEOPLECO GMBH | PeopleCo.de | tom |

That's one company stored twice. Why it's bad:

- **Two reps call the same company**, which looks unprofessional to the customer.
- **The data is split:** notes on one record, the deal on the other.
- **Reports are wrong** ("we have 500 accounts" when it's really 420).
- **Reps stop trusting the CRM** and go back to spreadsheets, which is exactly what this role is meant
  to fix.

The job post says "pull data from multiple sources, **deduplicate**, score and write it back", so dedupe
is a core part of the job. Every new source (an Apollo export, a webinar list, a website form) brings
the same companies back in a slightly different form.

---

## Level 1: exact duplicates

The simplest case is when values are identical:

```python
domains = ["peopleco.de", "opal.de", "peopleco.de"]
unique = list(set(domains))            # ['peopleco.de', 'opal.de']  (order not kept)
unique = list(dict.fromkeys(domains))  # same, but keeps the original order
```

- `set()` drops duplicates because a set can't hold the same value twice.
- `dict.fromkeys()` does the same while keeping order, because dict keys are unique and dicts remember
  insertion order.

This only catches exact matches. Real data is never that clean.

---

## Level 2: normalise first, then compare

The same company arrives written differently:

```
https://www.PeopleCo.de/about
peopleco.de
anna@PeopleCo.de
```

To a computer these are three different strings. **Normalise** them into one standard form first:

```python
def normalize_domain(value):
    if not value:
        return ""
    v = value.strip().lower()            # remove spaces, lowercase
    if "@" in v:
        v = v.split("@")[-1]             # email -> its domain
    for prefix in ("https://", "http://", "www."):
        if v.startswith(prefix):
            v = v[len(prefix):]          # drop the protocol and www.
    return v.split("/")[0]               # drop any path like /about

# all three -> 'peopleco.de'
```

**Rule:** you can only dedupe what you've normalised. Most dedupe bugs are really normalisation bugs:
a trailing space, a capital letter, a `www.` left in. When two values "look the same" but don't match,
`print(repr(value))` usually shows the hidden difference.

Other fields need normalising too: country (`Germany`, `germany`, `DE` → `DE`), industry (`SaaS`,
`software` → `Software`), emails (lowercase, trimmed), company names for matching (lowercase, legal
suffix removed: `PeopleCo GmbH` → `peopleco`).

---

## Level 3: choose the right key

The **key** is the value that identifies "the same thing".

| Key | Good | Problem |
| --- | --- | --- |
| **Domain** (for companies) | Stable, almost unique, available from websites and work emails | Some companies have several domains |
| Company name | Always present | Spelled many ways; not unique ("Apex" exists 500 times) |
| Email (for contacts) | Unique per person | People change jobs; shared inboxes like info@ |
| Provider or registry ID | Truly unique | Not every source has it |

For B2B companies, the standard key is the **normalised domain**, falling back to the domain of a work
email when the website is missing. **Personal domains** (gmail.com, yahoo.com, outlook.com, web.de) are
excluded, because they aren't companies: deduping on `gmail.com` would merge thousands of unrelated
people into one "company".

Rows with no usable key can't be deduped safely. Put them in a "dropped, and why" list rather than
guessing.

---

## Level 4: decide which duplicate to keep (survivorship)

When two records share a key, which one survives? These are **survivorship rules**:

| Rule | Example | When to use |
| --- | --- | --- |
| **Most complete** | The row with the most filled-in fields | Combining messy lists from different sources |
| **Most recent** | The latest `updated_at` | When freshness matters (employee counts, titles) |
| **Most trusted source** | The CRM (a human edited it) beats a data provider, which beats a scraped list | When sources differ in quality |

The classic code keeps the most complete row:

```python
best = {}
for row in rows:
    key = normalize_domain(row.get("website") or row.get("email"))
    if not key:
        continue                                            # no key: can't dedupe safely
    filled = sum(1 for v in row.values() if v not in (None, ""))
    if key not in best or filled > best[key][0]:            # ">" so ties keep the first one seen
        best[key] = (filled, row)
unique = [row for _, row in best.values()]
```

How it works: the dict `best` holds one entry per domain. Each new row replaces the stored one only if
it has more filled fields. At the end there's exactly one row per domain.

Decide (and write down) what happens on a **tie**. "Keep the first one seen" is a common, predictable
choice.

---

## Level 5: merge instead of just picking (the golden record)

Sometimes no single row is best: one has the employee count, another has the industry. **Merge** them
field by field into one **golden record**:

```python
golden = {
    "name":      crm_row["name"],                                    # the CRM wins for names (a human may have fixed it)
    "owner":     crm_row["owner"],                                   # never lose an existing owner
    "employees": provider_row["employees"] or crm_row["employees"],  # freshest number, fill the gap
    "industry":  crm_row["industry"] or provider_row["industry"],    # keep the CRM's if it has one
}
```

This is where **field ownership** comes in: decide which source is allowed to set which field, and write
it in a table in your README.

| Field | Owner | The pipeline may… |
| --- | --- | --- |
| name, owner, deal stage | CRM / people | Never overwrite on existing records |
| employees, industry | Data provider, unless a person edited it | Fill if empty |
| fit_score, score_reasons | Pipeline | Always write |

Without this, integrations fight: the pipeline overwrites a rep's correction, the rep fixes it, the
pipeline overwrites it again.

---

## Level 6: dedupe in pandas and in SQL

### pandas: "sort the best row first, then keep the first"

```python
df["domain"] = df["website"].apply(normalize_domain)
df["filled"] = df.notna().sum(axis=1)                  # how complete is each row?
df = (df.sort_values("filled", ascending=False, kind="stable")   # best first (stable keeps ties in file order)
        .drop_duplicates(subset="domain", keep="first"))         # one per domain
```

Useful helpers:

- `df.duplicated(subset="domain", keep=False)` marks every row that has a duplicate, so you can look at
  them before deciding.
- `df["domain"].nunique()` vs `len(df)` tells you how many duplicates there are.

### SQL: find them, then keep one per key

```sql
-- find duplicates (ignoring case)
SELECT LOWER(domain) AS domain, COUNT(*) AS copies
FROM accounts
GROUP BY LOWER(domain)
HAVING COUNT(*) > 1;

-- keep the most recent row per domain
WITH ranked AS (
  SELECT *, ROW_NUMBER() OVER (PARTITION BY LOWER(domain) ORDER BY updated_at DESC) AS rn
  FROM accounts
)
SELECT * FROM ranked WHERE rn = 1;
```

`ROW_NUMBER() OVER (PARTITION BY … ORDER BY …)` numbers rows 1, 2, 3 within each domain, best first;
`WHERE rn = 1` keeps the best. Both queries run against this repo's practice database in
[05-sql](../05-sql) (the `accounts` table contains a planted duplicate: `PeopleCo GmbH` and
`PEOPLECO GMBH`).

---

## Level 7: fuzzy matching (when there's no clean key)

Sometimes there's no domain, just names: "Nordbank Tech B.V." vs "Nordbank Technologies". **Fuzzy
matching** gives a similarity score from 0 (nothing in common) to 1 (identical):

```python
from difflib import SequenceMatcher

def similarity(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

similarity("Nordbank Tech", "Nordbank Technologies")   # about 0.76
```

Make it reliable:

1. **Clean the names first:** lowercase, remove legal suffixes (GmbH, AG, B.V., Ltd, Inc).
2. **Use a second signal:** same country, same city, or a similar website.
3. **Use thresholds:**
   - **0.9 or higher:** treat as the same company
   - **0.75 to 0.9:** send to a person to review
   - **below 0.75:** treat as different

Be cautious. **A wrong merge is worse than a duplicate**, because it mixes two customers' data (contacts,
deals, notes) and is hard to undo. A duplicate is annoying; a false merge can send one customer's
information to another company's rep.

For large volumes, the `rapidfuzz` library is much faster than `difflib` and has better scoring
functions (`token_sort_ratio` handles word order, e.g. "Tech Nordbank" vs "Nordbank Tech").

---

## Level 8: entity resolution (the hard cases)

**Entity resolution** is the advanced form of the question: "do these records refer to the same
real-world entity?"

| Hard case | Example | Typical approach |
| --- | --- | --- |
| Several domains | peopleco.de and peopleco.com | Keep a table of alternate domains per account |
| Subsidiaries | PeopleCo Austria GmbH (peopleco.at) | Separate accounts, linked with a parent-company association |
| Rebrands and acquisitions | OldName became NewName | Record the old domain as an alias |
| Contacts who move jobs | anna@peopleco.de becomes anna@newco.io | Same person, new contact at a new account; mark the old one as left |
| Shared domains | Agencies, consultants, gmail.com | Never dedupe on these |
| Typos | "Nordbanc Tech" | Fuzzy match → review queue |

Many of these are **business decisions**, not code decisions. Is a subsidiary its own account? Should
the German and Austrian offices have different owners? Agree them with the sales team, write them down,
and encode them as rules.

---

## Level 9: preventing duplicates (better than cleaning them up)

Cleaning duplicates after the fact is expensive. Stop them from being created in the first place:

1. **Upsert, never blind-create.** "Update if it exists, create if not", keyed on a unique property. In
   HubSpot, mark a domain-key property as unique and use the batch upsert endpoint. In SQL,
   `INSERT … ON CONFLICT(domain) DO UPDATE`. Running the pipeline twice then creates nothing new. That
   property is called **idempotency**.
2. **Dedupe before loading:** clean the batch itself before sending it.
3. **Match against what's already in the CRM:** fetch existing domains first, and keep their owners.
4. **Dedupe events too:** webhooks can arrive twice, so store each event's key in a set (or a database
   table) and skip ones you've already handled.
5. **Normalise at entry:** forms and imports should store the normalised domain.
6. **Beware "search, then create":** a CRM's search index can lag a few seconds behind writes, so two
   quick runs can both "not find" a company and both create it. A batch upsert on a unique property
   avoids that race.

The classic bug report, "every time the sync runs it creates duplicate companies", is almost always a
create-instead-of-upsert bug.

---

## Level 10: measuring it (production habit)

After every pipeline run, check and log:

| Check | Healthy | Worry if |
| --- | --- | --- |
| Duplicate domains in the CRM | 0 | Above 0: normalisation or upserts broke |
| Created count on a re-run of the same input | 0 | Above 0: the load creates instead of upserting |
| Rows dropped, with reasons | A few (personal emails, no domain) | A sudden jump: a source changed format |
| Review queue size | Small and handled | Growing: thresholds too loose, or nobody reviewing |
| Raw rows vs unique companies | A sensible ratio | Unique count tiny: normalisation is over-merging |

Alert someone when a number looks wrong. Put the counts in the run's summary line:

```
SUMMARY read=25 valid=23 unique=19 dropped=2 | CRM created=0 updated=19 | duplicates=0
```

---

## How to say it in an interview

> "I dedupe on normalised domain: lowercase, no protocol, no www, no path, falling back to the
> work-email domain, with personal domains excluded. When records collide I keep the most complete one
> and fill gaps from the others, and the CRM wins for human-edited fields like owner. Fuzzy name
> matches above a threshold go to a review list instead of merging automatically, because a wrong merge
> is worse than a duplicate. And I prevent new duplicates by batch-upserting on a unique domain
> property, so re-running the pipeline never creates copies."

Follow-up questions to be ready for:

| Question | Short answer |
| --- | --- |
| Why domain and not name? | Names vary and aren't unique; domains are stable and almost unique. |
| What about companies with two domains? | An alternate-domain table mapping both to one account. |
| What if two duplicates both have an owner? | Don't auto-merge: flag for the Head of Sales to decide, and keep both owners informed. |
| How do you know dedupe works? | Duplicate-domain check = 0 after each run, and created = 0 on a re-run; both alert if not. |
| What breaks at 10x? | Fuzzy matching every pair gets slow (compare only within the same country or first letter, "blocking"), and the review queue grows, so thresholds and ownership of the queue matter. |

---

## Practise it in this repo

| Level | Where |
| --- | --- |
| 0–4 (Python) | [code/dedupe_demo.py](code/dedupe_demo.py); [03-python/exercises/ex02_collections.py](../03-python/exercises/ex02_collections.py) (`dedupe_keep_most_complete`); [ex04_errors_and_files.py](../03-python/exercises/ex04_errors_and_files.py) |
| 6 (pandas) | [04-pandas/lessons/04_dedupe_sort_group_merge.py](../04-pandas/lessons/04_dedupe_sort_group_merge.py); [04-pandas/exercises/ex01_clean_score.py](../04-pandas/exercises/ex01_clean_score.py) |
| 6 (SQL) | [05-sql/lessons/02_aggregate_group.sql](../05-sql/lessons/02_aggregate_group.sql) (find duplicates); [05_ctes_windows.sql](../05-sql/lessons/05_ctes_windows.sql) (keep one per domain); [06_create_insert_upsert.sql](../05-sql/lessons/06_create_insert_upsert.sql) (upsert) |
| 5, 7, 8 | [08-data-quality/entity_resolution.py](../08-data-quality/entity_resolution.py) |
| 9 | [06-apis-and-webhooks/lessons/03_pagination_and_batching.py](../06-apis-and-webhooks/lessons/03_pagination_and_batching.py) (sections 4–5); live-coding problem P3 in [13-interview-prep/live_coding_practice](../13-interview-prep/live_coding_practice) |
