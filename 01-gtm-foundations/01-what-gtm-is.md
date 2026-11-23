# 1. What GTM is: the business, the team, the funnel

## GTM = go-to-market

Everything a company does to turn its product into money: finding the right customers, getting their
attention, convincing them, closing the deal, and keeping them.

At Secfix, the product team builds the compliance software. **The GTM team's job is to get companies
to buy it.**

## How a B2B SaaS company makes money

- **B2B:** it sells to businesses, not individuals.
- **SaaS (software as a service):** customers pay a **subscription** (usually yearly) instead of
  buying software once.
- **ARR (annual recurring revenue):** the yearly value of all active subscriptions. The number
  investors care about most. **MRR** is the monthly version.
- **Churn:** customers who leave. **Expansion / upsell:** existing customers paying more (for example
  adding SOC 2 after ISO 27001).
- **ACV (annual contract value):** the average yearly value of one customer's contract.

So growth = **new customers** (the GTM team's main job) + **expansion** − **churn**.

## The GTM team

| Role | What they do | Analogy | What you build for them |
| --- | --- | --- | --- |
| **Marketing** | Gets companies to notice Secfix: content, ads, LinkedIn, webinars, website | Puts up the shop sign | Lead capture, attribution, inbound scoring |
| **BDR / SDR** (business / sales development rep) | Finds and contacts potential customers, books first meetings | Says "come in, take a look" | Target lists, signals, enrichment, sequences, alerts |
| **AE** (account executive) | Runs demos, negotiates, closes deals | The salesperson at the counter | Account research briefs, CRM hygiene, proposal help |
| **CSM** (customer success manager) | Keeps customers happy so they renew and expand | Makes sure they come back | Health scores, renewal alerts |
| **RevOps** (revenue operations) | Manages CRM settings, reports and processes | Runs the shop's records | (Overlap: you build in code what they'd configure by hand) |
| **GTM Engineer** | Builds code, data pipelines and AI tools so all of the above work faster | Builds the machines that do the boring work | Everything above |

## The funnel: how a stranger becomes a customer

```
Total market: every company that might ever fit
   ↓   marketing and outreach
Lead          – we know they exist and have contact details
   ↓   they fit well and/or show interest
MQL           – Marketing Qualified Lead: marketing thinks it's promising
   ↓   a BDR checks and talks to them
SQL           – Sales Qualified Lead: real need, budget, timing confirmed; meeting booked
   ↓   discovery call, demo
Opportunity   – an active deal in the pipeline, with a value and a stage
   ↓   proposal, negotiation
Closed won    – customer (or closed lost)
   ↓   onboarding, value, renewal
Renewal / expansion
```

Companies drop out at every step. The GTM team's goal is to push **more of the right companies**
through, **faster**. Each arrow is a **conversion rate** you can measure (for example, 20% of MQLs
become SQLs).

## Deal stages (the sales pipeline)

A typical pipeline for a demo-led company:

`Meeting booked → Discovery done → Demo done → Proposal sent → Negotiation → Closed won / Closed lost`

"Pipeline" in sales means all open deals and their total value. "Pipeline generation" means creating
new opportunities. (Not to be confused with a **data pipeline**, which is code that moves data.)

## Inbound vs outbound

| | Inbound | Outbound |
| --- | --- | --- |
| Who starts | The buyer (fills a form, books a demo) | You (email, LinkedIn, call) |
| What matters most | **Speed to lead**: respond in minutes | **Targeting**: the right accounts, at the right moment |
| What you build | Scoring + routing + instant alerts (webhooks) | Lists + enrichment + signals + sequences |

## Sales-led vs product-led

- **Sales-led** (Secfix): you must talk to sales to buy. "Book a demo", no public price.
- **Product-led:** you sign up and use it yourself (Slack, Notion), and sales gets involved later.

Secfix is sales-led, so the GTM system's job is to **feed BDRs and AEs the right accounts at the
right time, with context**.

## Where a GTM Engineer fits

Reps waste hours on: googling companies, copying data into the CRM, guessing who to call first,
missing hot leads because nobody noticed, writing the same research notes, cleaning duplicates.

A GTM Engineer replaces that with systems that:

- **find** companies that match the ICP
- **enrich** them with missing data
- **score** them so reps call the best first
- **route** each lead to the right rep instantly
- **alert** reps when something important happens
- **research and draft** with AI
- keep the **CRM clean**: no duplicates, no missing data

**Say it in one sentence:**

> "A GTM Engineer builds the systems (data pipelines, automations, AI tools) that help sales and
> marketing find the right customers and close deals faster, so the team spends time selling instead
> of doing manual work."

## Check yourself

1. What's the difference between an SDR and an AE?
2. A company filled a form and an SDR confirmed they need ISO 27001 within 3 months. Lead, MQL or
   SQL?
3. Why does "speed to lead" matter more for inbound than outbound?
4. Name three manual tasks a rep does that you could automate.

<details><summary>Answers</summary>

1. SDRs find and contact prospects and book first meetings; AEs run demos and close.
2. SQL: need and timing are confirmed by sales.
3. An inbound buyer is interested *right now* and is probably talking to competitors too; the first
   company to respond often wins.
4. For example: researching a company before a call, entering data into the CRM, deciding who to
   call first, finding contact emails, writing follow-ups.

</details>

Next: [02-icp-personas-buying-committee.md](02-icp-personas-buying-committee.md)
