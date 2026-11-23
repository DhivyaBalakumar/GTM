# 2. ICP, personas and the buying committee: who to sell to

## ICP: Ideal Customer Profile

The **type of company** that gets the most value, buys fastest and stays longest. Everything else
(lists, scoring, routing) is built on the ICP.

An ICP is written as **attributes you can check with data**:

| Attribute | Type of data | Example for Secfix (a reasonable guess; confirm with the team) |
| --- | --- | --- |
| Industry | Firmographic | Software / SaaS, fintech, healthtech, automotive suppliers |
| Size | Firmographic | 20–500 employees |
| Region | Firmographic | EU, especially DACH (Germany, Austria, Switzerland) and Benelux |
| Sells to | Firmographic | Sells to enterprises (who demand certificates) |
| Tech stack | Technographic | Uses AWS / Google Workspace / Microsoft 365 (Secfix integrates with these) |
| Compliance status | Custom | No ISO 27001 / SOC 2 yet, or renewal coming up |
| Funding | Firmographic | Recently funded (moving upmarket) |

**Firmographics** = facts about the company (industry, size, location, revenue, funding).
**Technographics** = the tools they use (often detected from their website or job ads).

**Anti-ICP** (who *not* to target) matters too: companies too small to need it, companies that
already have a certificate and a long contract with a competitor, consumers (gmail addresses),
students, competitors.

## Personas

The **types of people** you talk to inside an ICP company.

| Persona | What they care about | What message works |
| --- | --- | --- |
| CTO / Head of Engineering | Not wasting engineers' time on audits | "Automated evidence collection; 250+ checks run by themselves" |
| Head of IT / Security | Getting it done without chaos | "Experts guide you; one place for policies and evidence" |
| CEO / Founder | Winning the big deal, speed | "Certified in weeks, so the enterprise deal doesn't stall" |
| CFO | Cost vs consultants | "Cheaper and faster than months of consultants" |
| Head of Sales | Security questionnaires slowing deals | "AI questionnaire answering; certificate in hand" |

## Account vs contact vs lead

- **Account** = a company (PeopleCo GmbH).
- **Contact** = a specific person at an account (Anna Müller, CTO).
- **Lead** = a person or company that *might* buy and isn't qualified yet. In many CRMs, "lead" is
  also a lifecycle stage.

## The buying committee

B2B purchases are rarely made by one person. The job post says "model accounts, contacts and
**buying committees**". That means your CRM data should know, for each account, *who* plays which
role:

| Role in the decision | Usually |
| --- | --- |
| Champion (pushes for it) | Head of IT / Security |
| Economic buyer (signs) | CEO or CFO |
| Technical evaluator | CTO |
| Influencer / blocker | Legal, procurement |

**Why it matters for a GTM Engineer:** a deal with only one contact is risky (if they leave, the deal
dies). A useful system flags "tier-A account with no economic buyer contact yet" so the rep can fill
the gap. In data terms: contacts are linked (associated) to accounts, each with a role property.

## TAM, segments and territories

- **TAM (total addressable market):** every company that fits the ICP. You can estimate it with a
  data provider query ("software, 20–500 staff, DACH").
- **Segments:** slices of the market treated differently, e.g. SMB (20–100), mid-market (100–500),
  enterprise (500+).
- **Territories:** how accounts are split between reps, usually by region or language (German
  speakers handle DACH) or by segment.

## Check yourself

1. Write a 5-line ICP for Secfix using only attributes you could check with data.
2. Why is a gmail.com sign-up usually not a lead for Secfix?
3. A tier-A deal has only one contact, a junior engineer. What should the system flag, and why?

<details><summary>Answers</summary>

1. E.g. industry in {software, fintech}; 20–500 employees; HQ in DE/AT/CH/NL/BE/LU; no ISO 27001
   listed; raised funding in the last 12 months.
2. It's a personal address, so there's no company to sell to (and no domain to match).
3. "No decision-maker contact": deals need a champion and an economic buyer; single-threaded deals
   are fragile.

</details>

Next: [03-signals-and-intent.md](03-signals-and-intent.md)
