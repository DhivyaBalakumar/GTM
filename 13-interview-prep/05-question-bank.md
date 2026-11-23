# Question bank with model answers

Short model answers to every question type found for GTM-engineer roles, plus the ones this company's
process makes likely. Say them in your own words.

## About you (intro and final)

| Question | Model answer (outline) | More |
| --- | --- | --- |
| Walk me through your background | Degree + CGPA → TechBliss internship → Mathra Marketing and the ConsultKumar outbound system → pipeline projects → "which is exactly this role" | [01-intro-call](01-intro-call.md) |
| Why GTM engineering? | You like turning messy manual processes into systems people use, and seeing the business impact directly | |
| Why Secfix? | First GTM engineer = ownership; a company that sells trust needs trustworthy data; culture doc line; Claude-first; growing after the Series A | |
| Tell me about your Claude experience | Daily Claude Code use with reviewed diffs; Claude in the outbound workflow with fixed output formats; agent skills for consistency | [09-claude-and-ai/03](../09-claude-and-ai/03-claude-code.md) |
| A time you owned something end to end | The outbound workflow → agent skills (STAR) | [04-final-round](04-final-round.md) |
| Something hard you learned quickly | A true example with how you learned and the result | |
| A mistake and how you fixed it | Root cause, fix, prevention | |
| Salary, start date, 9:00–13:00 CET | Within the posted range; a real date; "yes, 1:30–5:30 pm IST" | |

## Python and APIs

| Question | Model answer |
| --- | --- |
| Read a CSV of leads, enrich each via an API, write a new CSV | `csv.DictReader` or pandas → loop with try/except per row → enrich via a retry function, 404 = no data → write with `DictWriter`; log a summary of enriched vs failed |
| Parse this JSON; handle missing values | `.get()` with defaults at every level (`item.get("properties") or {}`), convert numbers in try/except |
| This script creates duplicate CRM records: why? | It creates instead of upserting. Fix: batch upsert by a unique property (or find-then-update); add a test that runs it twice |
| The API sometimes returns 429: add retry logic | Exponential backoff with jitter, respect Retry-After, retry 429/5xx/network only, max 5 tries, then raise and alert |
| It only gets the first 100 results | Missing pagination: loop on `paging.next.after` until absent |
| Dedupe accounts with different spellings | Normalise domains (or name keys); group; keep the most complete; fuzzy matches above a threshold to review |
| Add a scoring rule and a test | Add to config + score function with a reason; a test for the new rule and its boundary |
| Make this safe to run every hour | Idempotent writes (upserts), remembered alerts, logging + summary, alerts on failure, timeouts, a lock so runs don't overlap |
| Receive a webhook and process it once | Verify signature, reply 200 fast, queue, dedupe by event key, then process |
| What's the difference between `params=` and `json=`? | Query string vs JSON body |
| How do you keep API keys safe? | `.env` + `.gitignore`, `.env.example`, secrets managers in CI, rotate if leaked, least-privilege scopes |

## SQL

| Question | Concepts |
| --- | --- |
| Rows where a value is higher than X | `SELECT … WHERE amount > X ORDER BY …` |
| Contacts who opened a sequence but didn't reply, at companies over 100 employees | `JOIN` + `WHERE` on both tables |
| Leads by source per month | `GROUP BY source, SUBSTR(created_at, 1, 7)` |
| Duplicate domains | `GROUP BY LOWER(domain) HAVING COUNT(*) > 1` |
| Accounts with no contacts | `LEFT JOIN … WHERE c.id IS NULL` |
| Meeting rate by source | `100.0 * SUM(meeting_booked) / COUNT(*)` |
| Top account per rep | `ROW_NUMBER() OVER (PARTITION BY owner ORDER BY score DESC)` in a CTE |

All answered and runnable in [05-sql](../05-sql).

## GTM design (Head of GTM)

| Question | Model answer (outline) | More |
| --- | --- | --- |
| How would you build an outbound pipeline from scratch? | Clarify ICP/tools/volume → sit with BDRs → sources → normalise/dedupe → enrich → score fit+intent → route → upsert → alerts → measure → harden | [12-systems-thinking/01](../12-systems-thinking/01-design-patterns.md) |
| How do you prioritise target accounts? | Weighted fit + intent score, 0–100 with reasons, tiers, validated against won/lost deals | [01-gtm-foundations/04](../01-gtm-foundations/04-lead-scoring.md) |
| How would you design inbound scoring and routing? | Webhook → normalise → match existing account → score → route (owner → territory → round-robin → fallback) → Slack → SLA tracking | [01-gtm-foundations/05](../01-gtm-foundations/05-routing.md) |
| How do you measure outbound success? | Reply rate, positive reply rate, meeting rate, pipeline generated, cost per meeting; for your systems: hours saved, adoption | [01-gtm-foundations/07](../01-gtm-foundations/07-metrics.md) |
| Reply rates dropped 30%. What do you check? | Is it real → deliverability (bounces, DNS, volume) → data source → targeting → message → fix one thing at a time | [01-gtm-foundations/06](../01-gtm-foundations/06-outreach-and-sequences.md) |
| Sales says leads are bad; marketing says sales is slow | Shared definitions, conversion by source and speed to lead, fix the system not the blame | [01-gtm-foundations/07](../01-gtm-foundations/07-metrics.md) |
| Five teams want automations. Prioritise | Talk to them, find the root problem, impact × frequency ÷ effort, agree in writing | [12-systems-thinking/03](../12-systems-thinking/03-prioritisation-and-first-90-days.md) |
| AI or a rule? Guardrails for an agent writing to the CRM? | Rules for exact/high-volume; AI for messy text; schema validation, field allow-list, review queue, logging, kill switch | [09-claude-and-ai/02](../09-claude-and-ai/02-prompts-structured-output-guardrails.md) |
| What breaks at 10x? | Rate limits and run time → incremental + batching + caching; cost → AI only after fit rules; bursts → queue; state → persist | [12-systems-thinking/02](../12-systems-thinking/02-failure-modes-and-scale.md) |
| What would you build in your first 30 days? | Listen to every rep, audit CRM data, ship one quick win | [12-systems-thinking/03](../12-systems-thinking/03-prioritisation-and-first-90-days.md) |
| Clay or Python? n8n or code? | No-code for simple glue that ops can change; code for core data logic needing tests, retries, scale | [11-gtm-tools-and-integrations](../11-gtm-tools-and-integrations/README.md) |
| Explain a webhook to a sales rep | The doorbell analogy | |
| What signals would you track for Secfix? | Security/compliance hiring, funding, enterprise/bank/automotive customer announcements, US expansion, NIS2/DORA scope, pricing-page visits; negative: recently certified with a competitor | [01-gtm-foundations/03](../01-gtm-foundations/03-signals-and-intent.md) |
| How would you model buying committees in the CRM? | Contacts associated to the company with role labels (champion, economic buyer, technical evaluator); flag tier-A accounts missing an economic buyer | [07-crm-hubspot/01](../07-crm-hubspot/01-crm-concepts.md) |
| How do you keep the CRM the single source of truth? | Unique keys and upserts, enrichment that fills gaps only, field ownership, routing with fallbacks, quality checks and alerts, documentation | [08-data-quality](../08-data-quality/README.md) |
