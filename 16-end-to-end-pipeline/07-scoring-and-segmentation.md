# Step 7: Scoring and segmentation

- **Scoring** answers *"how good, and how urgent?"*: a number and a tier (A/B/C/D) with reasons.
- **Segmentation** answers *"which group, so which message?"*: vertical × size × persona → a sequence.

They're different: two leads can both score 85 but need different messages (a fintech CISO vs a SaaS
founder).

## 7.1 Tools

| Tool | What it does | Click or code |
| --- | --- | --- |
| **Python rules + config** | Transparent, testable fit + intent scoring | Code |
| **SQL** (`CASE WHEN`) | Scores and segments in the warehouse | Code |
| **HubSpot lead scoring** (score properties, Breeze) | Points for properties and behaviours | Click |
| **Salesforce Einstein / Agentforce scoring** | Predictive scores | Click |
| **Clay formula columns** | Score inside the table before pushing | Click |
| **MadKudu, 6sense, Demandbase, Pocus, Common Room** | Predictive fit/intent, ABM, product signals | Click (config) |
| **Claude** | Classify unstructured inputs (website text, job post, reply) into fixed categories | Code |
| **scikit-learn logistic regression** | Learn weights from won/lost history once you have enough data | Code |

## 7.2 The ICP and personas (inputs)

| ICP field | Example (EU compliance SaaS) |
| --- | --- |
| Countries | DACH core, then Benelux, rest of EU |
| Industries | software / SaaS, fintech, healthtech, insurtech, HR tech |
| Size | 20–500 employees |
| Triggers | funding, first enterprise customer, hiring security/compliance roles, new regulation (NIS2, DORA) |
| Buying committee | Economic buyer (CEO/CFO), champion (CTO, Head of IT), technical evaluator (security lead), blocker (procurement/legal) |

Background: [01-gtm-foundations/02-icp-personas-buying-committee.md](../01-gtm-foundations/02-icp-personas-buying-committee.md).

## 7.3 The process

1. **Fit score** (does it look like a customer?): firmographics + persona.
2. **Intent score** (is now the time?): signals + engagement, with **decay** (a 6-month-old funding
   round counts less than last week's).
3. **Total + tier** with thresholds from config.
4. **Reasons** in plain words for every point given. Reps ignore scores they can't read.
5. **Segment** each lead and map segment → sequence/playbook.
6. **Account roll-up**: account score = best contact + coverage of the buying committee.
7. **Calibrate** monthly against outcomes (chapter 12): do A-tier leads really book more meetings?

## 7.4 Fit + intent, with reasons

```python
WEIGHTS = {"country": 15, "core_country_bonus": 5, "industry": 20, "size": 15, "persona": 10,
           "senior": 5, "signal_funding": 20, "signal_hiring": 15, "signal_inbound": 15}
TIERS = [(80, "A"), (60, "B"), (40, "C"), (0, "D")]

def score(contact, account, icp, w=WEIGHTS):
    fit, intent, reasons = 0, 0, []
    if account["country"] in icp["countries"]:
        fit += w["country"]; reasons.append(f"{account['country']} in target region")
    if account["industry"] in icp["industries"]:
        fit += w["industry"]; reasons.append(account["industry"])
    if account["employees"] and icp["min"] <= account["employees"] <= icp["max"]:
        fit += w["size"]; reasons.append(f"{account['employees']} staff")
    if contact["function"] in icp["buyer_functions"]:
        fit += w["persona"]; reasons.append(f"{contact['function']} buyer")
    if "funding" in account["signals"]:
        intent += w["signal_funding"]; reasons.append("recent funding")
    total = min(100, fit + intent)
    tier = next(t for floor, t in TIERS if total >= floor)
    return {"fit": fit, "intent": intent, "score": total, "tier": tier, "reasons": reasons}
```

### Signal decay

```python
import math
def decayed(points, days_ago, half_life_days=30):
    return points * math.pow(0.5, days_ago / half_life_days)    # 30 days old = half the points

intent = sum(decayed(SIGNAL_POINTS[s["type"]], s["days_ago"]) for s in account["signals"])
```

### Negative scoring

Subtract for: personal email, student/intern, competitor, wrong country, very small companies,
unsubscribed, "not interested" reply in the last 90 days.

### SQL version

```sql
SELECT c.email,
       (CASE WHEN a.country IN ('DE','AT','CH') THEN 20 WHEN a.country IN ('NL','BE','LU','FR') THEN 15 ELSE 0 END
      + CASE WHEN a.industry IN ('software','fintech','healthtech') THEN 20 ELSE 0 END
      + CASE WHEN a.employees BETWEEN 20 AND 500 THEN 15 ELSE 0 END
      + CASE WHEN c.title ~* '(cto|ciso|head of (it|security|engineering))' THEN 15 ELSE 0 END) AS fit_score
FROM contacts c JOIN accounts a ON a.domain = c.domain;
```

### When to learn the weights

Rules first (you have no data yet and they're explainable). Once you have a few hundred outcomes,
fit a logistic regression on won/lost or meeting/no-meeting and compare its ranking with your rules.

```python
from sklearn.linear_model import LogisticRegression
X = df[["is_dach", "is_software", "size_in_range", "is_security_persona", "had_funding"]]
y = df["meeting_booked"]
model = LogisticRegression().fit(X, y)
print(dict(zip(X.columns, model.coef_[0].round(2))))   # which features actually predict meetings
```

## 7.5 Segmentation

| Dimension | Values | Drives |
| --- | --- | --- |
| Vertical | software, fintech, health, other | Message angle (fintech → DORA + SOC 2; health → patient data + ISO 27001) |
| Size band | smb (< 50), mid (50–250), upper_mid (> 250) | Team (BDR vs AE), price point, proof points |
| Persona | founder_exec, tech_lead, security_lead, finance | Pain and wording |
| Tier | A/B/C/D | Channel and effort (A: personal research + call; D: nurture newsletter) |
| Lifecycle | new, engaged, MQL, SQL, opportunity, customer | Which motion applies |
| Trigger | funding, hiring, regulation, inbound | First line of the message |

```python
def segment(contact, account):
    emp = account["employees"] or 0
    size = "smb" if emp < 50 else "mid" if emp <= 250 else "upper_mid"
    vertical = {"fintech": "fintech", "insurtech": "fintech", "healthtech": "health"}.get(
        account["industry"], "software" if account["industry"] in {"software", "saas"} else "other")
    persona = {"security": "security_lead", "engineering": "tech_lead", "it": "tech_lead",
               "executive": "founder_exec"}.get(contact["function"], "other")
    return f"{vertical}:{size}:{persona}"

SEQUENCE_FOR = {"fintech": "seq_fintech_dora_soc2", "health": "seq_health_iso27001",
                "software": "seq_saas_iso27001_fast", "other": "seq_generic_nurture"}
```

In pandas: `df.groupby(["vertical", "size_band", "persona"]).size()` shows how big each segment is.
A segment with 4 people doesn't deserve its own sequence; merge it.

### Classifying with Claude (only where rules can't)

Give Claude a closed set of labels and validate the answer (module [09](../09-claude-and-ai)):
"Based on this job post, is the company building a security/compliance function? one of
`yes_dedicated_role`, `yes_mentioned`, `no`" → becomes a signal.

## 7.6 Demo output

On the sample data the demo scores 9 remaining contacts: `lena@opalanalytics.de` is **A 90** (DE,
software, 25 staff, CEO, seed funding), three are B (Kite Labs, Fjord Systems, Kranich Logistik),
two C, three D (US retail, UK media, 600-person automotive). Each comes with its reasons and a
segment like `software:smb:founder_exec`.

## 7.7 Interview lines

> "I split fit from intent: fit says whether they look like a customer, intent says whether now is
> the time, and intent decays. Every point has a written reason that goes into the CRM, so reps can
> trust it. I start with rules from config and only move to learned weights once there are enough
> outcomes to check against."

> "Segmentation is separate from scoring: it decides the message. Vertical, size and persona map to a
> sequence, and tiny segments get merged."
