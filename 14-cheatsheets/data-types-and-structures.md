# Cheat sheet: data types and data structures (and which ones matter for this role)

**One-line difference:** a **data type** is what kind of *single value* something is (text, number,
true/false, missing). A **data structure** is a *container* that holds and organises many values
(list, dict, set, tuple, DataFrame).

Priority key: **Must** = you'll use it every day in this role · **Good** = useful, learn after the
Musts · **Skip** = not tested for GTM engineering.

Full explanations: [15-deep-dives/01-data-types-and-structures.md](../15-deep-dives/01-data-types-and-structures.md).
Runnable examples: [15-deep-dives/code/types_and_structures_demo.py](../15-deep-dives/code/types_and_structures_demo.py).

---

## Part 1: data types (one single value)

### `str`: text · Must

```python
company = "PeopleCo GmbH"
domain = "https://www.PeopleCo.de/about".lower().replace("https://", "").replace("www.", "").split("/")[0]
```

- **What it is:** any text, written in quotes.
- **Why it matters here:** company names, domains, emails, countries and industries are all text, and
  half of GTM work is cleaning them so they can be compared and deduplicated.
- **Watch out:** values from a CSV are *always* text, even `"120"`. Strings can't be changed in place:
  `name.strip()` returns a new string, so write `name = name.strip()`.
- **Most-used tools:** `strip()`, `lower()`, `replace()`, `split("@")`, `startswith()`, `in`,
  f-strings `f"{name} has {n} staff"`.

### `int` and `float`: numbers · Must

```python
employees = int("120")      # whole number
score = 87.5                # decimal
wait = 2 ** attempt         # retry backoff: 2, 4, 8, 16...
```

- **What they are:** `int` = whole numbers, `float` = decimals.
- **Why they matter:** employee counts, scores, thresholds, rates, retry wait times.
- **Watch out:** `"120" >= 20` crashes (text vs number). `int("51-200")` and `int("abc")` raise
  `ValueError`, so convert inside `try/except` and decide a rule for ranges (e.g. midpoint 125).
  APIs like HubSpot often send numbers *as strings*.

### `bool`: True / False · Must

```python
raised_recently = True
is_target = country in {"DE", "AT", "CH"} and employees >= 20
```

- **What it is:** one of two values, `True` or `False`. Every comparison produces one.
- **Why it matters:** flags (is_customer, hiring_security) and every scoring and routing rule.
- **Watch out:** Python writes `True`; JSON writes `true` (converted automatically).
  `sum([True, False, True])` is `2`, handy for counting.

### `None` (and pandas `NaN`): missing · Must

```python
owner = None
if owner is None: ...
```

- **What it is:** "there is no value". JSON `null` becomes `None`. In pandas, missing values are `NaN`.
- **Why it matters:** missing data is everywhere: no owner yet, no employee count, no website.
- **Watch out:** `None` is not `0` and not `""`: unknown is different from zero. `NaN` breaks JSON
  ("Out of range float values are not JSON compliant"), so convert NaN to None before calling APIs.
  **Never send blanks to the CRM**: they can erase real values.
- **Truthiness:** in an `if`, `None`, `0`, `""`, `[]`, `{}` all count as False. `if not website:`
  catches both None and empty text.

### `datetime` / `date`: dates and times · Good

```python
from datetime import date, timedelta
recent = date.fromisoformat("2026-11-01") >= date.today() - timedelta(days=90)
```

- **Why it matters:** "funding in the last 90 days", signal decay, speed to lead, `created_at`.
- **Watch out:** APIs send dates as ISO strings (`"2026-11-20T16:40:12Z"`) or epoch milliseconds
  (`1763900000000`): convert them. Prefer UTC.

### Others · Skip for now

`bytes` (only for webhook signatures), `Decimal` (exact money maths), `complex`. You'll recognise them
if you see them; you won't need to write them.

---

## Part 2: data structures (containers for many values)

### `dict`: labelled values · Must (the most important one)

```python
lead = {"name": "PeopleCo", "domain": "peopleco.de", "employees": 120}
lead["owner"] = "lena"                     # add / change
lead.get("country", "unknown")             # safe read: no crash if missing
owner_by_domain = {c["domain"]: c["owner"] for c in crm_rows}   # lookup table
```

- **What it is:** keys (labels) mapped to values, in curly braces. Keys are unique.
- **Why it matters:** **every CSV row and every API response becomes dicts.** Also the fastest way to
  look things up ("is this domain already in the CRM, and who owns it?"), count things and group things.
- **Watch out:** `d["key"]` crashes with `KeyError` if the key is missing; use `d.get("key")`. Keys
  must be immutable (str, int, tuple).

### `list`: an ordered collection · Must

```python
domains = ["peopleco.de", "opal.de"]
domains.append("kitelabs.io")
for i in range(0, len(records), 100):
    batch = records[i:i + 100]             # batches for APIs
```

- **What it is:** items in order, in square brackets. Can repeat, can change.
- **Why it matters:** rows of leads, API results, batches of up to 100 records per API call.
- **Watch out:** `x in a_list` gets slow on big lists (use a set). `lst.sort()` returns `None`
  (use `sorted(lst)` for a new list). Positions start at 0; a position past the end raises
  `IndexError`.

### list of dicts: the shape of real data · Must

```python
leads = [{"name": "PeopleCo", "country": "DE"}, {"name": "Nordbank", "country": "NL"}]
german = [l["name"] for l in leads if l["country"] == "DE"]
```

- **What it is:** a list where each item is a dict (one record).
- **Why it matters:** this is exactly what `csv.DictReader`, `response.json()["results"]` and
  `df.to_dict("records")` give you, and what batch APIs expect.

### `set`: unique values, fast "seen before?" · Must

```python
TARGET_COUNTRIES = {"DE", "AT", "CH", "NL", "BE", "LU"}
brand_new = set(new_domains) - set(crm_domains)
processed = set(); processed.add((event_id, subscription_id))
```

- **What it is:** an unordered collection with no duplicates. Checking `x in s` is instant at any
  size.
- **Why it matters:** deduping, allowed-value checks, new vs existing companies, processing each
  webhook event once.
- **Watch out:** no order and no positions. `{}` is an empty *dict*; an empty set is `set()`. Items
  must be immutable (use tuples, not lists).

### `tuple`: a fixed group of values · Good

```python
def route(lead):
    return "lena", "DACH round-robin"      # returns a tuple
owner, reason = route(lead)                # unpacking
```

- **What it is:** like a list, but can't change once created. Round brackets.
- **Why it matters:** returning two values together (owner + reason), and as keys in sets/dicts
  (e.g. a webhook event key).

### pandas `DataFrame` and `Series`: tables · Must

```python
df = pd.DataFrame(leads)                   # list of dicts -> table
df[df["country"] == "DE"]                  # filter
df.drop_duplicates(subset="domain")        # dedupe
records = df.to_dict(orient="records")     # table -> list of dicts
```

- **What it is:** a DataFrame is a table with named columns; a Series is one column.
- **Why it matters:** cleaning, deduping, scoring, merging with the CRM and reporting on whole lead
  lists at once.
- **Watch out:** numbers read as text show dtype `object`; use `pd.to_numeric(errors="coerce")`. Use
  `&` and `|` (with brackets) in filters, not `and`/`or`.

### Computer-science structures · Skip

Linked lists, trees, graphs, heaps, stacks and queues as algorithm topics aren't tested for GTM
engineering. (A "queue" in GTM talk usually means a message queue for webhooks or leads waiting for a
rep.)

---

## Part 3: which do I use?

| You need to… | Use | Example |
| --- | --- | --- |
| Describe one lead or one API record | `dict` | `{"domain": "peopleco.de", "employees": 120}` |
| Hold many leads in order | `list` (of dicts) | `leads = [ {...}, {...} ]` |
| Send records in batches | `list` slicing | `records[i:i + 100]` |
| Check "is this domain already in the CRM?" | `dict` or `set` | `owner_by_domain.get(domain)` |
| Count leads per country or owner | `dict` / `Counter` | `Counter(countries)` |
| Group leads by owner | `dict` of lists / `defaultdict(list)` | `by_owner[owner].append(lead)` |
| Skip duplicates or processed events | `set` (of tuples) | `if key in processed: continue` |
| New vs existing companies | `set` maths | `new - crm`, `new & crm` |
| Return owner and reason together | `tuple` | `return owner, reason` |
| Clean, dedupe, score, join a whole CSV | `DataFrame` | `df.merge(crm, on="domain", how="left")` |
| Send a DataFrame to an API | `to_dict("records")` with NaN → None | `df.astype(object).where(df.notna(), None)` |

## Part 4: the bugs you'll hit, and the one-line fix

| Symptom | Fix |
| --- | --- |
| `TypeError: '>=' not supported between 'str' and 'int'` | Convert: `int(value)` (safely) |
| `'120' + '5'` gives `'1205'` | Convert to numbers before maths |
| `KeyError: 'country'` | `.get("country")` |
| `AttributeError: 'NoneType' object has no attribute 'lower'` | `(value or "").lower()` |
| `TypeError: unhashable type: 'list'` | Use a tuple as the key |
| The original dict changed by itself | Copy first: `row = dict(row)` |
| `nan is not JSON compliant` | NaN → None, then drop empty fields |
| `int64 is not JSON serializable` | `int(value)` |

## Part 5: speed in one sentence

`x in a_list` checks every item (slow when big); `x in a_set` and `key in a_dict` are instant at any
size. So if you'd search a list inside a loop, build a set or dict once instead.
