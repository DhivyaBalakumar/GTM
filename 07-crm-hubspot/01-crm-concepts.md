# 1. CRM concepts

## What a CRM is

**CRM = customer relationship management system.** The shared database a sales team works from:
every company, person, deal and interaction. HubSpot and Salesforce are the most common for B2B.

**"Single source of truth"** means every rep trusts the CRM is complete, correct and current, so
nobody keeps a private spreadsheet. That trust is fragile: a few duplicates or wrong owners and reps
go back to spreadsheets. Your job is to earn and keep it.

## Core objects

| Object | What it is | Secfix example |
| --- | --- | --- |
| **Company** (account) | A business you sell to | PeopleCo GmbH |
| **Contact** | A person, usually linked to a company | Anna Müller, CTO |
| **Deal** (opportunity) | A potential sale, with a value and a stage | "PeopleCo ISO 27001", €18,000, Demo done |
| **Activity / engagement** | Calls, emails, meetings, notes, tasks | "Demo call, 20 Nov" |
| **Ticket** | A support request (mostly for customer success) | — |
| **Custom objects** | Anything else you need (higher plans) | "Audit", "Certificate" |

## Properties

The **fields** on a record. HubSpot has default ones (name, domain, industry, numberofemployees,
hubspot_owner_id, lifecyclestage) and you can create **custom properties** (fit_score, score_reasons,
last_signal, signal_date).

Property types: single-line text, number, date, dropdown (enumeration), checkbox, multi-select.
Each property has an **internal name** (`fit_score`) used by the API and a **label** ("Fit score")
shown to people.

A property can be marked **unique** ("require unique values"). That's what makes upserts by domain or
by an external ID possible.

## Associations

Links between records: contact ↔ company, deal ↔ company, deal ↔ contact. An association can have a
**label** (e.g. "Decision maker", "Champion"). This is how you model a **buying committee**: contacts
associated with the company, each labelled with their role.

## Pipelines and stages

A **deal pipeline** is the ordered list of stages a deal moves through:

`Meeting booked → Discovery → Demo done → Proposal sent → Negotiation → Closed won / Closed lost`

Each stage can have a win probability, used for forecasting. Stage changes are the classic webhook
trigger ("deal moved to Demo booked → alert the AE").

## Lifecycle stages

Where a contact or company is in the funnel:

`Subscriber → Lead → MQL → SQL → Opportunity → Customer → Evangelist`

Rules usually move records forward automatically (for example, when a deal is created the contact
becomes an Opportunity).

## Owners and teams

Each record has an **owner** (`hubspot_owner_id`), the rep responsible. Teams group reps (DACH team,
Benelux team). Routing sets the owner; your pipeline should **never steal** an existing owner.

## Lists, views, workflows (the no-code side)

- **Active lists:** auto-updating segments ("tier A companies in DE with no open deal").
- **Saved views:** filtered tables reps use daily.
- **Workflows:** no-code automation inside HubSpot (if property X changes, then do Y).
- **Sequences:** automated email follow-ups for reps.
- **Reports and dashboards.**

A GTM Engineer uses these too, but writes code when logic is complex, crosses tools, needs external
data, or needs AI.

## Data model: how accounts, contacts and deals fit together

```
Company (unique domain) 1 ──── many Contacts (unique email), each with a role label
        │
        └──── many Deals (each with a stage, amount, owner, associated contacts)
```

In SQL terms: `contacts.account_id` and `deals.account_id` are foreign keys to `accounts.id`. That's
exactly the tables in [05-sql](../05-sql).

## What makes CRM data bad (and what you build to prevent it)

| Problem | Cause | Fix you build |
| --- | --- | --- |
| Duplicate companies | Imports and integrations creating instead of upserting; names spelled differently | Normalise domains, upsert by unique domain, dedupe jobs |
| Missing fields | Manual entry, no enrichment | Enrichment pipeline that fills gaps only |
| Wrong owners / unassigned | No routing rules | Automated routing with a fallback |
| Stale data | Nobody updates it | Scheduled refresh, freshness dates |
| Overwritten good data | Integrations writing blanks or old values | Never write blanks; field ownership |
| Unused fields | Too many properties | Keep the data model small and documented |

## Check yourself

1. What does marking `domain` as a unique property make possible?
2. How would you represent "Anna is the champion at PeopleCo" in a CRM?
3. Name three things that destroy reps' trust in a CRM.

Next: [02-hubspot-api.md](02-hubspot-api.md)
