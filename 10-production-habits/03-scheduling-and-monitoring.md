# 3. Scheduling and monitoring

## Scheduling: making it run by itself

| Option | Where it runs | Good for |
| --- | --- | --- |
| **Windows Task Scheduler** | Your laptop | Practice (laptop must be on) |
| **cron** | A Linux/Mac machine or server | Simple servers |
| **GitHub Actions (schedule)** | GitHub's machines | Small pipelines, free tier, secrets built in |
| **Cloud schedulers** (Cloud Run jobs, AWS Lambda + EventBridge) | The cloud | Production |
| **Orchestrators** (Airflow, Dagster, Prefect) | A server | Many dependent jobs |
| **n8n / Zapier schedules** | Their cloud | Simple no-code flows |

### Windows Task Scheduler

Create Basic Task → trigger: Daily, repeat every 1 hour → Action: Start a program →
Program: `C:\Users\<you>\GTM\.venv\Scripts\python.exe` → Arguments: `src\run_pipeline.py` →
Start in: `C:\Users\<you>\GTM`.

### cron

```
# minute hour day-of-month month day-of-week  command
0 * * * *  cd /home/me/pipeline && .venv/bin/python src/run_pipeline.py >> cron.log 2>&1
```

`0 * * * *` = at minute 0 of every hour. `30 7 * * 1-5` = 07:30 on weekdays. Times are in the
server's time zone (often UTC).

### GitHub Actions

See [examples/github_actions_schedule.yml](examples/github_actions_schedule.yml). API keys go in the
repo's **Settings → Secrets and variables → Actions**, never in the YAML.

## Webhooks vs schedules

Schedules for batch work (refresh enrichment nightly, rescore hourly). Webhooks for things that must
happen in seconds (new demo request → route and alert). Many systems use both, plus a periodic full
sync as a safety net in case webhooks were missed.

## Monitoring: knowing it worked

| What | How |
| --- | --- |
| **Failure alerts** | On any crash, post to Slack (or email) with the error and a link to logs |
| **Silent-failure alerts** | Alert if the job *didn't run* (no summary in 2 hours), or wrote 0 records when it usually writes 50 |
| **Threshold alerts** | Failed records > 10%; created count spikes on a re-run; duplicates > 0 |
| **Dashboards** | Runs per day, records processed, failures, API usage |
| **Heartbeat** | Each run pings a monitoring service; no ping → alert (e.g. healthchecks.io) |

Alert the right people with **actionable** messages, and not too often (alert fatigue makes people
ignore them).

```
🔴 Account pipeline failed at 02:14 UTC
Step: load (HubSpot batch upsert)  Error: HTTP 401 Unauthorized
Likely cause: service key expired or scopes changed.  Logs: <link>  Runbook: <link>
```

## Runbook: so nothing depends on one person

The job post: "document it so nothing depends on one person". A runbook says, for each system:

- What it does and when it runs.
- How to run it manually, and how to dry-run it.
- How to read the summary line (healthy vs worrying values).
- "If X breaks, do Y" (a troubleshooting table).
- Who owns it, where the keys live, how to rotate them.

## After an incident: a five-line write-up

```
What broke:   overnight run updated 0 companies (failure alert 02:14)
Root cause:   3,000 leads imported; enrichment exceeded the rate limit for 40 minutes
Fix:          throttled enrichment, enrich only new/stale companies, re-ran (idempotent)
Prevention:   alert when updates < 50% of the 7-day average; batch-size check in tests
Owner / date: <you>, <date>
```

Next: [04-git-and-documentation.md](04-git-and-documentation.md)
