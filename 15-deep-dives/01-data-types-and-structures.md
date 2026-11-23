# Deep dive 1: Python data types and data structures

This guide explains, from zero, the difference between data types and data structures, every type and
structure you need, *why* each one matters in GTM engineering, the mistakes beginners make, and how to
choose the right one. Every example uses the kind of data you'll handle at Secfix: leads, companies,
domains, owners, API responses.

Run the examples as you read: [code/types_and_structures_demo.py](code/types_and_structures_demo.py).
One-page summary: [14-cheatsheets/data-types-and-structures.md](../14-cheatsheets/data-types-and-structures.md).

---

## 1. The difference in one minute

A **data type** is what kind of *single value* something is. A **data structure** is a *container*
that holds and organises many values.

| | Data type | Data structure |
| --- | --- | --- |
| What it is | One value and what kind it is | A way to hold and organise many values |
| Examples | `"PeopleCo"` (str), `120` (int), `87.5` (float), `True` (bool), `None` | list `[...]`, tuple `(...)`, dict `{key: value}`, set `{...}`, pandas DataFrame |
| Question it answers | "Is this text or a number? Is it missing?" | "How do I store 500 leads and find one quickly?" |
| GTM example | `employees = 120` | `lead = {"name": "PeopleCo", "employees": 120}` |

**Analogy.** Data types are the *items*: a book, a coin, a key. Data structures are the *furniture*
that holds them:

- a **shelf** where things stay in order → **list**
- a **sealed box** you can't change once packed → **tuple**
- a **labelled filing cabinet** where you find a folder by its label → **dict**
- a **bag that refuses duplicates** → **set**
- a **spreadsheet** → **DataFrame**

They always work together. One CSV row is a **dict** (a structure) whose values are **str and int**
(types). A whole lead list is a **list of dicts**.

```python
lead = {                       # dict: a data structure
    "name": "PeopleCo GmbH",   # str: a data type
    "employees": 120,          # int
    "score": 87.5,             # float
    "is_customer": False,      # bool
    "owner": None,             # NoneType: "missing"
    "tags": ["software", "dach"],   # a list inside the dict: a structure inside a structure
}
```

Technically, list, dict and set are also "types" in Python (`type([])` prints `list`), but it helps
to think of them separately: **simple values** vs **containers**.

**Why this matters for the job:** almost every bug in a beginner's GTM script is either a *type*
problem ("120" is text, not a number; a value is None) or a *structure* problem (looking something up
in a list instead of a dict; a dict key that doesn't exist). Knowing both well removes most of your
debugging.

---

## 2. Data types in detail

Five types cover almost everything in GTM work.

| Type | What it holds | Examples | GTM use |
| --- | --- | --- | --- |
| `str` (string) | Text | `"PeopleCo"`, `"anna@peopleco.de"`, `"120"` | Names, domains, emails, countries, industries |
| `int` (integer) | Whole numbers | `120`, `0`, `-5` | Employee counts, scores, counts of leads |
| `float` | Decimal numbers | `87.5`, `0.93`, `1.5` | Averages, rates, AI confidence, wait times |
| `bool` (boolean) | `True` or `False` | `True`, `False` | Flags: is_customer, raised_recently, hiring_security |
| `NoneType` | Only the value `None`: "nothing / missing" | `None` | A field with no value: no owner yet, unknown size |

### 2.1 `str`: text

**What it is.** Any text, written in quotes: `"PeopleCo"` or `'PeopleCo'` (same thing).

**Key facts.**

- **Immutable:** a string can't be changed in place. Methods return a *new* string, so you must save
  the result: `name = name.strip()`. Writing just `name.strip()` does nothing useful.
- A number written in quotes is still text: `"120"` is a str, not an int.
- Strings can be indexed and sliced: `s[0]` (first character), `s[-1]` (last), `s[0:5]` (characters 0
  to 4; the end position is excluded).

**The methods you'll use constantly.**

| Method | Does | Example → result |
| --- | --- | --- |
| `strip()` | Remove spaces at both ends | `"  PeopleCo  ".strip()` → `"PeopleCo"` |
| `lower()` / `upper()` | Change case | `"PeopleCo.DE".lower()` → `"peopleco.de"` |
| `replace(a, b)` | Replace text | `"www.x.de".replace("www.", "")` → `"x.de"` |
| `split(sep)` | Cut into a list | `"anna@peopleco.de".split("@")` → `["anna", "peopleco.de"]` |
| `join(list)` | Glue a list into text | `", ".join(["a", "b"])` → `"a, b"` |
| `startswith()` / `endswith()` | Check start/end | `"https://x".startswith("http")` → `True` |
| `in` | Contains? | `"@" in "anna@x.de"` → `True` |
| f-string | Insert values | `f"{name} has {n} staff"` |

**A real cleaning example.**

```python
website = "  HTTPS://www.PeopleCo.de/about  "
domain = website.strip().lower().replace("https://", "").replace("www.", "").split("/")[0]
# 'peopleco.de'
```

Read it left to right: remove spaces → lowercase → remove the protocol → remove `www.` → cut at the
first `/` and keep the first piece. Each step returns a new string that the next step works on.

**Why it matters for the job:** the same company arrives as `https://www.PeopleCo.de/about`,
`peopleco.de` and `anna@PeopleCo.de`. Until you normalise the text, your code thinks these are three
companies, and the CRM gets duplicates.

### 2.2 `int` and `float`: numbers

**What they are.** `int` for whole numbers, `float` for decimals.

**Key facts.**

- Dividing with `/` always gives a float: `10 / 2` is `5.0`. `//` gives a whole number: `7 // 2` is 3.
- `%` is the remainder: `7 % 2` is 1. `**` is power: `2 ** 3` is 8 (used for retry waits: 1, 2, 4, 8
  seconds).
- `round(72.456, 1)` gives `72.5`. `int(72.9)` gives `72`: it *cuts*, it doesn't round.
- Floats can be slightly imprecise: `0.1 + 0.2` is `0.30000000000000004`. Fine for scores; for money,
  round when displaying.

**Why they matter for the job:** employee thresholds (20–500), scores (0–100), tiers (A ≥ 75),
conversion rates, retry backoff, batch sizes.

### 2.3 `bool`: True or False

**What it is.** One of exactly two values. Every comparison produces one: `120 >= 20` is `True`;
`"DE" == "NL"` is `False`.

**Key facts.**

- Combine with `and`, `or`, `not`.
- Capital letters in Python: `True`, `False`. JSON writes `true`/`false`; Python converts them for you.
- Bools behave like 1 and 0 in maths: `sum([True, False, True])` is `2`, a quick way to count how many
  leads match a rule.

**Why it matters for the job:** every scoring, routing and filtering rule is a set of bool conditions.

### 2.4 `None`: "there is no value"

**What it is.** The single value meaning *missing or unknown*: a company with no owner yet, an API
field that wasn't returned. JSON's `null` becomes `None` in Python.

**Key facts.**

- Check with `is None`, not `== None`.
- `None` is **not** `0` and **not** `""`. "Zero employees" and "we don't know how many employees" are
  different facts and must be handled differently (unknown → enrich it; zero → probably invalid).
- Calling a method on `None` crashes: `None.lower()` → `AttributeError: 'NoneType' object has no
  attribute 'lower'`. Guard with `if value:` or `(value or "").lower()`.

### 2.5 Other types you'll meet

| Type | What | Where in GTM work |
| --- | --- | --- |
| `datetime`, `date` | Dates and times | Signal dates, `created_at`, "in the last 90 days", speed to lead |
| `bytes` | Raw binary data | Webhook signature checks |
| `Decimal` | Exact decimal maths | Money, if precision matters |
| numpy `int64`, `float64` | pandas' number types | Values from a DataFrame; convert with `int()` before JSON |

---

## 3. Checking and converting types

### 3.1 The most common GTM bug

A CSV gives you **every value as text**. `"120"` looks like a number, but it's a str, so maths and
comparisons go wrong until you convert it.

```python
employees = "120"          # from a CSV: a str
employees + "5"            # '1205'  (joins text!)
employees >= 20            # TypeError: '>=' not supported between 'str' and 'int'
int(employees) >= 20       # True
```

### 3.2 Checking a type

```python
type(120)                       # <class 'int'>
isinstance(120, int)            # True: the usual way to check in code
isinstance(87.5, (int, float))  # True: "is it any kind of number?"
```

Use `print(type(x), x)` whenever something behaves strangely. It's the fastest debugging tool.

### 3.3 Converting

| From → to | Code | Result | Fails when |
| --- | --- | --- | --- |
| str → int | `int("120")` | `120` | `int("abc")`, `int("51-200")`, `int("12.5")` → ValueError |
| str → float | `float("87.5")` | `87.5` | `float("abc")` → ValueError |
| number → str | `str(120)` | `"120"` | Never |
| float → int | `int(72.9)` | `72` (cuts) | Never (use `round()` to round) |
| anything → bool | `bool("x")`, `bool(0)` | `True`, `False` | Never (see truthiness) |
| None → int | `int(None)` | — | Always: TypeError |

### 3.4 Converting safely (real data is messy)

```python
def safe_int(value, default=None):
    try:
        return int(value)
    except (TypeError, ValueError):     # None -> TypeError, "abc" -> ValueError
        return default

safe_int("120")   # 120
safe_int("abc")   # None
safe_int(None, 0) # 0
```

Ranges like `"51-200"` need their own rule. A common choice is the midpoint (125). Decide it, write it
in your README, and test it.

### 3.5 Types from APIs

- JSON has strings, numbers, true/false, null, arrays and objects. They become str, int/float, bool,
  None, list and dict.
- Many APIs (HubSpot included) return numbers **as strings**: `"numberofemployees": "120"`. Convert
  before comparing.
- When you **send** data, HubSpot expects property values as strings, so `str(120)` before upserting.
- pandas numbers are numpy types (`numpy.int64`). `json.dumps` can't handle them: convert with
  `int()` / `float()` first.

---

## 4. Missing values: None, empty strings, truthiness and NaN

Missing data appears in four forms, and each behaves differently.

| Form | Where it comes from | How to check |
| --- | --- | --- |
| `None` | Python code, JSON `null`, `.get()` on a missing key | `x is None` |
| `""` (empty string) | Empty CSV cells read with `csv`, blank form fields | `x == ""` or `not x.strip()` |
| `NaN` | Empty or unparseable cells in pandas | `pd.isna(x)` (never `x == np.nan`: NaN isn't even equal to itself) |
| Missing key | A dict that never had the field | `"key" in d`, or `d.get("key")` returns None |

### 4.1 Truthiness: what counts as False

In an `if`, these all behave like **False**: `None`, `0`, `0.0`, `""`, `[]`, `{}`, `set()`. Everything
else is **True**, including `"False"`, `" "` and `[0]`.

```python
if not website:          # catches None AND "" in one check
    website = email_domain
```

**The trap:** `if not employees:` is also True when employees is `0`. If 0 is a real value, check
`if employees is None:` instead.

### 4.2 NaN in pandas

- pandas puts `NaN` ("not a number") wherever data is missing, even in text columns.
- `df["col"].isna()` finds them; `fillna(...)` fills them; `dropna(subset=[...])` drops rows.
- **NaN is not valid JSON.** Sending a record containing NaN to an API raises "Out of range float
  values are not JSON compliant: nan". Convert first:

```python
records = df.astype(object).where(df.notna(), None).to_dict(orient="records")   # NaN -> None
records = [{k: v for k, v in r.items() if v is not None} for r in records]       # then drop blanks
```

### 4.3 Why missing values matter so much in GTM

- **Never write blanks to the CRM.** Sending `""` or `None` can erase a value a rep typed in. Strip
  missing values before sending.
- **Unknown is not zero.** `employees = None` (needs enrichment) is different from `employees = 0`.
- **Report what's missing.** Count missing fields after every run; it's a data-quality metric the GTM
  team cares about ("how complete is our CRM?").

---

## 5. Mutable vs immutable, and the copy trap

**Mutable** means it can be changed in place. **Immutable** means it can't: any "change" creates a new
value.

| Immutable (can't change) | Mutable (can change) |
| --- | --- |
| `str`, `int`, `float`, `bool`, `None`, `tuple` | `list`, `dict`, `set`, pandas DataFrame |

```python
name = "peopleco"
name.upper()          # returns 'PEOPLECO' but name is unchanged
name = name.upper()   # you must save it

leads = ["a.de"]
leads.append("b.de")  # changes the list itself; no need to reassign
```

### 5.1 The copy trap

Assigning a mutable object to a new name does **not** copy it. Both names point to the *same* object.

```python
original = {"name": "PeopleCo", "score": 80}
updated = original          # NOT a copy: a second label on the same dict
updated["score"] = 95
print(original["score"])    # 95: the original changed too!

safe = dict(original)       # a real copy (also: original.copy())
safe["score"] = 50          # original unaffected
```

The same happens when you pass a dict or list into a function: changes inside the function affect the
caller's object. Good pipeline habit: copy a record before changing it (`row = dict(row)`), so the raw
input stays intact and you can always compare before/after.

For nested structures (a dict containing lists), `.copy()` is *shallow*: the inner lists are still
shared. Use `copy.deepcopy(obj)` when you need a full, independent copy.

### 5.2 Why only immutable things can be dict keys or set items

Dict keys and set items must be **hashable** (unchangeable), so `str`, `int` and `tuple` work, but
`list` and `dict` don't. That's why a webhook event key is the tuple `(event_id, subscription_id,
occurred_at)`, not a list.

---

## 6. Lists and tuples

### 6.1 `list`: an ordered, changeable collection

Written with square brackets. Items keep their order, can repeat, and can be any type.

**Use for:** rows of leads, a list of domains, a batch of records, API results.

| Operation | Code | Result / note |
| --- | --- | --- |
| Create | `domains = ["a.de", "b.nl"]` | |
| Read by position | `domains[0]`, `domains[-1]` | First, last (positions start at 0) |
| Length | `len(domains)` | 2 |
| Add one / many | `domains.append("c.io")`, `domains.extend([...])` | Changes the list |
| Insert at a position | `domains.insert(0, "x.de")` | |
| Remove by value / last | `domains.remove("a.de")`, `domains.pop()` | `pop` returns the removed item |
| Membership | `"a.de" in domains` | True/False (slow on huge lists) |
| Slice | `domains[0:10]`, `domains[-3:]` | A new list; end position excluded |
| Sort | `sorted(domains)` (new list), `domains.sort()` (in place) | `reverse=True` for biggest first |
| Loop | `for d in domains:` / `for i, d in enumerate(domains):` | |
| Build from a loop | `[d.lower() for d in domains if d]` | A list comprehension |
| Min, max, sum | `max(scores)`, `sum(scores)` | Numbers only |

**Batching** (APIs accept at most N records per call) is just slicing in a loop:

```python
for i in range(0, len(records), 100):
    batch = records[i:i + 100]        # positions 0-99, then 100-199, ...
    send(batch)
```

With 230 records this sends batches of 100, 100 and 30. This exact loop is how you write to HubSpot's
batch endpoints.

**Common errors:** `IndexError` (a position that doesn't exist), and `.sort()` returning `None`
(`x = lst.sort()` makes `x` None; use `x = sorted(lst)`).

### 6.2 `tuple`: an ordered, unchangeable collection

Written with round brackets. Like a list, but fixed once created.

**Use for:** values that belong together and shouldn't change, returning several values from a
function, and keys in sets or dicts.

```python
pair = ("lena", "existing owner")
owner, reason = pair                  # unpacking: one variable per item

def route(lead):
    return "lena", "DACH round-robin"   # the comma makes a tuple

owner, reason = route(lead)

event_key = (101, 9001, 1763900000000)  # hashable: can go in a set
```

| list | tuple |
| --- | --- |
| `[1, 2, 3]` | `(1, 2, 3)` |
| Mutable: append, remove, sort | Immutable |
| A collection of similar things (many leads) | A fixed group of related values (owner + reason) |
| Can't be a dict key or set item | Can be |

---

## 7. Dictionaries (dict): the most important structure for GTM work

A dict maps **keys** (labels) to **values**, written with curly braces: `{key: value}`. Keys are
unique, and looking up by key is instant even with millions of entries. **Every CSV row and every API
response becomes dicts.**

| Operation | Code | Note |
| --- | --- | --- |
| Create | `lead = {"name": "PeopleCo", "employees": 120}` | |
| Read | `lead["name"]` | `KeyError` if the key is missing |
| Read safely | `lead.get("country")`, `lead.get("country", "unknown")` | `None` or your default if missing |
| Add / change | `lead["country"] = "DE"` | Same syntax for both |
| Add / change several | `lead.update({"tier": "A", "owner": "lena"})` | |
| Remove | `del lead["owner"]`, `lead.pop("owner", None)` | |
| Check a key | `"owner" in lead` | Checks keys, not values |
| Loop | `for key, value in lead.items():` | Also `.keys()`, `.values()` |
| Count entries | `len(lead)` | |
| Copy | `dict(lead)` or `lead.copy()` | See the copy trap |
| Build from a loop | `{c["domain"]: c for c in companies}` | A dict comprehension |

Since Python 3.7, dicts remember the order keys were inserted.

### Pattern 1: a lookup table ("is this already in the CRM?")

```python
crm = [{"domain": "peopleco.de", "owner": "lena"}, {"domain": "nordbanktech.nl", "owner": "tom"}]
owner_by_domain = {c["domain"]: c["owner"] for c in crm}   # build once

owner_by_domain.get("peopleco.de")   # 'lena': instant lookup
owner_by_domain.get("newco.io")      # None: not in the CRM yet
```

**Why this matters:** routing's first rule is "keep the existing owner". With 20,000 CRM companies and
2,000 new leads, searching a list for every lead means 40 million comparisons; building the dict once
makes each check instant.

### Pattern 2: counting

```python
counts = {}
for country in ["DE", "NL", "DE"]:
    counts[country] = counts.get(country, 0) + 1     # {'DE': 2, 'NL': 1}

from collections import Counter
Counter(["DE", "NL", "DE"]).most_common(1)          # [('DE', 2)]
```

`counts.get(country, 0)` means "the current count, or 0 if this country hasn't appeared yet".

### Pattern 3: grouping

```python
by_owner = {}
for lead in leads:
    by_owner.setdefault(lead["owner"], []).append(lead)   # create the list if new, then add

from collections import defaultdict
by_owner = defaultdict(list)       # missing keys start as an empty list automatically
```

### Pattern 4: dedupe, keeping the best record

```python
best = {}
for row in rows:
    key = row["domain"]
    filled = sum(1 for v in row.values() if v not in (None, ""))   # how complete is this row?
    if key not in best or filled > best[key][0]:
        best[key] = (filled, row)
unique = [row for _, row in best.values()]
```

The dict holds one entry per domain; a row replaces the stored one only if it's more complete. This is
the core of "deduplicate" in the job post.

### Pattern 5: config and mappings

```python
COUNTRY = {"germany": "DE", "netherlands": "NL"}
COUNTRY.get("Germany".lower(), "")     # 'DE'
```

Keys must be immutable (str, int, tuple). Values can be anything, including lists and other dicts.

---

## 8. Sets: unique values and fast "have I seen this?"

A set is an unordered collection with **no duplicates**, written `{"a", "b"}` or created with `set()`.
(Careful: `{}` alone is an empty *dict*.) Checking `x in my_set` is instant even with millions of items.

**Use for:** deduping, skipping already-processed items, allowed-value lists, comparing two lists.

| Operation | Code | Result |
| --- | --- | --- |
| Create | `s = set()`, `{"DE", "AT", "CH"}` | |
| From a list (dedupes) | `set(["a", "b", "a"])` | `{'a', 'b'}` |
| Add | `s.add("NL")` | Adding an existing item does nothing |
| Remove | `s.discard("NL")` | No error if missing |
| Membership | `"DE" in s` | Instant |
| Count unique | `len(set(domains))` | |
| In both | `a & b` | Intersection |
| In either | `a \| b` | Union |
| In a but not b | `a - b` | Difference |

### GTM patterns

```python
# 1. Allowed values (fast checks)
TARGET_COUNTRIES = {"DE", "AT", "CH", "NL", "BE", "LU"}
PERSONAL_DOMAINS = {"gmail.com", "yahoo.com", "outlook.com"}
if domain in PERSONAL_DOMAINS: ...

# 2. New vs existing companies
crm = {"peopleco.de", "opal.de"}
new_list = {"peopleco.de", "kitelabs.io"}
brand_new = new_list - crm          # {'kitelabs.io'}
already_in_crm = new_list & crm     # {'peopleco.de'}

# 3. Process each webhook event once (senders retry, so duplicates happen)
processed = set()
for event in events:
    key = (event["eventId"], event["subscriptionId"], event["occurredAt"])   # a tuple: hashable
    if key in processed:
        continue
    processed.add(key)
    handle(event)
```

Sets have no order and no positions (`s[0]` is an error). If you need order, sort: `sorted(s)`. Items
must be immutable (str, int, tuple; not lists or dicts).

---

## 9. Nested data: how API responses look

Real data is structures inside structures. A typical CRM API response is a **dict** containing a
**list** of **dicts**, each with another **dict** inside:

```python
response = {
    "results": [                                   # list of records
        {"id": "1", "properties": {"name": "PeopleCo", "numberofemployees": "120"}},
        {"id": "2", "properties": {"name": "Nordbank"}},     # no employee count
        {"id": "3", "properties": None},                      # properties missing entirely
    ],
    "paging": {"next": {"after": "3"}},             # dict in a dict in a dict
}
```

### 9.1 Reading it step by step

```python
response["results"]                              # the list
response["results"][0]                           # the first record (a dict)
response["results"][0]["properties"]["name"]     # 'PeopleCo'
```

Read the path left to right: `["results"]` (dict key) → `[0]` (list position) → `["properties"]`
(dict key) → `["name"]` (dict key). Square brackets with a string = dict key; with a number = list
position.

### 9.2 Reading it safely (real APIs leave things out)

```python
for item in response.get("results", []):          # [] if there are no results
    props = item.get("properties") or {}           # {} if missing OR None
    name = props.get("name", "")
    try:
        employees = int(props.get("numberofemployees") or 0)
    except ValueError:
        employees = 0
    print(name, employees)

next_cursor = response.get("paging", {}).get("next", {}).get("after")   # None when there's no next page
```

Two rules: use `.get()` with a sensible default at every level, and use `or {}` / `or []` when a value
might be `None` rather than missing (`.get("properties", {})` still returns `None` if the key exists
with value `None`).

### 9.3 Building nested data to send

```python
body = {"inputs": [
    {"idProperty": "company_domain_key", "id": "peopleco.de",
     "properties": {"name": "PeopleCo GmbH", "fit_score": "95"}},
]}
requests.post(url, json=body, headers=headers, timeout=10)   # json= converts it for you
```

### 9.4 Flattening: nested → flat rows (for pandas or CSV)

```python
rows = [{"id": item["id"], **(item.get("properties") or {})} for item in response["results"]]
# [{'id': '1', 'name': 'PeopleCo', 'numberofemployees': '120'}, {'id': '2', 'name': 'Nordbank'}, {'id': '3'}]
```

`**some_dict` spreads a dict's keys into a new dict. `pd.json_normalize(response["results"])` does the
same in pandas, producing columns like `properties.name`.

**Tip:** when you meet unfamiliar JSON, print it nicely first: `print(json.dumps(response, indent=2))`.

---

## 10. pandas: Series and DataFrame

pandas adds two structures for working with tables.

| Structure | What it is | Think of it as |
| --- | --- | --- |
| **Series** | One column: values plus an index (row labels) | A list with labels, or one spreadsheet column |
| **DataFrame** | A table: many Series sharing an index | A spreadsheet, or a list of dicts with the same keys |

```python
import pandas as pd

leads = [{"name": "PeopleCo", "employees": 120}, {"name": "Opal", "employees": 25}]
df = pd.DataFrame(leads)          # list of dicts -> DataFrame
df["employees"]                   # a Series (one column)
df.to_dict(orient="records")      # DataFrame -> list of dicts (what APIs want)
```

### 10.1 Each column has a dtype (data type)

| pandas dtype | Python equivalent | Note |
| --- | --- | --- |
| `int64` | int | Can't hold missing values; becomes `float64` if any NaN appears |
| `float64` | float | Missing numbers are `NaN` |
| `object` / `str` | str (or mixed) | Text, or columns pandas couldn't make numeric |
| `bool` | bool | |
| `datetime64` | datetime | From `parse_dates=` or `pd.to_datetime` |

Check with `df.dtypes` or `df.info()`. A column you expected to be numbers showing as `object` usually
means some values are text (`"51-200"`, `"abc"`). Convert deliberately:
`pd.to_numeric(df["employees"], errors="coerce")` turns bad values into NaN instead of crashing.

### 10.2 List/dict thinking vs pandas thinking

| Task | Plain Python | pandas |
| --- | --- | --- |
| Filter | `[r for r in rows if r["country"] == "DE"]` | `df[df["country"] == "DE"]` |
| New field | loop and set `r["score"] = ...` | `df["score"] = df["x"].apply(fn)` |
| Count per value | dict or `Counter` | `df["country"].value_counts()` |
| Dedupe | dict keyed by domain | `df.drop_duplicates(subset="domain")` |
| Lookup / join | dict lookup | `df.merge(other, on="domain", how="left")` |

Use plain structures for small, record-by-record logic (API calls, routing one lead, webhooks). Use
pandas for whole-table work (cleaning, deduping, grouping, joining). Many pipelines use both: pandas to
clean, then `to_dict("records")` and a loop to send.

---

## 11. Choosing the right structure

| You need to… | Use | Example |
| --- | --- | --- |
| Keep items in order, maybe with repeats | **list** | Rows of leads, a batch to send |
| Group a few fixed values together | **tuple** | `(owner, reason)`, `(event_id, subscription_id)` |
| Describe one record with named fields | **dict** | One lead, one API response |
| Look something up by a key, fast | **dict** | Owner by domain, country code by name |
| Count or group things | **dict** / `Counter` / `defaultdict` | Leads per country, accounts per owner |
| Keep only unique values / check "seen before?" fast | **set** | Processed webhook events, allowed countries |
| Compare two collections | **set** maths | New domains vs CRM domains |
| Work on a whole table | **DataFrame** | Clean, dedupe, group, join a CSV |

### Speed, in three sentences

- Checking `x in a_list` gets slower as the list grows (it checks every item).
- Checking `x in a_set` or `key in a_dict` stays instant no matter the size.
- So whenever you'd search a list inside a loop, build a set or dict once instead. That's the only
  "Big-O" you need for this role.

### What to skip for this role

Computer-science data structures (linked lists, trees, graphs, heaps, stacks and queues as algorithm
topics) and algorithm puzzles aren't tested for GTM engineering. If someone mentions a "queue" in a GTM
context, they usually mean a message queue for webhooks or a list of leads waiting for a rep.

---

## 12. Common bugs and practice questions

### 12.1 The bugs you'll actually hit

| Error / symptom | Cause | Fix |
| --- | --- | --- |
| `TypeError: '>=' not supported between 'str' and 'int'` | Comparing CSV text to a number | `int(value)` first (safely) |
| `'120' + '5'` gives `'1205'` | Adding strings | Convert to numbers |
| `ValueError: invalid literal for int()` | `int("abc")` or `int("51-200")` | try/except; a rule for ranges |
| `KeyError: 'country'` | Reading a missing dict key with `[]` | `.get("country")` |
| `IndexError: list index out of range` | A position past the end | Check `len()`; loop instead of indexing |
| `AttributeError: 'NoneType' object has no attribute 'lower'` | Calling a method on `None` | `if value:` first, or `(value or "").lower()` |
| `TypeError: unhashable type: 'list'` | A list as a dict key or set item | Use a tuple |
| Original data changed unexpectedly | Two names, one mutable object | `dict(row)` / `.copy()` |
| "Out of range float values are not JSON compliant: nan" | pandas NaN sent to an API | Convert NaN to None and drop blanks |
| "Object of type int64 is not JSON serializable" | numpy number sent to `json.dumps` | `int(value)` |
| `.sort()` returned `None` | `sort()` works in place | Use `sorted(lst)` for a new list |
| `{}` used as an empty set | `{}` is an empty dict | `set()` |

### 12.2 Practice questions (answer first, then check)

1. What type is each: `"45"`, `45`, `45.0`, `False`, `None`, `[45]`, `{"n": 45}`?
2. Why does `"120" >= 20` fail, and how do you fix it?
3. Which of these are False in an `if`: `0`, `"0"`, `""`, `" "`, `None`, `[]`, `[None]`?
4. You need to check 50,000 domains against 200,000 CRM domains. List or set for the CRM domains? Why?
5. Write a dict comprehension mapping each domain to its owner from `crm = [{"domain": "a.de", "owner": "lena"}]`.
6. How do you safely get the `after` cursor from `{"results": []}` without an error?
7. Why is a webhook event key a tuple and not a list?
8. What does `b = a; b.append(4)` do to `a` if `a = [1, 2, 3]`?
9. Count leads per country from `["DE", "NL", "DE"]` two ways.
10. Find domains in `new` but not in `crm`, both sets, in one expression.

<details><summary>Answers</summary>

1. str, int, float, bool, NoneType, list, dict.
2. You're comparing text to a number; convert with `int("120")` (wrapped in try/except for messy data).
3. `0`, `""`, `None`, `[]` are False. `"0"`, `" "` and `[None]` are True (non-empty).
4. A set: membership checks stay instant; with a list each check scans up to 200,000 items.
5. `{c["domain"]: c["owner"] for c in crm}`
6. `data.get("paging", {}).get("next", {}).get("after")` returns None.
7. Set items and dict keys must be immutable (hashable); tuples are, lists aren't.
8. `a` becomes `[1, 2, 3, 4]`: both names point to the same list.
9. A dict loop with `counts[c] = counts.get(c, 0) + 1`, or `Counter([...])`.
10. `new - crm`

</details>

### 12.3 Practise in code

Run [code/types_and_structures_demo.py](code/types_and_structures_demo.py), then Python lessons 01, 03
and 04 in [03-python/lessons](../03-python/lessons), then exercises `ex01_strings.py` and
`ex02_collections.py` in [03-python/exercises](../03-python/exercises).
