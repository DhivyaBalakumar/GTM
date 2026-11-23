# 3. Signals and intent: knowing *when* to reach out

## The idea

The ICP tells you **who** fits. **Signals** tell you **when** they're likely to buy. A perfect-fit
company that has no reason to act this quarter will ignore you; the same company the week a big
customer demands ISO 27001 will take the call.

**Signal** = a visible event suggesting the need is real *now*.
**Signal-based outbound** = reaching out because of a specific event, and saying so ("saw you're
hiring a compliance manager…").

## Signals that matter for Secfix

| Signal | Why it suggests a need | Where the data comes from | Strength |
| --- | --- | --- | --- |
| Job ad mentions ISO 27001, SOC 2, TISAX, "compliance", "information security" | They're staffing up for it | Job boards, LinkedIn jobs, the company's careers page | Strong |
| Hired a first security / IT lead | New owner of the problem, building a plan | LinkedIn, news | Strong |
| Raised funding (seed, Series A/B) | Moving upmarket to enterprise customers who demand certificates | Crunchbase, news APIs, press releases | Medium–strong |
| Announced an enterprise / bank / automotive customer | That customer will demand proof of security | News, the company's website | Strong |
| Expanding to the US | SOC 2 will be asked for | News, job ads in the US | Medium |
| Falls under NIS2 / DORA | Legal obligation | Industry + size rules | Medium |
| Visited Secfix's pricing or ISO 27001 pages | Actively researching | Website visitor tracking | Strong (intent) |
| Downloaded a guide, attended a webinar | Learning about the topic | Marketing tools | Medium |
| Competitor contract renewal coming up | A window to switch | Hard to get; sometimes from conversations | Medium |
| Negative: just got certified with a competitor | Not buying for a while | Their website trust page | Negative |

## Fit vs intent

| | Fit | Intent |
| --- | --- | --- |
| Question | "Are they the right *kind* of company?" | "Are they likely to buy *now*?" |
| Changes | Slowly (size, industry) | Quickly (this week's events) |
| Examples | Industry, size, region, tech stack | Signals above |
| Decay | Rarely | Yes: a funding round from 18 months ago means little |

Good scoring combines both (next lesson).

## Signal decay

Signals lose value over time. A job post from yesterday is hot; one from eight months ago is cold.
Common approach: full points within 30 days, half within 90, none after. In code:

```python
from datetime import date

def signal_points(event_date: date, full_points: int, today: date) -> float:
    days = (today - event_date).days
    if days <= 30:
        return full_points
    if days <= 90:
        return full_points / 2
    return 0
```

## From signal to action: the "call today" alert

A signal is useless unless it reaches the right rep with context. A good alert answers four
questions in one line:

> **Who** to call · **why now** · **why they fit** · **who owns it**
>
> "Lena: call PeopleCo today. Hiring an ISO 27001 Compliance Manager (posted 2 days ago), Series A
> last month, 120 staff, Berlin, software."

## Common mistakes

- **Too many alerts:** reps stop reading them (alert fatigue). Only alert on tier A, or send one
  daily digest.
- **No reason given:** "Score 87" means nothing; reasons drive action.
- **Stale signals:** forgetting decay.
- **Same signal twice:** alerting again every run because nothing remembers it was sent
  (idempotency again).

## Check yourself

1. Is "120 employees" a signal? Why or why not?
2. Write a one-line alert for: Nordbank Tech (NL, fintech, 80 staff) announced a partnership with
   ING yesterday; owner Tom.
3. Why should signals decay?

<details><summary>Answers</summary>

1. No, it's a fit attribute: it describes who they are, not a recent event.
2. "Tom: call Nordbank Tech today. Announced an ING partnership yesterday (banks demand security
   proof); 80-person fintech in NL."
3. The need may already be solved, or the moment has passed; old signals waste reps' time.

</details>

Next: [04-lead-scoring.md](04-lead-scoring.md)
