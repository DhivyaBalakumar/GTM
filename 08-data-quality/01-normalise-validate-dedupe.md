# 1. Normalise, validate, deduplicate

## ETL: the shape of every pipeline

| Step | Meaning | GTM example |
| --- | --- | --- |
| **Extract** | Get raw data from sources | Read a CSV export; call a data provider's API; page through CRM companies |
| **Transform** | Clean, standardise, combine, score | Normalise domains, dedupe, enrich, score, route |
| **Load** | Write to the destination | Batch upsert into the CRM |

**ELT** is the warehouse variant: load raw data into a warehouse first, transform with SQL there.
**Reverse ETL** pushes cleaned warehouse data back into tools like the CRM.

Always **save raw data before transforming**, so a bug in cleaning can be fixed and re-run without
calling the APIs again.

## Schema: know your fields

A schema says which fields exist, their types, and which are required. Write it down for your
pipeline (even as a table in the README): `domain` (text, required, unique), `employees` (int,
optional), `country` (2-letter ISO code)…

## Normalisation: one consistent format per field

You can't compare or dedupe values until they're in the same format.

| Field | Raw values | Normalised |
| --- | --- | --- |
| Domain | `https://www.PeopleCo.de/about`, `peopleco.de`, `anna@PeopleCo.de` | `peopleco.de` |
| Country | `DE`, `de`, `Germany`, `Deutschland` | `DE` (ISO 3166 alpha-2) |
| Industry | `SaaS`, `software`, `Software Development`, `COMPUTER_SOFTWARE` | `Software` (your own short list, via a mapping) |
| Employees | `120`, `51-200`, `abc`, blank | `120`, `125` (midpoint), `None`, `None` |
| Company name | `PeopleCo GmbH`, `Peopleco`, `PEOPLECO GMBH` | key `peopleco` (lowercase, legal suffix removed) |
| Email | ` Anna@PeopleCo.de ` | `anna@peopleco.de` |
| Phone | `+49 30 1234`, `030-1234` | E.164 `+49301234` (with a library like `phonenumbers`) |
| Dates | `20/11/2026`, `2026-11-20T16:40Z` | ISO `2026-11-20`, UTC |

Keep mappings (industry, country) in config, not scattered through code.

## Validation: reject what isn't usable

Check each record and keep a **"dropped and why"** list (so you can report and fix sources):

- No domain and no work email → no company to match → drop.
- Personal email (gmail.com, yahoo.com, outlook.com, web.de…) → not a company lead → drop or route
  separately.
- Impossible values (employees = -5, a country code that doesn't exist) → set to None and flag.
- Competitors, existing customers, students → exclude from outbound.

## Unique keys: what identifies "the same company"?

| Key | Good | Problems |
| --- | --- | --- |
| **Domain** | Stable, almost unique, available from websites and work emails | Companies with several domains (peopleco.de, peopleco.com); subsidiaries; agencies' shared domains |
| Company name | Always present | Spelled many ways; not unique ("Apex" exists 500 times) |
| Registry ID / provider ID | Truly unique | Not every source has it |
| Email (for contacts) | Unique per person | People change jobs; shared inboxes (info@) |

**Normalised domain is the standard company key**, with a fallback (e.g. normalised name + country)
when there's no domain.

## Deduplication

1. Normalise the key.
2. Group records by key.
3. Keep one per group, choosing the best by a **survivorship rule**.
4. Optionally merge fields from the others (fill gaps).

Survivorship rules (which record or value wins):

| Rule | Example |
| --- | --- |
| Most complete record | The row with the most filled fields |
| Most recent | The latest `updated_at` |
| Most trusted source | CRM (human-edited) > paid provider > scraped |
| Per field | Name from the CRM, employees from the provider, owner from the CRM |

"Sort so the best is first, then keep first" is the standard implementation (in pandas:
`sort_values(...).drop_duplicates(subset="domain", keep="first")`).

## Entity resolution: harder matching

Deciding which records refer to the same real company when keys don't match exactly:

- **Multiple domains:** peopleco.de and peopleco.com. Keep a mapping table of alternate domains.
- **Rebrands and acquisitions.**
- **Subsidiaries:** PeopleCo Austria GmbH (peopleco.at) vs PeopleCo GmbH. Same company or not? It's a
  business decision (often: separate accounts linked by a "parent company" association).
- **Fuzzy names:** "Nordbank Tech B.V." vs "Nordbank Technologies". Use a similarity score (Python's
  `difflib`, or `rapidfuzz`), plus a second signal such as the same country or city, and send
  borderline matches to a human review list rather than merging automatically.

Merging wrongly is worse than not merging: a false merge mixes two customers' data. Be conservative.

## Interview phrasing

> "I dedupe on normalised domain: lowercase, no protocol, no www, no path, falling back to the
> work-email domain, with personal domains excluded. When duplicates collide I keep the most complete
> record and fill gaps from the others, with the CRM winning for human-edited fields like owner. Fuzzy
> name matches above a threshold go to a review list instead of auto-merging, because a wrong merge is
> worse than a duplicate."

Next: [02-enrichment-ownership-freshness.md](02-enrichment-ownership-freshness.md)
