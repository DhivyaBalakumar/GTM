# 4. Git and documentation

## Git: snapshots of your code

| Command | What it does |
| --- | --- |
| `git init` | Start tracking a folder (once) |
| `git clone <url>` | Copy a repo from GitHub |
| `git status` | What changed |
| `git diff` | The exact line changes |
| `git add .` | Stage all changes for the next commit |
| `git commit -m "Add dedupe step"` | Save a snapshot with a message |
| `git push` / `git pull` | Upload / download commits |
| `git log --oneline` | History |
| `git checkout -- file.py` | Throw away uncommitted changes to a file |
| `git switch -c feature-x` | Create and switch to a new branch |

**Good commits:** small, one idea each, message says *what and why* in the imperative ("Retry 429s
with backoff in enrichment"). A take-home with 15 clear commits tells a story; one giant commit
doesn't.

**Branches and pull requests (PRs):** work on a branch, open a PR on GitHub, get a review, merge. Good
to know; not essential for a solo take-home.

## .gitignore

```
.venv/
.env
__pycache__/
*.log
output/
*.db
```

**Never commit secrets.** If you ever do: rotate (revoke and replace) the key immediately, because
deleting the commit isn't enough. At a security-compliance company, a leaked key in a take-home is an
instant red flag.

## README: the front page of every project

```markdown
# Account Pipeline

One paragraph: what problem it solves and what it does.
Pulls accounts from X and Y, dedupes by domain, scores against the ICP, upserts into HubSpot.
Safe to re-run; alerts on failure.

## Run it
pip install -r requirements.txt
cp .env.example .env   # add keys
python src/run_pipeline.py --dry-run

## How it works
1. Extract … 2. Normalise … 3. Dedupe … 4. Score … 5. Load …   (a diagram helps)

## Design decisions
- Dedupe on normalised domain, falling back to email domain, because names vary across sources.
- Batch upsert by a unique domain property so re-runs never duplicate.
- Retries with backoff on 429/5xx; other 4xx fail fast.
- Field ownership: the pipeline writes score fields only; never owner on existing records.

## Assumptions
## Limitations and what I'd do next
## Tests
pytest
```

The **design decisions** and **limitations** sections are what reviewers read most closely: they show
judgement.

## Documenting decisions (lightweight)

A short note per important choice: *context → decision → alternatives considered → consequences*.
Example: "We score with rules, not ML, because we have < 200 closed deals; revisit at 1,000."

## Writing for a remote team

Secfix is fully remote and writes things down. Good async updates are short and structured:

```
Shipped: inbound routing v1. Demo requests now reach the right AE in under a minute (was ~4 h median).
Next: alerts for tier-A signals. Blocked on: Slack app approval.
Ask: Jonas, can you confirm the DACH territory list?
```

Short Loom videos (2–3 min) work well for walkthroughs.
