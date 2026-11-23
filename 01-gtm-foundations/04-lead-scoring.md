# 4. Lead and account scoring

## Why score at all

Reps have limited hours. Scoring puts a number on every account so they call the best ones first.
A good score is **simple, explainable and checked against results**.

## The standard design: fit + intent = 0–100

| Part | Points | Built from |
| --- | --- | --- |
| **Fit** (who they are) | 0–60 | Industry, size, region, tech, compliance status |
| **Intent** (what they're doing) | 0–40 | Signals, with decay |
| **Total** | 0–100 | Fit + intent |

Then **tiers**: A ≥ 75 (call this week), B 50–74 (sequence), C < 50 (nurture or ignore).

## A worked example

| Rule | Points |
| --- | --- |
| Industry in {Software, Fintech, Healthtech} | +25 |
| 20–500 employees | +20 |
| Country in DACH or Benelux | +15 |
| Raised funding in the last 90 days | +20 |
| Hiring for security / compliance | +20 |

PeopleCo: software (+25), 120 staff (+20), DE (+15), Series A last month (+20), hiring an ISO
manager (+20) = **100, tier A**.

## Always keep the reasons

```python
def score(company: dict) -> dict:
    points, reasons = 0, []
    if company.get("industry") in {"Software", "Fintech", "Healthtech"}:
        points += 25
        reasons.append(f"industry: {company['industry']}")
    employees = company.get("employees") or 0
    if 20 <= employees <= 500:
        points += 20
        reasons.append(f"{employees} employees")
    if company.get("country") in {"DE", "AT", "CH", "NL", "BE", "LU"}:
        points += 15
        reasons.append(f"based in {company['country']}")
    if company.get("raised_recently"):
        points += 20
        reasons.append("raised funding recently")
    if company.get("hiring_security"):
        points += 20
        reasons.append("hiring for security/compliance")
    tier = "A" if points >= 75 else "B" if points >= 50 else "C"
    return {"score": points, "tier": tier, "reasons": reasons}
```

Reps ignore numbers they don't understand. "Score 100: software, 120 employees, DE, raised
recently, hiring for security" tells them *why* to call and *what to say*.

## Rules vs models

| | Rules (points) | Machine-learning model |
| --- | --- | --- |
| Explainable | Yes | Hard |
| Needs historical data | No | Yes, lots of won/lost deals |
| Easy to change | One line | Retrain |
| Right for | A young company, a first system | Many years of data |

For a first GTM Engineer at a 36-person company: **start with rules**. Say so in interviews and
explain why.

## How to validate and improve a score

1. Take the last 6–12 months of deals. Score the accounts as they looked *before* the deal.
2. Compare: do tier-A accounts actually convert to meetings and wins more than tier B and C?
3. If not, adjust weights. For example, if hiring signals predict meetings far better than funding,
   raise the hiring weight.
4. Ask reps: "Which tier-A accounts were rubbish? Which tier-C ones were great?" Their examples
   reveal missing rules.
5. Re-check every quarter.

## Edge cases to handle in code

- Missing data (no employee count): score what you can; don't crash; maybe flag "needs enrichment".
- **Boundaries:** is 20 employees inside 20–500? Decide and **test it** (a classic bug is `> 20`
  instead of `>= 20`).
- Ranges like "51-200": convert to a number first (midpoint 125).
- Negative signals: subtract points (already a competitor's customer).

## Interview question: "How would you design lead scoring for Secfix?"

> "Fit plus intent, 0 to 100. Fit, up to 60, from the ICP: industry, size, region, and whether they
> already have a certificate. Intent, up to 40, from signals like security hiring, funding and
> pricing-page visits, decaying over 90 days. Tiers: A at 75 and above goes straight to a rep with
> an alert, B goes into a sequence, C into nurture. Every score stores its reasons so reps trust it.
> I'd start with simple rules because they're explainable and need no history, then check after a
> quarter whether tier A really converts better and adjust weights with the reps."

Next: [05-routing.md](05-routing.md)
