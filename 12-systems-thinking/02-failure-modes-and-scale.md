# 2. Failure modes, and what breaks at 10x

## Failure modes: what goes wrong, how you'd know, what protects you

| Failure | Symptom | Protection |
| --- | --- | --- |
| API rate-limited | 429s, slow or failed runs | Retries + backoff, batching, throttling, incremental loads |
| API down / timeouts | Run fails or hangs | Timeouts, retries, failure alerts, safe re-runs |
| API format changed | KeyErrors, blanks everywhere | Defensive `.get()`, validation, alert on null spikes |
| Key expired / scope removed | 401/403 | Fail fast, clear alert naming the cause, key rotation runbook |
| Duplicates created | Reps see two PeopleCos | Upsert by unique key, dedupe job, "created on re-run" alert |
| Good data overwritten | Reps' corrections vanish | Field ownership, never write blanks |
| Silent failure (job didn't run) | Nothing happens, nobody notices | Heartbeat / "no summary in 2 h" alert |
| Partial failure | Half the batch written | Idempotent writes; per-record error log; re-run |
| Webhook missed or duplicated | Lead not routed / routed twice | Event dedupe, retries from sender, periodic sync safety net |
| Bad source data | Wrong scores | Validation, dropped-with-reason reports, quality checks |
| AI wrong or malformed | Rubbish in CRM | Schema validation, allow-listed fields, review queue |
| Alert fatigue | Reps ignore Slack | Thresholds, digests, measure alert → action |
| Logic bug in scoring | Wrong accounts prioritised | Tests on boundaries, review with reps, dry runs |

## What breaks at 10x volume (a favourite question)

Say 2,000 → 20,000 accounts, or 50 → 500 inbound leads a day.

| What breaks | Why | Fix |
| --- | --- | --- |
| Rate limits | 10x the API calls | Batch endpoints, throttle, **incremental** processing (only new/changed), cache enrichment |
| Run time | Hourly job takes 2 hours | Incremental loads, parallelism within limits, split jobs |
| Cost | Enrichment and AI per record | Only enrich/AI accounts passing fit rules; cache; cheaper models; waterfalls |
| Memory | Loading everything into pandas | Process in chunks; push heavy joins into SQL/warehouse |
| Duplicates | More sources, more variants | Stronger entity resolution, alternate-domain table, review queue |
| Routing fairness | Round-robin state lost on restarts | Store assignment state in the CRM/DB; capacity-based routing |
| Alert volume | 10x alerts | Stricter thresholds, daily digest, prioritised list per rep |
| Webhook bursts | Spikes of events | Queue + workers; reply 200 immediately |
| Maintainability | One big script | Modules, tests, docs, monitoring, a warehouse for history |
| People | More reps, more requests | Self-serve configs, prioritisation process, documentation |

> "At 10x the first things to break are rate limits and run time, so I'd move to incremental
> processing with batch endpoints and caching. Cost is next, so enrichment and AI only run on accounts
> that pass cheap fit rules. Then I'd add a queue for webhook bursts, persist routing state, and push
> heavier joins into a warehouse."

## Diagnosing a problem (ownership: "find the root cause, ship the fix, document it")

1. **Reproduce** and scope it: which records, since when?
2. **Read the logs** around the first failure.
3. **Form a hypothesis**, check it with data.
4. **Fix** the cause, not just the symptom; add a test that would have caught it.
5. **Repair the data** (idempotent re-run).
6. **Write the five-line incident note** and add monitoring so it's caught next time.

Next: [03-prioritisation-and-first-90-days.md](03-prioritisation-and-first-90-days.md)
