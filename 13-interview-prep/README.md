# Module 13: Interview prep, round by round

| Round | File | When |
| --- | --- | --- |
| 1. Intro call (30 min) with Jakub, Talent Partner | [01-intro-call.md](01-intro-call.md) | **Fri 27 Nov 2026, 4:00 pm IST** |
| 2. Take-home (8–10 h, 7 days) | [02-take-home.md](02-take-home.md) | After the intro call |
| 3. Live coding with the Head of GTM (90 min) | [03-live-coding.md](03-live-coding.md) + [live_coding_practice/](live_coding_practice) | After the take-home |
| 4. Final with a co-founder and the Head of GTM | [04-final-round.md](04-final-round.md) | Last |
| All rounds | [05-question-bank.md](05-question-bank.md) | Every question type, with model answers |

## Rules for every round

1. **Only claim what you built and can explain.** Interviewers dig into follow-ups; the intro call is
   recorded by an AI notetaker, so later interviewers may read it. Stay consistent with your resume and
   video.
2. **Connect every technical answer to the business:** reps' time saved, pipeline, trust in the CRM.
3. **Be specific:** numbers, tools, what *you* did ("I", not "we").
4. **Think out loud** in technical rounds. Getting stuck and recovering clearly beats silence.
5. **Ask good questions.** It shows you're already thinking about their system.

## The 2-minute version of what you'd build (memorise it, use it everywhere)

> "Right now every salesperson runs their own setup for data and outreach. I'd build one central system:
> it pulls companies from providers and signal sources, normalises and dedupes them by domain, enriches
> the gaps, and scores each one on fit and intent with reasons. It batch-upserts them into the CRM so
> re-runs never create duplicates, keeps existing owners, and routes new accounts by territory. Then it
> tells each rep who to call today and why, in Slack, and uses Claude for research briefs, with
> validated output so nothing bad reaches the CRM. Underneath: retries for rate limits, logging, tests,
> scheduled runs and alerts when anything breaks. Success is reps spending less time on manual work and
> more pipeline coming from systems they actually use."
