# Round 3: live coding with the Head of GTM (about 90 minutes)

## What it tests

That you understand your own take-home, can debug and extend real GTM code calmly while explaining,
write basic SQL, and think about GTM problems. Reported format at this company (for engineering roles):
a shared codebase with bugs and bug reports; find the cause, fix it, implement a feature end to end.
"Real-world problem scenarios", not puzzles. One SQL question was "select rows where a value is above
X".

## Likely shape

- ~20 min on your take-home ("why this design?", "what breaks at 10x?", "what if this API is down?")
- ~45 min coding: debug or extend a GTM script; maybe a small SQL task
- ~20 min GTM design questions (see [12-systems-thinking](../12-systems-thinking))

Ask at the start: "Can I look things up or use AI tools?" and "Should I optimise for working first,
then clean?"

## How to behave while coding (say these steps out loud)

1. **Restate** the problem in your words; ask about inputs, edge cases, and what "done" means.
2. **Look at the data first:** "Let me print a few rows."
3. **Say your plan** in one or two sentences before typing.
4. **Write the simplest version that works,** then improve.
5. **Test as you go** with a tiny example.
6. **When stuck, narrate the debugging routine:** reproduce → read the error (last line first) → guess
   → check with a print → fix → re-run.
7. **Mention what you'd add with more time:** tests, retries, logging.

Getting stuck and recovering clearly scores better than silence. "I'm not sure; here's how I'd find
out" is a good answer.

## The 12 problem types you should have solved out loud at least once

Practise each in under 15 minutes, out loud, in
[live_coding_practice/problems.py](live_coding_practice/problems.py) (solutions in
[live_coding_practice/solutions.py](live_coding_practice/solutions.py)):

| # | Problem | Concept |
| --- | --- | --- |
| P1 | Normalise domains from URLs and emails | Strings, edge cases |
| P2 | Dedupe keeping the most complete record | Dicts, survivorship |
| P3 | Bug: "every run creates duplicate companies" | Upserts, idempotency |
| P4 | Bug: "only 100 contacts sync; we have 2,300" | Pagination |
| P5 | "The enrichment API sometimes returns 429 and the job dies" | Retries, backoff |
| P6 | Parse a nested API response safely | `.get()`, defensive code |
| P7 | Enrich every row; one failure must not stop the rest | try/except per record, logging |
| P8 | Bug: "companies with exactly 20 employees are scored Small" | Boundaries, tests |
| P9 | Count leads per source per month | Grouping, dates |
| P10 | Route a lead: existing owner, DACH team, round-robin, fallback | Rules, order, cycle |
| P11 | Process each webhook event once | Sets, event keys |
| P12 | SQL: duplicates, accounts without contacts, meeting rate by source | GROUP BY/HAVING, LEFT JOIN, CASE |

Run `python 13-interview-prep/live_coding_practice/problems.py` to check your answers.

## SQL to have ready

```sql
-- Rows above a value
SELECT name, amount_eur FROM deals WHERE amount_eur > 15000 ORDER BY amount_eur DESC;
-- Duplicate domains
SELECT LOWER(domain) d, COUNT(*) FROM accounts GROUP BY LOWER(domain) HAVING COUNT(*) > 1;
-- Accounts with no contacts
SELECT a.name FROM accounts a LEFT JOIN contacts c ON c.account_id = a.id WHERE c.id IS NULL;
-- Meeting rate by source
SELECT source, COUNT(*) leads, ROUND(100.0 * SUM(meeting_booked) / COUNT(*), 1) meeting_pct
FROM leads GROUP BY source ORDER BY meeting_pct DESC;
-- Top account per rep
WITH r AS (SELECT owner, name, score, ROW_NUMBER() OVER (PARTITION BY owner ORDER BY score DESC) rn FROM accounts)
SELECT owner, name, score FROM r WHERE rn = 1;
```

Full practice: [05-sql/exercises.md](../05-sql/exercises.md).

## Phrases that help

- "Before I change anything, let me reproduce it."
- "My hypothesis is X; let me check by printing Y."
- "This works for the happy path; the edge cases I'd handle next are…"
- "I'd add a test here so this bug can't come back."
- "With more time I'd add retries and a dry-run flag."
- "In business terms, this fix means reps stop seeing duplicate accounts."
