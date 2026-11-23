# 3. Prioritisation and the first 90 days

## "Five teams want automations. How do you prioritise?"

1. **Talk to the people first.** What problem is behind each request? (The culture doc: treat feedback
   as a signal, not instructions. Twenty requests often share one root cause, like bad data.)
2. **Estimate value:** hours saved × how often × how many people, or pipeline impact.
3. **Estimate effort and risk.**
4. **Score:** impact × frequency ÷ effort. Quick wins first, but schedule one foundational piece (e.g.
   clean data) because everything depends on it.
5. **Agree in writing** with the Head of GTM, share the list, revisit monthly.

| Request | Impact | Frequency | Effort | Priority |
| --- | --- | --- | --- | --- |
| Auto-route inbound demo requests | High (speed to lead) | Daily | Low–medium | **1** |
| Dedupe and enrich CRM accounts | High (everything depends on it) | Continuous | Medium | **2** |
| Tier-A signal alerts | High | Daily | Medium | 3 |
| AI pre-demo briefs | Medium–high | Per demo | Medium | 4 |
| Custom report for one rep | Low | Monthly | Low | Later / self-serve |

## Measuring success (from the job post)

"Reps spend less time on manual work and more time with customers, and more pipeline comes from
systems that run reliably and are actually used." So track: hours saved per rep, adoption, speed to
lead, data completeness and duplicate rate, pipeline and meetings from system-generated accounts,
reliability.

## Your first 30 / 60 / 90 days (a strong intro-call and final-round answer)

| When | Focus | Output |
| --- | --- | --- |
| **Days 1–30: listen and quick wins** | Sit with every BDR and AE; map their tools, spreadsheets and where time goes; audit CRM data quality (duplicates, missing fields, owners) | A written map of the current process and the top bottlenecks; one quick win shipped (e.g. inbound routing or a dedupe job) |
| **Days 31–60: the foundation** | Design the central system with the Head of GTM; build the account pipeline (normalise, dedupe, enrich, score, upsert) with monitoring | Clean, scored accounts in the CRM; a runbook; first metrics |
| **Days 61–90: pipeline generation** | Signal alerts, inbound scoring, AI briefs; measure and iterate with reps | Alerts reps use; a dashboard of impact; a prioritised roadmap for the next quarter |

> "First month: listen. I'd sit with every BDR and AE, map their setups and where their time goes, audit
> the CRM data, and ship one small high-impact fix fast, probably inbound routing. Second month: build
> the foundation, a clean, deduplicated, scored account layer in the CRM with monitoring. Third month:
> pipeline generation, signal alerts and AI briefs, measured against meetings booked and hours saved."

## Working with sales (they'll test this)

- Sit with reps and watch their day; don't build from assumptions.
- Ship small, visible wins early to earn trust.
- Explain things in their language (time saved, deals), not tech.
- Ask for feedback constantly; remove features nobody uses.
- Make the system's reasons visible (why this lead, why now).

## "Explain a technical concept to a sales rep"

> "A webhook is like a doorbell. Instead of our system checking every hour whether a new lead has
> arrived, HubSpot rings our system the moment someone books a demo, so the lead reaches you in seconds,
> with their company info and score attached."

> "An upsert means 'update it if it's there, add it if it's not', so when the system runs again it
> never creates a second PeopleCo."
