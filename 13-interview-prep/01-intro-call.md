# Round 1: the intro call (30 minutes)

**With:** Jakub Ossowski, Talent Partner. **When:** Fri 27 Nov 2026, 4:00 pm IST. An AI notetaker
records it.

## What it tests

That you fit on paper, communicate clearly in English, understand the role and the company, prepared
as asked (job description, website, culture doc), are honest and consistent with your resume, and
bring good questions. It's not a coding interview.

## Likely flow

1. Intros and small talk (2 min)
2. Jakub explains Secfix and the process (5 min)
3. Your background and motivation (10 min)
4. Role understanding, maybe one light scenario (5 min)
5. Logistics: hours, salary, start date, notice (3 min)
6. Your questions (5 min)

## Your answers (say them in your own words; don't read)

### "Walk me through your background." (about 90 seconds)

Order: degree → internship → current role and the most relevant thing you built → why GTM engineering
→ bridge to this role.

> "I'm a Computer Science graduate from Dayananda Sagar University, 2026, with a 9.12 CGPA, majoring in
> Cloud and DevOps. During my final year I interned at TechBliss Solutions as an AI engineering intern,
> cleaning and analysing datasets in Python and building dashboards in Power BI and Tableau.
>
> Since April I've been at Mathra Marketing, where the most relevant thing I've built is an outbound
> lead-generation workflow for a client, ConsultKumar. It pulls prospects from Apollo and Clay, enriches
> and deduplicates contacts, segments them by ICP, drafts segment-specific email and LinkedIn sequences
> with Claude, and logs results. I then packaged the steps as Claude agent skills so anyone can run it
> the same way.
>
> I've also built data pipelines in my projects: a YouTube ETL pipeline with retries and rate-limit
> handling that writes scores back to HubSpot, and GreenTensor, a real-time pipeline that scores
> workloads and flags anomalies, which has a published patent application.
>
> What I enjoy most is turning a messy manual process into a reliable system people actually use,
> which is exactly what this role is."

### "Why this role? Why Secfix?"

- **First GTM Engineer:** owning the whole system, not one ticket. "I want the ambiguity and the
  ownership."
- **A company that sells trust** needs a clean, reliable CRM and data: "that's my kind of problem".
- **One specific line from the culture doc:** "Treating customer feedback as a signal rather than
  instructions. In GTM that means finding the one bottleneck behind twenty automation requests."
- **Claude:** "It's the must-have in the post, and it's how I already work every day."
- **The timing:** the Series A in February to expand across Europe means the GTM team is growing,
  which is exactly when a central system matters.

### "What do you understand about what Secfix does?"

> "Secfix helps European companies get security certifications like ISO 27001, SOC 2 and TISAX in weeks
> instead of months, with a platform that automates the security checks and evidence collection, plus
> experts who guide them through the audit. Customers usually buy when a big client demands a
> certificate, a regulation like NIS2 applies, or they raise money and move upmarket. Sales is
> demo-led, so BDRs book demos and AEs close."

### "What do you understand about this role?"

> "Today every salesperson runs their own setup for data and outreach. The role is to replace that with
> one central, automated system: clean, deduplicated, scored data in the CRM; signal-based alerts telling
> reps who to call and why; fast inbound scoring and routing; and Claude-powered tools for research and
> CRM updates, all reliable, monitored and documented. It's a coding role, Python and SQL every day,
> and success is measured by reps spending less time on manual work and more pipeline coming from
> systems they actually use."

### "Explain the system you'd build in plain words."

Use the 2-minute version in the [README](README.md), or walk the diagram in
[00-the-target/04-the-system-at-a-glance.md](../00-the-target/04-the-system-at-a-glance.md).

### "Tell me about your Claude experience." / "about your application video"

Go one level deeper than the video, using only what you did:

> "I use Claude Code daily to build: I have it read the project, then I make small changes and review
> every diff. On the API side, in the outbound workflow Claude drafts sequences per ICP segment. I
> learned to ask for a fixed output format and check it before anything is used, and I packaged the
> workflow as agent skills so the output is consistent whoever runs it."

Prepare one concrete "what broke and how I fixed it" example from your own work.

### "What would you do in your first 30 days?"

> "Talk to every BDR and AE, map their current setups and where their time goes, audit the CRM data,
> and ship one small high-impact fix quickly, probably inbound routing or deduplication. Then design the
> central system with the Head of GTM." (Full version:
> [12-systems-thinking/03](../12-systems-thinking/03-prioritisation-and-first-90-days.md).)

### "Explain a technical concept to a sales rep."

> "A webhook is like a doorbell: instead of our system checking every hour whether a new lead arrived,
> the CRM rings our code the moment someone books a demo, so you get the lead in seconds."

### "What are you learning right now?" / "Where are you less experienced?"

Be honest and show momentum:

> "I'm deepening HubSpot's API, webhooks and SQL. I've set up a structured plan and I'm building small
> practice systems every day, like a retry function with backoff and a batch upsert that proves
> re-runs don't create duplicates."

## Logistics

| Question | Answer |
| --- | --- |
| Working 9:00–13:00 CET in sync? | "Yes. That's 1:30 to 5:30 pm IST in winter time." |
| Salary expectations? | The post lists 20k–32k USD. Say a figure within the range, towards the upper end, and be flexible. Don't name a number above the range. |
| Start date? | A real date you can commit to. |
| Notice period? | The truth (and what your current commitments are). |
| Other interviews? | Honest, brief. |

## Questions to ask Jakub (pick 3–4)

1. "Which CRM and outreach tools does the GTM team use today?"
2. "What's the single biggest manual bottleneck you'd want the first GTM Engineer to fix?"
3. "What would success look like for this role after three months?"
4. "What does the take-home usually involve, and are AI tools allowed?"
5. "Who would I work with most day to day: the Head of GTM, BDRs, AEs?"
6. "How does the team in India work with the team in Europe day to day?"

## On the day

- Quiet room, good light, earphones; test camera and mic; join 3–5 minutes early.
- Job description and notes open in another window, but **talk, don't read**.
- Smile at the start and end. Pause before answering; it's fine.
- Keep answers to 60–90 seconds; offer to go deeper.
- End: thank him, ask about next steps and timing.

## Practice

Record yourself answering the first five questions. Check: under 90 seconds each? specific? any
claim you couldn't defend in a follow-up? Then do a full mock call (ask Claude to play Jakub).
