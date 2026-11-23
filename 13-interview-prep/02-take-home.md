# Round 2: the take-home (8–10 hours of work, 7 days)

## What it tests

Whether you can build a small, working, reliable GTM system and explain it. It mirrors the job: "pull
data from multiple sources, deduplicate, score and write it back", "scheduled jobs, error handling",
AI workflows. The next round will dig into your code, so understand every line.

## Likely shapes

1. **Account pipeline:** 2–3 sources (a CSV plus an API) → normalise → dedupe → score against an ICP →
   write to a CRM or database, safe to re-run.
2. **Signal alerts:** given events (funding, hiring, web visits), decide which accounts a rep should
   call today and why; send alerts.
3. **AI workflow for AEs:** Claude researches an account and drafts a brief or email, with guardrails.
4. **Inbound routing:** score and assign incoming leads with rules and a fallback.

## A 7-day plan

| Day | Do |
| --- | --- |
| 1 | Read the brief twice. List assumptions and questions; email the questions (including "are AI tools allowed?"). Sketch the design on paper. Set up the repo: README skeleton, `.gitignore`, `.env.example`, `requirements.txt` |
| 2–3 | Build the **simplest version that works end to end**, even if crude |
| 4 | Reliability: retries with backoff, logging, upserts, per-record error handling, a `--dry-run` flag, a summary line |
| 5 | Tests for the logic that decides things (normalising, dedupe, scoring boundaries, routing); clean up structure and names |
| 6 | README: summary, setup, how it works, design decisions and trade-offs, assumptions, limitations, next steps. Record a 3–5 minute walkthrough video if allowed |
| 7 | Buffer. Clone the repo fresh and follow only your README to run it. Submit early |

## Rules

- **Working beats clever.** Don't over-engineer.
- **State assumptions** instead of guessing silently ("I assumed domain is the company key because…").
- **Never commit keys.** Use `.env` and `.env.example`.
- **Small commits** with clear messages: they tell the story of how you built it.
- If you use Claude Code (and it's allowed), say so in the README and make sure you can explain and
  change every line.

## Structure to aim for

```
README.md  requirements.txt  .env.example  .gitignore  CLAUDE.md (optional)
src/
  config.py  extract.py  transform.py  score.py  load.py  alerts.py  run_pipeline.py
tests/
  test_transform.py  test_score.py
data/   (sample inputs, if provided or created)
```

## README template

See [10-production-habits/04-git-and-documentation.md](../10-production-habits/04-git-and-documentation.md).
The sections reviewers read most: **design decisions**, **trade-offs**, **limitations and next steps**.

## Self-grading rubric

| Area | Strong submission |
| --- | --- |
| Works | Runs from a fresh clone using only the README |
| Correctness | Traps handled: www/https, email-derived domains, ranges like "51-200", blanks, personal emails |
| Idempotency | Second run creates zero new records |
| Reliability | Retries on 429/5xx, timeouts, per-record error handling, summary log line, dry run |
| AI use | Validated JSON, fallback on bad output, only where it adds value, cost noted |
| Code quality | Small pure functions, clear names, config in one place, no secrets |
| Tests | Edge cases for normalising, dedupe, scoring boundaries, routing |
| Explanation | README states decisions, trade-offs, assumptions, next steps |
| Business sense | Explains what a rep gets out of it and how you'd measure success |

## Practice brief (do it before the real one, in one 6-hour sitting)

> You have two lead sources: `crm_export.csv` (existing accounts: name, domain, owner) and
> `new_leads.csv` (name, website, country, employees, industry, contact_email). Build a Python pipeline
> that (1) normalises domains from websites and emails, (2) merges the sources so each company appears
> once, keeping existing owners, (3) scores each company 0–100 against this ICP: software or fintech,
> 20–500 employees, in DACH or Benelux, (4) uses Claude to write a one-sentence reason for every A-tier
> account, validated, (5) writes results to SQLite (or HubSpot) so that re-running produces no
> duplicates, (6) logs a run summary and survives one bad row. Include tests and a README.

You can use `data/leads_raw.csv` and `data/crm_accounts.csv` from this repo as the two sources: they
already contain the traps. Everything you need is taught in modules 3–10.

## Questions they'll ask about it in round 3

- Why this design? Why domain as the key?
- What happens if the API is down / rate-limits you / changes format?
- What breaks at 10x?
- How do you know it worked?
- What would you do with another week?
- Walk me through this function. Change it so that… (live)
