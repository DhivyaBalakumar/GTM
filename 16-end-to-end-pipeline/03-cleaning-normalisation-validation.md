# Steps 2–3: Map to one schema, clean, normalise, validate, quarantine

**Goal:** turn ten differently-shaped, messy sources into **one table with one schema** where the same
thing is always written the same way, and every row that can't be trusted is set aside with a reason.

Dedupe, scoring and routing all compare values. If one row says `Germany` and another `DE`, or one
says `https://www.PeopleCo.de/about` and another `peopleco.de`, every later step quietly breaks.

## 3.0 Start from zero

**Cleaning** = making data consistent and trustworthy before anyone uses it. It has four parts:

| Part | Plain meaning | Example |
| --- | --- | --- |
| **Mapping** | Rename fields so every source uses the same names | `Work Email` → `email` |
| **Normalising** | Write the same value the same way | `Germany` → `DE` |
| **Deriving** | Work out new fields from existing ones | `CTO` → seniority `c_level`, function `engineering` |
| **Validating** | Check rules; set aside what fails | `max@gmail.com`, title `Student` → quarantine |

**Why it comes before everything else:** computers compare exactly. `"DE" == "Germany"` is `False`.
If you dedupe or score before normalising, two records for the same company look different, and a
German company looks "not in target countries".

**Regular expressions (regex), from zero:** a tiny language for patterns in text.

| Pattern | Means | Matches |
| --- | --- | --- |
| `^` / `$` | start / end of the text | |
| `\d+` | one or more digits | `120` |
| `(\d+)\s*-\s*(\d+)` | digits, optional spaces, dash, digits (two groups) | `51-200`, `51 - 200` |
| `^https?://` | `http://` or `https://` at the start | |
| `\b(cto\|ciso)\b` | the whole word cto or ciso | `CTO`, not `doctor` |
| `[A-Za-z0-9._%+-]+@...` | an email shape | |

```python
import re
re.sub(r"^https?://", "", "https://peopleco.de")       # 'peopleco.de'
re.fullmatch(r"(\d+)\s*-\s*(\d+)", "51-200").groups()   # ('51', '200')
bool(re.search(r"\b(cto|ciso)\b", "cto & co-founder")) # True
```

**Personal vs work vs role email:** `anna@peopleco.de` is a work email (domain = company).
`max@gmail.com` is personal (domain tells you nothing about the employer). `info@corvex.de` is a role
inbox (a shared mailbox, not a person).

## 3.1 Tools

| Tool | Used for | Click or code |
| --- | --- | --- |
| **Python + pandas** | Mapping, normalising, validating at any volume, tested and repeatable | Code |
| **Clay formula / AI columns** | Normalise inside a Clay table (e.g. "clean company name", "domain from URL") | Click (formulas) |
| **Excel / Google Sheets** | `TRIM`, `LOWER`, `PROPER`, `REGEXEXTRACT`, Find & Replace, Text-to-columns | Click |
| **OpenRefine** | Free desktop tool: clustering similar values, facets, bulk edits | Click |
| **Insycle, Dedupely, HubSpot data quality tools** | Bulk-fix formats inside the CRM | Click |
| **`phonenumbers` (Python)** | Parse/format phones to E.164 (`+4930123456`) | Code |
| **`email-validator` (Python)** | Syntax + domain checks for emails | Code |
| **`pycountry`** | Country names ↔ ISO codes | Code |
| **`great_expectations` / `pandera` / `pydantic`** | Declare rules ("email must match", "employees ≥ 0") and fail loudly | Code |
| **dbt tests** | Same idea inside a warehouse (`not_null`, `unique`, `accepted_values`) | Code (SQL) |

## 3.2 The process

1. **Map** each source's fields to the common schema (and keep `source`).
2. **Trim and standardise blanks** (`""`, `"N/A"`, `"-"`, `"null"` → `None`).
3. **Normalise** each field type (domain, email, name, title, country, size, industry, phone, dates).
4. **Derive** helpful fields (domain from work email, first/last name, seniority, function,
   personal vs work email, role inbox).
5. **Validate** with explicit rules; collect *all* problems per row.
6. **Quarantine** failing rows with reasons (don't delete them); pass the rest on.
7. **Measure**: % valid, top failure reasons per source. A source whose failure rate jumps has changed
   format.

## 3.3 Step 1: one schema

| Common field | Apollo API | Clay export | Webinar CSV | HubSpot |
| --- | --- | --- | --- | --- |
| `company` | `organization.name` | `Company Name` | `Organisation` | `properties.name` |
| `website` | `organization.website_url` | `Website` | — | `properties.domain` |
| `first_name` | `first_name` | `First Name` | `Name` (split) | `properties.firstname` |
| `email` | from `bulk_match` | `Work Email` | `Email` | `properties.email` |
| `title` | `title` | `Job Title` | `Job title` | `properties.jobtitle` |
| `country` | `country` | `Country` | `Country` | `properties.country` |
| `employees` | `organization.estimated_num_employees` | `Employee Count` | — | `properties.numberofemployees` (a string!) |

```python
def map_apollo(p):
    org = p.get("organization") or {}            # nested JSON: .get() so missing keys don't crash
    return {"source": "apollo", "company": org.get("name"), "website": org.get("website_url"),
            "first_name": p.get("first_name"), "last_name": p.get("last_name"),
            "email": p.get("email"), "title": p.get("title"), "country": p.get("country"),
            "employees": org.get("estimated_num_employees"), "industry": org.get("industry")}

CLAY_MAP = {"Company Name": "company", "Website": "website", "Work Email": "email",
            "Job Title": "title", "Country": "country", "Employee Count": "employees"}
clay = pd.read_csv("raw/clay.csv", dtype=str).rename(columns=CLAY_MAP).assign(source="clay")
```

## 3.4 Step 2–4: normalise each field type

| Field | Rule | Example in → out |
| --- | --- | --- |
| Domain | lowercase, strip `http(s)://`, `www.`, path, query; from email if no website | `https://www.PeopleCo.de/about` → `peopleco.de` |
| Email | trim, lowercase; validate syntax; flag personal (`gmail.com`) and role (`info@`) | ` Anna@PeopleCo.DE ` → `anna@peopleco.de` |
| Company name | trim; keep the display name; build a separate **match key** without legal suffixes | `PeopleCo GmbH` → key `peopleco` |
| Person name | trim; strip titles (`Dr.`, `Prof.`); split first/last; fix casing carefully (`McDonald`, `Hans-Peter`, `O'Brien`) | `Dr. Eva Brandt` → `Eva` / `Brandt` |
| Country | to ISO-3166 alpha-2 | `Germany`, `Deutschland`, `de` → `DE` |
| Employees | number; ranges → midpoint or min/max; junk → `None` | `51-200` → 125; `abc` → `None` |
| Industry | map provider vocabularies to *your* list | `COMPUTER_SOFTWARE`, `SaaS`, `software` → `software` |
| Title | keep raw; derive `seniority` + `function` | `Head of IT` → `vp_head`, `it` |
| Phone | E.164 with `phonenumbers` | `030 1234567` (DE) → `+49301234567` |
| Dates | ISO 8601 UTC | `27/11/2026` → `2026-11-27` |

```python
import re

def normalise_domain(value):
    if not value or not str(value).strip():
        return None
    v = str(value).strip().lower()
    if "@" in v:
        v = v.split("@")[-1]                          # works for emails too
    v = re.sub(r"^https?://", "", v)
    v = re.sub(r"^www\.", "", v)
    return v.split("/")[0].split("?")[0] or None

COUNTRY = {"germany": "DE", "deutschland": "DE", "austria": "AT", "netherlands": "NL", "uk": "UK"}
def normalise_country(v):
    if not v: return None
    v = v.strip()
    return COUNTRY.get(v.lower(), v.upper() if len(v) == 2 else None)

def parse_employees(v):
    s = str(v or "").replace(",", "").strip()
    if s.isdigit(): return int(s)
    m = re.fullmatch(r"(\d+)\s*-\s*(\d+)", s)
    return (int(m[1]) + int(m[2])) // 2 if m else None
```

Phones:

```python
import phonenumbers
def to_e164(raw, country="DE"):
    try:
        n = phonenumbers.parse(raw, country)
        return phonenumbers.format_number(n, phonenumbers.PhoneNumberFormat.E164) \
            if phonenumbers.is_valid_number(n) else None
    except phonenumbers.NumberParseException:
        return None
```

### Title → seniority and function (order matters)

```python
def classify_title(title):
    t = (title or "").lower()
    if any(w in t for w in ("intern", "student", "trainee")):   # check juniors FIRST,
        seniority = "junior"                                       # or "Engineer Intern" = engineer
    elif re.search(r"\b(ceo|cto|ciso|chief|founder)\b", t) and "product owner" not in t:
        seniority = "c_level"
    elif re.search(r"\b(vp|head of|director)\b", t):
        seniority = "vp_head"
    elif "manager" in t or "lead" in t:
        seniority = "manager"
    else:
        seniority = "ic"
    ...
```

Rules handle 90% of titles. For the long tail (`"Verantwortlicher Informationssicherheit"`,
`"Chief Trust Officer"`), send only the **unclassified** ones to Claude with a fixed list of allowed
answers and validate the reply (module [09](../09-claude-and-ai)). Cache the answer per distinct title.

### The same in pandas (vectorised)

```python
df["domain"] = df["website"].where(df["website"].str.strip() != "", df["email"]).map(normalise_domain)
df["email"] = df["email"].str.strip().str.lower()
df["country"] = df["country"].map(normalise_country)
df["employees"] = df["employees"].map(parse_employees).astype("Int64")   # nullable int
df[["seniority", "function"]] = df["title"].apply(lambda t: pd.Series(classify_title(t)))
df["is_personal"] = df["email"].str.split("@").str[-1].isin(PERSONAL_DOMAINS)
```

## 3.5 Steps 5–6: validate and quarantine

```python
EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+'-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")

def problems(row):
    p = []
    if not row["email"] or not EMAIL_RE.match(row["email"]):   p.append("invalid_email")
    if row["is_personal"] and not row["company"]:              p.append("personal_email_no_company")
    if row["seniority"] == "junior":                           p.append("not_a_buyer")
    if row["employees"] is not None and row["employees"] < 0:  p.append("bad_employee_count")
    return p

df["problems"] = df.apply(problems, axis=1)
quarantine = df[df["problems"].str.len() > 0]
clean = df[df["problems"].str.len() == 0]
quarantine.to_csv("out/quarantine.csv", index=False)      # someone reviews and fixes the source
print(quarantine["problems"].explode().value_counts())    # top reasons, per run
```

With **pydantic** you declare the schema once:

```python
from pydantic import BaseModel, EmailStr, field_validator
class Lead(BaseModel):
    email: EmailStr
    domain: str
    country: str | None = None
    employees: int | None = None
    @field_validator("country")
    @classmethod
    def iso2(cls, v):
        if v and len(v) != 2: raise ValueError("country must be ISO-2")
        return v
```

In the demo: `map_apollo`, `map_file`, `normalise_*`, `parse_employees`, `classify_title`,
`clean_and_validate`. On the sample data it quarantines 2 rows (`max.fischer@gmail.com`: personal
email, no company, freelancer; `sara.lopez@yahoo.com`: personal email, student) and derives Julia
Schmidt's company domain `kranich-logistik.de` from her work email because her row had no website.

## 3.6 Pitfalls

- Normalising the display value instead of keeping a separate match key (you end up showing
  "peopleco" to reps).
- Lower-casing names ("hans-peter") or `.title()`-casing them ("Mcdonald").
- Treating `NaN`, `""` and `"N/A"` as different values.
- Letting pandas guess types (phone numbers become floats: `4.93e+10`).
- Dropping bad rows silently: the source never gets fixed.

## 3.7 Interview lines

> "I map every source into one schema first, then normalise per field type: domain is the most
> important because it's the account key. I keep display values and match keys separate, and bad rows
> go to a quarantine file with reasons, so we can fix the source instead of losing leads."

## 3.8 Summary

- **Map** every source into one schema and keep `source` on every row.
- **Normalise per field type**: domain (most important, it's the account key), email, names, country
  (ISO-2), employees (number), industry (your vocabulary), phone (E.164), dates (ISO).
- **Derive** domain-from-work-email, seniority, function, personal/role flags.
- **Validate** with explicit rules, collect all reasons, **quarantine** instead of deleting.
- Keep display values and match keys separate; measure failure rates per source.

## 3.9 Key functions to remember

| Function | Input → output | Edge cases it handles |
| --- | --- | --- |
| `map_apollo(p)` / `map_file(r)` | source-shaped dict → common schema dict | missing nested `organization` |
| `normalise_domain(v)` | URL/email/domain → `peopleco.de` or `None` | `www.`, `https`, paths, `?query`, emails, blanks |
| `normalise_country(v)` | name/code → ISO-2 | aliases, lowercase codes, unknown → `None` |
| `parse_employees(v)` | `"120"`, `"51-200"`, `"abc"` → `120`, `125`, `None` | commas, ranges, junk |
| `clean_person_name(v)` | `"Dr. Eva"` → `"Eva"` | titles |
| `classify_title(t)` | title → `(seniority, function)` | interns first, "Product Owner" ≠ owner |
| `clean_and_validate(records)` | mapped rows → `(clean, quarantine)` | collects all reasons per row |

## 3.10 Important logic

| Rule | Why |
| --- | --- |
| No website but a **work** email → domain = email domain | Recovers the account key (Julia @ kranich-logistik.de) |
| Personal email **and** no company → quarantine | Can't tie them to an account |
| Junior / student / freelancer → quarantine as `not_a_buyer` | Never a buyer, protects reps' time |
| Check junior keywords **before** role keywords | "Software Engineer Intern" must be junior |
| Unknown country → `None`, not a guess | A wrong value is worse than a blank |
| Never `.title()` names blindly | `McDonald`, `O'Brien`, `Hans-Peter` |

## 3.11 Check yourself

1. Write the domain for: `HTTPS://www.Vektorcloud.NL/de/about?ref=x`.
2. Why quarantine instead of `drop`?
3. Why must the intern check come first in `classify_title`?
4. Pandas read `0049301234` as `49301234.0`. What setting prevents that?

<details><summary>Answers</summary>

1. `vektorcloud.nl`
2. So the source can be fixed and the leads aren't silently lost; you can also measure failure rates.
3. Otherwise "engineer" or "manager" matches first and an intern gets buyer points.
4. `pd.read_csv(..., dtype=str)` (and `keep_default_na=False`).
</details>
