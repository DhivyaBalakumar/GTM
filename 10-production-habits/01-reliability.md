# 1. Reliability: the habits that make a script a system

| Habit | Plain meaning | Why it matters |
| --- | --- | --- |
| **Logging** | Timestamped notes to a file (the `logging` module) instead of `print` | Tells you what happened at 3 am when nobody was watching |
| **Secrets in .env** | Keys in a file that's never committed | Safety (bots scan GitHub for leaked keys within minutes) |
| **Config in one place** | Thresholds, team lists, batch sizes in `config.py` | Business changes are one-line edits, not logic changes |
| **Per-record error handling** | One bad record is logged and skipped | The run finishes instead of dying halfway |
| **Fail loudly on fatal errors** | Bad key, missing input file → stop with a clear message and alert | Problems are found in minutes, not weeks |
| **Retries with backoff** | Temporary API failures are retried | Survives rate limits and blips |
| **Idempotency** | Running twice = running once (upserts, remembered alerts) | Re-runs after a crash are safe |
| **Dry run** | `--dry-run` does everything except the final write | Safe testing on real data |
| **Summary line** | One line per run with all the counts | Spot problems at a glance |
| **Exit codes** | `0` = success, non-zero = failure | Schedulers know when a run failed |
| **Tests** | Small checks of the decision logic | Change code without fear |
| **Structure** | extract / transform / load in separate files | Easy to read, test and hand over |

## Logging

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-7s %(name)s: %(message)s",
    handlers=[logging.FileHandler("pipeline.log", encoding="utf-8"), logging.StreamHandler()],
)
log = logging.getLogger("pipeline")

log.info("Read %d leads from %s", 25, "leads.csv")
log.warning("Skipping %s: personal email", "max@gmail.com")
log.error("Upsert failed for batch %d: %s", 3, "HTTP 400 ...")
log.exception("Unexpected error")      # inside except: logs the full traceback too
```

Levels: DEBUG (detail for developers) < INFO (normal progress) < WARNING (something odd, run continues)
< ERROR (something failed) < CRITICAL. Never log API keys or unnecessary personal data.

## The summary line

```
SUMMARY read=25 valid=23 unique=19 enriched=15 failed=1 | tiers A=5 B=6 C=8 | CRM created=4 updated=15 | alerts=5 | dry_run=False | 6.2s
```

A human (or an alert rule) can see at once whether the run was healthy. A re-run with `created` > 0
for the same input means dedupe or upserts broke.

## Config

```python
# config.py
TARGET_INDUSTRIES = {"Software", "Fintech", "Healthtech"}
TARGET_COUNTRIES = {"DE", "AT", "CH", "NL", "BE", "LU"}
EMPLOYEES_MIN, EMPLOYEES_MAX = 20, 500
TIER_A, TIER_B = 75, 50
DACH_TEAM = ["lena", "jonas"]
BATCH_SIZE = 100
```

Secrets don't go here: `HUBSPOT_TOKEN = os.getenv("HUBSPOT_TOKEN")`, with the value in `.env`, and a
`.env.example` listing the names (no values) so others know what to set.

## Error handling: what to catch where

```python
def main():
    try:
        leads = read_leads(path)              # missing file -> fatal, handled below
        for lead in leads:
            try:
                process(lead)                 # one bad lead -> log, count, continue
            except Exception as e:
                failed.append(lead["domain"])
                log.warning("Failed on %s: %s", lead["domain"], e)
        upsert(results)
        log.info("SUMMARY ...")
    except Exception:
        log.exception("Run failed")
        send_failure_alert()
        sys.exit(1)                           # tell the scheduler it failed
```

Also alert if too many records fail (e.g. > 10%): that's usually a systemic problem, not bad data.

## Project structure

```
src/
  config.py      settings
  extract.py     read files, call APIs (retries, pagination)
  transform.py   normalise, dedupe (pure functions)
  score.py       scoring and routing (pure functions)
  load.py        CRM writes (batch upsert, dry run)
  alerts.py      Slack messages
  run_pipeline.py  main(): the steps in order + summary
tests/
README.md  requirements.txt  .env.example  .gitignore
```

See the working pattern in [examples/pipeline_skeleton.py](examples/pipeline_skeleton.py).

Next: [02-testing.md](02-testing.md)
