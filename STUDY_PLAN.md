# Study plan

About 5–6 hours a day. Each day: **learn** (read the module, run the lessons), **build** (do the
exercise without AI help; if stuck for 15 minutes, ask for a hint, not the answer), **explain** (say it
out loud for 2 minutes as if to the Head of GTM). Tick boxes as you go.

## Week 1: intro call first, Python foundations alongside

The intro call (Fri 27 Nov, 4 pm IST) doesn't test coding. It tests your story, the company and the
role. So mornings go to call prep, afternoons to Python.

### Mon 23 Nov
- [ ] [00-the-target](00-the-target): the company, the role, the process, the system diagram
- [ ] [01-gtm-foundations/01](01-gtm-foundations/01-what-gtm-is.md) and [02](01-gtm-foundations/02-icp-personas-buying-committee.md)
- [ ] Setup: [02-computers-and-setup](02-computers-and-setup) (clone this repo, venv, packages)
- [ ] Python lessons 1–2 (values, strings)

### Tue 24 Nov
- [ ] [01-gtm-foundations/03–05](01-gtm-foundations): signals, scoring, routing
- [ ] Python lessons 3–4 (lists, dicts, sets)
- [ ] Exercise [ex01_strings](03-python/exercises/ex01_strings.py)

### Wed 25 Nov
- [ ] [01-gtm-foundations/06–08](01-gtm-foundations): outreach, metrics, the compliance market
- [ ] Python lessons 5–7 (conditions, loops, functions)
- [ ] Exercises [ex02](03-python/exercises/ex02_collections.py) and [ex03](03-python/exercises/ex03_functions_and_rules.py)

### Thu 26 Nov
- [ ] [13-interview-prep/01-intro-call.md](13-interview-prep/01-intro-call.md): write your own answers; record yourself
- [ ] A full mock intro call (ask Claude to play Jakub)
- [ ] Python lessons 8–9 (comprehensions, errors)

### Fri 27 Nov
- [ ] Morning: re-read the company page, your answers and your questions; light Python only
- [ ] **4:00 pm IST: intro call with Jakub**
- [ ] After: write down what was asked and anything about the take-home

### Sat 28 – Sun 29 Nov
- [ ] Python lessons 10–12 (files, standard library, scripts) + [ex04](03-python/exercises/ex04_errors_and_files.py)
- [ ] [04-pandas](04-pandas): lessons 1–3

## Week 2: data, APIs, CRM, SQL

| Day | Learn | Build |
| --- | --- | --- |
| Mon 30 Nov | pandas lessons 4–5 | [pandas exercise](04-pandas/exercises/ex01_clean_score.py) |
| Tue 1 Dec | [06-apis](06-apis-and-webhooks) theory 1–3, lessons 1–3 | [API exercise](06-apis-and-webhooks/exercises/ex01_api_client.py) |
| Wed 2 Dec | Webhooks theory 4, lessons 4–5; [07-crm-hubspot](07-crm-hubspot) | Free HubSpot account + service key; run `hubspot_client.py` twice |
| Thu 3 Dec | [05-sql](05-sql) lessons 1–3 | SQL exercises 1–10 |
| Fri 4 Dec | SQL lessons 4–6; [08-data-quality](08-data-quality) | SQL exercises 11–15; run `entity_resolution.py` |
| Sat 5 Dec | [09-claude-and-ai](09-claude-and-ai) | Get an API key; run `claude_scoring.py --live`; break the prompt and watch validation |
| Sun 6 Dec | [10-production-habits](10-production-habits) | Run the skeleton and tests; schedule something with Task Scheduler |

## Week 3: put it together and rehearse

| Day | Do |
| --- | --- |
| Mon–Tue | The [practice take-home](13-interview-prep/02-take-home.md) in one 6-hour sitting, from an empty folder; grade it with the rubric |
| Wed | [11-gtm-tools](11-gtm-tools-and-integrations) + [12-systems-thinking](12-systems-thinking); answer the design questions out loud |
| Thu | [Live-coding practice](13-interview-prep/live_coding_practice) P1–P6, timed, out loud |
| Fri | P7–P12 + SQL trio; one full mock live round |
| Weekend | [Final-round stories](13-interview-prep/04-final-round.md): write five true stories and the hack answer; rehearse |

When the real take-home arrives, follow the 7-day plan in [02-take-home.md](13-interview-prep/02-take-home.md).

## Ready checklists

**Intro call**
- [ ] Background in 90 seconds, without notes
- [ ] Secfix in 30 seconds; the role in 60 seconds
- [ ] The system in 2 minutes
- [ ] 3–4 questions ready; logistics answers ready

**Take-home**
- [ ] Clean, dedupe and score a messy CSV with pandas
- [ ] Call an API with a key, retries, pagination and batching
- [ ] Upsert into HubSpot by a unique key with no duplicates on re-run
- [ ] Logging, a summary line, a dry-run flag, tests, a README with decisions

**Live coding**
- [ ] Retry, pagination and batching loops from memory
- [ ] All 12 practice problems passing, out loud, under 15 minutes each
- [ ] Basic SQL: filter, group, join, duplicates, CASE, ROW_NUMBER

**Final**
- [ ] Five true STAR stories + the hack answer
- [ ] First-90-days plan; why first GTM engineer; questions for the co-founder
