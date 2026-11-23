# 1. Design patterns for GTM systems

Four systems cover most of what the role builds. For each: the flow, the key decisions, and how to
explain it.

## Pattern 1: the account pipeline (outbound data layer)

**Goal:** the CRM always has the right companies, clean, deduplicated, enriched and scored.

```
Sources (provider export/API, CRM, signal feeds)
  → extract (paginate, retry, save raw)
  → normalise (domain, country, industry, size)
  → dedupe (normalised domain; survivorship rules)
  → match to existing CRM records (keep owners)
  → enrich gaps (waterfall; only new/stale; record source+date)
  → score fit + intent (with reasons)
  → route (existing owner → territory → round-robin → fallback)
  → batch upsert to CRM (unique key; only owned fields; no blanks)
  → summary log + data-quality checks + alerts
```

**Key decisions to state:** the unique key; who owns which field; how often it runs (nightly full,
hourly incremental); what happens to records that fail.

## Pattern 2: signal-based alerts ("call this account today, because…")

**Goal:** reps act on buying signals within a day, with context.

```
Signal sources (job posts, funding news, website visits, product usage)
  → detect (keywords/regex for cheap filtering; Claude for judgement on text)
  → match signal to an account (domain)
  → dedupe signals (same job post seen twice = one signal)
  → update intent score (with decay)
  → if tier A and not alerted for this signal before:
        alert owner in Slack with who/why now/why fit + a suggested opener
        record "alert sent" (idempotency)
  → measure: alerts → meetings booked
```

**Key decisions:** which signals matter (ask reps and check won deals); alert thresholds (avoid alert
fatigue: daily digest vs instant); decay.

## Pattern 3: inbound scoring and routing (speed to lead)

**Goal:** a demo request reaches the right rep in under a few minutes.

```
Form submitted / demo booked
  → webhook to your endpoint (verify signature, reply 200, queue)
  → normalise email → domain; drop personal/students/competitors (or route separately)
  → match to existing account → existing owner wins
  → enrich quickly (cached) → score
  → route: territory/language → round-robin → fallback; never unassigned
  → create/update CRM records (upsert), set owner, create task
  → Slack the rep with context; escalate if not contacted within X minutes
  → measure speed to lead and meeting rate
```

**Key decisions:** what's "qualified"; SLA (e.g. contact within 15 minutes in working hours);
fallbacks; what happens outside working hours.

## Pattern 4: AI research assistant for AEs ("research to proposals to CRM updates")

**Goal:** AEs walk into demos prepared without spending 30 minutes researching.

```
Trigger: meeting booked (webhook) or every morning for today's meetings
  → gather inputs: website text, recent news, job posts, CRM history, previous call notes
  → Claude: structured brief (what they do, customers, likely framework needed, risks, opener),
     with evidence quotes
  → validate (schema, length, evidence present)
  → write to an ai_brief field / note on the deal; Slack the AE a link
  → feedback button (useful / not useful) → improve prompt
```

**Key decisions:** what the AI may write and where (AI-specific fields only); human review; cost per
brief; measuring usefulness.

## How to answer "How would you build an outbound pipeline from scratch?"

1. **Clarify:** who's the ICP? which tools exist? what volume? what's the success metric?
2. **Start with people:** sit with BDRs, see their current process, where time goes.
3. **Sketch the flow** (pattern 1 + 2) and name the key decisions.
4. **Ship a thin version first** (one source, simple scoring, upsert, one alert) in a week or two.
5. **Measure** (meetings from system-sourced accounts, hours saved) and iterate.
6. **Harden:** retries, monitoring, tests, docs.

## How to answer "How do you prioritise target accounts?"

> "A weighted score: fit from the ICP (industry, size, region, compliance status) plus intent from
> signals (security hiring, funding, enterprise customer announcements, site visits) with decay, as
> 0–100 with reasons. Tier A goes to reps with an alert, B into sequences, C into nurture. I'd validate
> the weights against the last year's won and lost deals and revisit quarterly with the reps."

Next: [02-failure-modes-and-scale.md](02-failure-modes-and-scale.md)
