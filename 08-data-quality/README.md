# Module 8: Data quality (the heart of GTM engineering)

Most GTM engineering problems are really data problems: messy inputs, duplicates, missing fields,
stale values, and integrations overwriting each other. This module is the thinking; you apply it with
Python and pandas.

| # | File | Covers |
| --- | --- | --- |
| 1 | [01-normalise-validate-dedupe.md](01-normalise-validate-dedupe.md) | ETL, schemas, normalisation, validation, unique keys, deduplication, entity resolution, fuzzy matching, survivorship rules |
| 2 | [02-enrichment-ownership-freshness.md](02-enrichment-ownership-freshness.md) | Enrichment and waterfalls, fill-gaps-only, field ownership, freshness, incremental loads, data-quality checks, GDPR |
| 3 | [entity_resolution.py](entity_resolution.py) | Runnable: exact keys, fuzzy name matching with difflib, survivorship rules, an enrichment waterfall |

```powershell
python 08-data-quality/entity_resolution.py
```
