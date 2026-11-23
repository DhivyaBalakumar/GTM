# 2. Enrichment, field ownership, freshness, checks

## Enrichment

Filling missing facts (employee count, industry, country, funding, tech stack, contact emails and
phone numbers) from a data provider: Apollo, Clay, ZoomInfo, Cognism, Lusha, Clearbit/Breeze, etc.

**Rules:**

1. **Fill gaps only.** If the CRM already has a value (possibly corrected by a rep), keep it.
2. **Never write blanks** from a provider that returned nothing.
3. **Treat 404 / "no match" as normal**, not an error.
4. **Record the source and date** (`employees_source = apollo`, `enriched_at = 2026-11-20`) so you
   know what to trust and when to refresh.
5. **Cost:** most providers charge per credit. Don't re-enrich companies enriched recently; enrich only
   accounts that matter (e.g. above a fit threshold).

## Enrichment waterfall

Try providers in order until one returns a value, field by field. Clay is built around this idea.

```
email for Anna Müller @ peopleco.de:
  provider A → no result
  provider B → anna@peopleco.de (confidence 0.92) ✓ stop
```

Order providers by accuracy for your market (European coverage varies a lot), then cost. Verify emails
before sending (bounces hurt deliverability).

## Field ownership

Every field has **one system allowed to set it**. Without this, integrations fight: the pipeline
overwrites a rep's correction, the rep fixes it, the pipeline overwrites it again.

| Field | Owner | Your pipeline may… |
| --- | --- | --- |
| `name`, `owner`, deal stage | CRM / people | Never overwrite on existing records |
| `fit_score`, `score_reasons`, `tier` | Pipeline | Always write |
| `employees`, `industry` | Provider, unless a human edited it | Fill if empty |
| `last_signal`, `signal_date` | Signal pipeline | Write |

Write the table in your README. It's a strong design-decision answer in interviews.

## Freshness and incremental loads

- Data goes stale: people change jobs (~20–30% of B2B contact data decays per year is a commonly quoted
  range), companies grow, signals expire.
- Store `enriched_at` / `updated_at`; refresh after N days.
- **Incremental loads:** process only records created or changed since the last run (using
  `updatedAt` / a "last run" timestamp) instead of everything every time. Faster, cheaper, gentler on
  rate limits. Keep a periodic full refresh as a safety net.

## Data-quality checks (run after every load)

| Check | Why |
| --- | --- |
| Duplicate domains = 0 | Dedupe and upserts still work |
| % of accounts with industry / size / country / owner filled | Completeness trend |
| Unassigned accounts above tier C = 0 | Routing works |
| Created count on a re-run = 0 | Idempotency |
| Row counts in vs out, dropped count with reasons | Nothing silently lost |
| Values in allowed sets (country codes, tiers) | Normalisation works |

Alert when a check fails or a number jumps (e.g. created count 10× the usual).

## Privacy and GDPR (essential for European B2B)

- Business contact data about people is still **personal data** under GDPR.
- You need a **lawful basis** (B2B outreach usually relies on legitimate interest, with an easy
  opt-out); some countries (e.g. Germany) are stricter about cold email.
- Honour **opt-outs and deletion requests** everywhere (CRM, sequences, warehouse, backups). Keep a
  suppression list your pipeline checks.
- **Minimise:** collect only what you use. Don't put personal data in logs or prompts unnecessarily.
- At a security-compliance company, careful data handling is part of the product's credibility.

Code: [entity_resolution.py](entity_resolution.py)
