# Signals and alerts ("who should I call today, and why?")

The batch pipeline keeps the CRM clean. **Signals** make it timely: something happened at an account
that makes a conversation likely to land now. The output is a short, explained alert to the owner.

## 10.1 Signal types

| Signal | Example | Source | Click or code |
| --- | --- | --- | --- |
| Funding | "Raised €12M Series A" | Crunchbase, Dealroom, news APIs, Vibe Prospecting events | Both |
| Hiring | Job post for "ISO 27001 Compliance Manager" | Company careers pages, LinkedIn Jobs, job APIs (e.g. Coresignal, TheirStack) | Code |
| Leadership change | New CTO / CISO | Sales Navigator alerts, UserGems, provider job-change data | Both |
| Champion moved | Former user joined a new company | UserGems, Common Room, your own CRM history | Both |
| Website visit | Pricing page viewed 3× this week | RB2B (US person-level), Dealfront/Leadfeeder (EU company-level), HubSpot | Click + webhooks |
| Product usage | Trial user invited 5 teammates | Product DB, Segment, PostHog | Code |
| Content engagement | Downloaded the SOC 2 checklist, attended webinar | HubSpot, webinar tool | Both |
| Third-party intent | Researching "SOC 2 compliance" | Bombora, G2 Buyer Intent | Click |
| Tech change | Added Okta, moved to AWS | BuiltWith, Wappalyzer | Code |
| Regulation | NIS2 / DORA applies to their sector | Your own mapping of industry → regulation | Code |
| Deal stage change | Deal moved to "demo booked" | CRM webhook | Code |

## 10.2 The process

1. **Detect**: poll sources on a schedule, or receive webhooks.
2. **Match** the signal to an account (domain first; fuzzy name for news).
3. **Diff** against the last snapshot: only *new* events count ("hiring" this week, not still hiring).
4. **Score** the signal (type weight × recency decay × account fit). Low-fit accounts don't alert.
5. **Dedupe alerts** (one alert per account per signal type per N days) and respect quiet hours.
6. **Route** to the owner (or the AE if there's an open deal, the AM if it's a customer).
7. **Alert with a reason and a next step**, in Slack, plus a CRM task.
8. **Measure**: alerts sent, acted on (task completed), meetings within 14 days.

## 10.3 The code

### Snapshot diff: only new things

```python
import json, pathlib
SNAP = pathlib.Path("state/job_posts.json")
previous = json.loads(SNAP.read_text()) if SNAP.exists() else {}

current = {domain: sorted(fetch_job_titles(domain)) for domain in target_domains}
new_events = []
for domain, titles in current.items():
    for t in set(titles) - set(previous.get(domain, [])):
        if re.search(r"(security|compliance|iso 27001|soc 2|ciso)", t, re.I):
            new_events.append({"domain": domain, "type": "hiring_security", "detail": t})
SNAP.write_text(json.dumps(current))
```

### Alert with reason, dedupe and routing

```python
from datetime import datetime, timedelta
COOLDOWN = timedelta(days=14)

def maybe_alert(event, account, sent_log):
    key = (event["domain"], event["type"])
    if key in sent_log and datetime.utcnow() - sent_log[key] < COOLDOWN:
        return False                                          # already told them recently
    if account["fit"] < 40:
        return False                                          # not worth a rep's time
    owner = account["deal_owner"] or account["owner"]
    text = (f":bell: *Call {account['company']} today* ({account['tier']}, fit {account['fit']})\n"
            f"Why: {event['detail']}\n"
            f"Who: {account['best_contact']} ({account['best_contact_title']})\n"
            f"Suggested opener: \"Saw you're hiring a {event['detail']}; usually means ISO 27001 is on the roadmap.\"")
    requests.post(os.environ["SLACK_WEBHOOK_URL"], json={"text": text}, timeout=10).raise_for_status()
    create_hubspot_task(owner, account, f"Signal: {event['detail']}")
    sent_log[key] = datetime.utcnow()
    return True
```

### CRM change → instant reaction (webhook)

HubSpot sends `propertyChange` events in batches and retries on failure, so dedupe by `eventId`
(see [data/webhook_events.json](../data/webhook_events.json), which has duplicates on purpose, and
[06-apis-and-webhooks/04-webhooks.md](../06-apis-and-webhooks/04-webhooks.md)).

## 10.4 Tools for the alert itself

| Tool | Way |
| --- | --- |
| Slack incoming webhook | Code (one POST) |
| Slack app with buttons ("Snooze", "Create task", "Not relevant") | Code (Bolt SDK) |
| HubSpot workflow → Slack notification / task | Click |
| Clay → Slack action | Click |
| n8n: schedule → HTTP → IF → Slack | Click + light code |

A related project in this portfolio applies the same detect → score → alert pattern to GPU
telemetry: [Real-time Data Pipeline with Signal Detection and Alerts](https://github.com/DhivyaBalakumar/Real-time-Data-Pipeline-with-Signal-Detection-and-Alerts).

## 10.5 Interview lines

> "A signal only becomes an alert if it's new, matches an account with decent fit, and hasn't been
> sent in the cooldown window. The alert says why, who, and a suggested opener, goes to the owner,
> or the AE if there's an open deal, and also creates a CRM task so we can measure whether alerts turn
> into meetings."
