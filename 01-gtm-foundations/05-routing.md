# 5. Lead routing: getting each lead to the right rep, instantly

## What routing is

Deciding **automatically** which rep owns a new lead or account, and telling them. Bad routing means
leads sit unassigned for days, two reps call the same company, or a German-speaking prospect gets an
English-only rep.

## The rules, in priority order

Order matters: the first rule that matches wins.

1. **Existing owner first.** If the company is already in the CRM with an owner, they keep it.
   Never steal accounts (reps hate it, and it confuses the customer).
2. **Existing open deal:** route to the deal owner.
3. **Territory / language:** DACH → German-speaking team; Benelux → Benelux team.
4. **Segment / size:** enterprise accounts to senior AEs, SMB to BDRs.
5. **Round-robin** within the matching team, so leads are spread evenly.
6. **Fallback:** if nothing matches, assign to a named person (head of sales) or a queue. **No lead
   is ever unassigned.**
7. **Low score:** tier C goes to a nurture queue, not a rep.

## Round-robin in Python

`itertools.cycle` hands out names in turn forever:

```python
from itertools import cycle

DACH_TEAM = cycle(["lena", "jonas"])
OTHER_TEAM = cycle(["maria", "tom"])

next(DACH_TEAM)  # 'lena'
next(DACH_TEAM)  # 'jonas'
next(DACH_TEAM)  # 'lena' again
```

The full routing function (always return the **reason** too, for logging and trust):

```python
def route(lead, existing_owner=None):
    if existing_owner:
        return existing_owner, "existing owner"
    if lead.get("tier") == "C":
        return "nurture-queue", "tier C goes to nurture"
    if lead.get("country") in {"DE", "AT", "CH"}:
        return next(DACH_TEAM), "DACH round-robin"
    if lead.get("country"):
        return next(OTHER_TEAM), "general round-robin"
    return "head-of-sales", "no country: fallback"
```

## Speed to lead

For inbound leads (someone books a demo), responding in **minutes** instead of hours dramatically
raises the chance of a meeting, because the buyer is interested *now* and may be talking to
competitors. That's why inbound routing uses **webhooks** (instant) rather than an hourly batch job.

## Lead-to-account matching

A new inbound lead `anna@peopleco.de` should be matched to the existing account `peopleco.de` before
routing, so it goes to PeopleCo's owner. That's the email-domain → company-domain normalisation you
learn in [data quality](../08-data-quality).

## Production concerns

- **State:** a simple `cycle` resets when the script restarts. In production, store "who got the last
  lead" in the CRM or a database, or count current open leads per rep and pick the lowest.
- **Out of office:** skip reps who are away (a simple availability list).
- **Fairness and capacity:** weight by rep capacity if some reps handle more.
- **Audit trail:** log every routing decision with its reason.

## Check yourself

1. A lead from Austria arrives; the company already exists in the CRM owned by Maria. Who gets it?
2. Why must there always be a fallback owner?
3. What's the problem with `cycle()` in a script that restarts every hour?

<details><summary>Answers</summary>

1. Maria (existing owner wins).
2. Otherwise some leads silently go unassigned and are never contacted.
3. It always starts from the first name again, so the first rep in each list gets more leads.

</details>

Next: [06-outreach-and-sequences.md](06-outreach-and-sequences.md)
