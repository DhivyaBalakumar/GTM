# Module 10: Production habits (scripts → systems)

The job post: *"You build systems that run reliably at 10x volume, not one-off scripts"* and *"scheduled
jobs, error handling, monitoring and alerts when something breaks"*. Secfix's culture doc has a "zero
high-severity bugs" policy. A GTM pipeline that fails silently means lost leads that nobody notices.

| # | File | Covers |
| --- | --- | --- |
| 1 | [01-reliability.md](01-reliability.md) | Logging, config, secrets, error handling per record, idempotency, dry runs, the summary line, project structure |
| 2 | [02-testing.md](02-testing.md) | pytest, what to test, boundaries and edge cases, parametrize, testing without calling real APIs |
| 3 | [03-scheduling-and-monitoring.md](03-scheduling-and-monitoring.md) | Task Scheduler, cron, GitHub Actions, failure alerts, health checks, runbooks |
| 4 | [04-git-and-documentation.md](04-git-and-documentation.md) | Git workflow, commits, branches and PRs, .gitignore, README template, decision records |

Examples you can run or copy:

| File | What |
| --- | --- |
| [examples/pipeline_skeleton.py](examples/pipeline_skeleton.py) | The reliable-pipeline pattern in ~100 lines: config, logging to file, per-record errors, dry run, summary, exit codes, failure alert |
| [examples/test_examples.py](examples/test_examples.py) | pytest examples: plain asserts, parametrize, expected exceptions, mocking an API |
| [examples/slack_alert.py](examples/slack_alert.py) | Post a message to Slack with an incoming webhook |
| [examples/github_actions_schedule.yml](examples/github_actions_schedule.yml) | Run a pipeline on a schedule in GitHub Actions, with secrets |

```powershell
python 10-production-habits/examples/pipeline_skeleton.py --dry-run
pytest 10-production-habits/examples/test_examples.py -v
```
