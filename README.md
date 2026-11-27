# GTM Engineer: everything I need to know

One place to learn, from zero, everything the **GTM Engineer** role at **Secfix** needs: the company,
the role, go-to-market concepts, Python, pandas, SQL, APIs, webhooks, CRM/HubSpot, data quality, Claude,
production habits, the tool landscape, systems design, and a script for every interview round.

It's built for learning by doing: theory as short markdown lessons, code as **runnable, heavily
commented Python files**, and **exercises that check your answers** (with solutions to compare after).

**Start here:** read this page, then [STUDY_PLAN.md](STUDY_PLAN.md) for the day-by-day plan, and
[HOW_TO_LEARN_THE_CODE.md](HOW_TO_LEARN_THE_CODE.md) for how to practise (rebuild the 6 core patterns,
don't memorise code).

## The modules

| # | Module | What you'll be able to do | Type |
| --- | --- | --- | --- |
| 00 | [The target](00-the-target) | Explain Secfix, the role (line by line), the interview rounds and the whole system | Read |
| 01 | [GTM foundations](01-gtm-foundations) | Talk like a Head of GTM: funnel, roles, ICP, signals, scoring, routing, outreach, metrics, the compliance market | Read |
| 02 | [Computers and setup](02-computers-and-setup) | Understand how programs and APIs work; set up Python, VS Code, venv, Git on Windows | Read + do |
| 03 | [Python](03-python) | Write 50–150 line scripts that clean data and make decisions; 12 lessons, 4 checked exercises | Code |
| 04 | [pandas](04-pandas) | Load, clean, dedupe, score, merge and export tables; 5 lessons, 1 checked exercise | Code |
| 05 | [SQL](05-sql) | Answer GTM questions with SQL, from SELECT to window functions and upserts; 6 lessons, 15 exercises | Code |
| 06 | [APIs and webhooks](06-apis-and-webhooks) | Call APIs with keys, retries, pagination and batching; build a webhook receiver; practise against a local API that rate-limits and fails like a real one | Read + code |
| 07 | [CRM and HubSpot](07-crm-hubspot) | Understand CRM data models; use the HubSpot API: unique properties, batch upserts, search, associations | Read + code |
| 08 | [Data quality](08-data-quality) | Normalise, validate, dedupe, resolve entities, enrich with waterfalls, own fields, keep data fresh | Read + code |
| 09 | [Claude and AI](09-claude-and-ai) | Decide AI vs rules; call Claude with structured output, validation and guardrails; use Claude Code well | Read + code |
| 10 | [Production habits](10-production-habits) | Logging, config, secrets, tests, scheduling, monitoring, Git, READMEs, runbooks | Read + code |
| 11 | [GTM tools and integrations](11-gtm-tools-and-integrations) | Know Clay, Apollo, n8n, outreach tools, warehouses and reverse ETL; decide code vs no-code | Read |
| 12 | [Systems thinking](12-systems-thinking) | Design account pipelines, signal alerts, inbound routing and AI assistants; failure modes; 10x; prioritisation; first 90 days | Read |
| 13 | [Interview prep](13-interview-prep) | Scripts and practice for the intro call, take-home, live coding (12 checked problems) and final round | Read + practise |
| 14 | [Cheat sheets](14-cheatsheets) | Python, pandas, SQL, HTTP, Git, cron, data types and structures, and a glossary on a few pages | Reference |
| 15 | [Deep dives](15-deep-dives) | Long, very explanatory guides: data types and data structures; JSON, APIs and pandas and how this role uses them; deduplication from zero to advanced; each with runnable companion code | Read + code |
| 16 | [The end-to-end pipeline](16-end-to-end-pipeline) | Every step from collection to CRM and outreach: all the tools per step (Apollo, Clay, ZoomInfo, Cognism, HubSpot, sequencers...), click vs code, pagination, rate limits, cleaning, dedupe, enrichment waterfalls, suppression, scoring, segmentation, routing, upserts, signals, scheduling, reporting; one runnable script doing all 11 steps | Read + code |

Sample data used by the lessons lives in [data/](data) (messy leads with deliberate traps, CRM accounts,
contacts, deals, inbound leads, an API response and webhook events).

## Quick start (Windows PowerShell)

```powershell
git clone https://github.com/DhivyaBalakumar/GTM.git
cd GTM
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt

python 03-python/lessons/01_values_and_variables.py     # your first lesson
python 03-python/exercises/ex01_strings.py              # your first exercise (it checks your answers)
pytest                                                  # checks that every solution in the repo works
```

Some modules need a second terminal (the local practice API or webhook receiver); their READMEs say
exactly what to run.

## How to study each topic

Full method and the 6 core patterns to rebuild: [HOW_TO_LEARN_THE_CODE.md](HOW_TO_LEARN_THE_CODE.md).

1. **Read** the lesson (markdown or the comments in the `.py` file).
2. **Run** the code and match each printed line to the code that produced it.
3. **Break** something on purpose; read the error; fix it.
4. **Do the exercise without AI.** Stuck for 15 minutes? Ask for a hint, not the answer. Then compare
   with the solution.
5. **Explain it out loud** for two minutes as if to the Head of GTM. If you can explain it, you know it.

## The one-paragraph version of the job

Secfix helps European companies get security certifications (ISO 27001, SOC 2, TISAX) in weeks. Its
sales team today runs on scattered, personal setups. The first GTM Engineer replaces that with **one
central, automated system**: clean, deduplicated, scored accounts in the CRM; signal-based alerts telling
reps who to call today and why; fast inbound scoring and routing; and Claude-powered tools for research
and CRM updates, all reliable, monitored and documented. Success: **reps spend less time on manual work,
and more pipeline comes from systems that run reliably and are actually used.**

## What you can skip

LeetCode-style algorithms, machine learning, advanced object-oriented design, async programming, web
frameworks beyond one small Flask app, database administration.

## Notes

- Company facts were researched in November 2026; check Secfix's website for updates.
- HubSpot's developer platform changes often (for example, legacy private apps were retired in October
  2026 in favour of service keys); check the current docs when building against it.
- The companies, people and numbers in `data/` are invented for practice.
- Never commit API keys: they go in `.env`, which `.gitignore` excludes. See `.env.example`.
