# Step 10: Outreach and sequencing

**Goal:** the right contacts get the right multi-step message (email, LinkedIn, call) from the right
rep, at a volume that keeps your sending domains healthy, and every reply, bounce and meeting flows
back into the CRM.

**House rule in this repo: the pipeline drafts, a human approves and sends.** Nothing here sends
email on anyone's behalf.

## 9.1 Tools

| Tool | What it's for | Click or code |
| --- | --- | --- |
| **Apollo Sequences** | Email + call + LinkedIn task steps, built on Apollo's own data | Click; API to add contacts to a sequence |
| **HubSpot Sequences** (Sales Hub) | 1:1 sequences from the rep's inbox, tasks, logs to CRM | Click; enrol via API on some tiers |
| **Outreach, Salesloft** | Enterprise sales engagement, cadences, dialer, analytics | Click; full APIs |
| **lemlist, Instantly, Smartlead** | High-volume cold email, inbox rotation, warm-up, multichannel (lemlist) | Click; APIs + webhooks for replies |
| **HeyReach, Expandi, Dripify** | LinkedIn automation (connection requests, messages) | Click. Careful: LinkedIn limits automation, accounts can be restricted |
| **Aircall, Kixie, Orum, Nooks** | Dialers / parallel dialing | Click |
| **Claude** (API or Claude Code skills) | Research briefs, first lines, segment-specific drafts, reply classification | Code |
| **Clay AI columns** | Personalised first lines at table scale | Click |
| **Google Postmaster Tools, MXToolbox, mail-tester** | Deliverability monitoring | Click |

## 9.2 The process

1. **Pick who enters** (tier A/B, not suppressed, verified email, owner assigned).
2. **Pick the sequence by segment** (chapter 07) and the **channel mix by tier**:
   - A: researched first touch + LinkedIn + call by the owner.
   - B: segment sequence with a personalised first line.
   - C: lighter sequence; D: marketing newsletter only.
3. **Write the copy per segment** (pain + proof + small ask), then **personalise one line** per
   contact from a real signal.
4. **Human review**: owner approves drafts (or at least the segment template + a sample).
5. **Enrol** via the tool's UI or API, from the rep's own mailbox.
6. **Throttle**: daily caps per mailbox, spread over the day.
7. **Sync back** replies, bounces, unsubscribes, meetings to the CRM (webhooks).
8. **Classify replies** (interested / not now / wrong person / unsubscribe / out of office) and act:
   unsubscribe → suppress everywhere; wrong person → find the referral; OOO → pause and resume.
9. **Measure** per sequence and step: delivered, open (unreliable), reply, positive reply, meeting.

## 9.3 A typical cold sequence (B tier, 12 days)

| Day | Channel | Step |
| --- | --- | --- |
| 1 | Email | Trigger-based first touch (funding / hiring / regulation), one question |
| 2 | LinkedIn | Connection request, no pitch |
| 4 | Email | Same thread: proof point (similar company, outcome, time to certification) |
| 7 | Call | Call + voicemail referencing the email |
| 9 | LinkedIn | Message if connected: useful resource (checklist) |
| 12 | Email | Breakup: "should I close the loop?" |

Copywriting guide: [01-gtm-foundations/06-outreach-and-sequences.md](../01-gtm-foundations/06-outreach-and-sequences.md).

## 9.4 Deliverability: the part that decides whether anything lands

| Item | What to do |
| --- | --- |
| **Separate sending domains** | Send cold email from look-alike domains (`getpeopleco.com`), never your main domain |
| **SPF, DKIM, DMARC** | Set all three on every sending domain (Gmail and Yahoo require them for bulk senders since Feb 2024) |
| **One-click unsubscribe** | `List-Unsubscribe` + `List-Unsubscribe-Post` headers; honour within 2 days |
| **Spam complaint rate** | Keep under 0.1%, never reach 0.3% (Gmail's threshold) |
| **Warm-up** | New inboxes ramp up over 2–4 weeks |
| **Volume per inbox** | Commonly ~30–50 cold emails/day per mailbox; scale with more inboxes, not more volume per inbox |
| **Bounce rate** | Verified emails only; keep bounces under ~2% |
| **Plain text, few links, no tracking pixel on first touch** | Better inbox placement |

## 9.5 The code

### Drafting with Claude: structured, grounded, validated

```python
import anthropic, json
client = anthropic.Anthropic()

SYSTEM = """You write first-touch B2B emails for a compliance automation company.
Rules: under 90 words; one specific, verifiable reference to the trigger provided; no invented facts,
numbers or customer names; one question as the call to action; no 'I hope this finds you well'.
Return JSON: {"subject": str, "body": str, "trigger_used": str}"""

def draft(contact, account, segment_template):
    facts = {"first_name": contact["first_name"], "company": account["company"],
             "country": account["country"], "signals": account["signals"],
             "segment_angle": segment_template["angle"], "proof_point": segment_template["proof"]}
    msg = client.messages.create(model="claude-haiku-5-5", max_tokens=400, temperature=0.3,
                                 system=SYSTEM,
                                 messages=[{"role": "user", "content": json.dumps(facts)}])
    out = json.loads(msg.content[0].text)
    assert len(out["body"].split()) <= 90
    assert out["trigger_used"] in account["signals"] or out["trigger_used"] == "none"
    return {**out, "to": contact["email"], "status": "DRAFT - needs approval"}
```

Guardrails: pass **only facts you have** (so it can't invent), validate length and that the trigger
is one you supplied, keep a human approval step, and log prompt + output for review. Check current
model names in Anthropic's docs.

### Enrolling via API (shape)

```python
# Apollo: add contacts to an existing sequence (contact IDs must already exist in Apollo)
session.post(f"https://api.apollo.io/api/v1/emailer_campaigns/{sequence_id}/add_contact_ids",
             json={"contact_ids": ids, "emailer_campaign_id": sequence_id,
                   "send_email_from_email_account_id": mailbox_id}, timeout=30)
```

Each tool's enrolment endpoint differs (Instantly/Smartlead "add leads to campaign", Outreach
"sequenceStates"). Check the docs; the pattern is always: existing contact ID + sequence ID + sending
mailbox.

### Replies back into the CRM (webhook) + classification

```python
@app.post("/webhooks/outreach")
def outreach_event():
    e = verify_and_parse(request)
    if e["type"] == "reply":
        label = classify_reply(e["text"])      # rules first: "unsubscribe", "out of office"; Claude for the rest
        if label == "unsubscribe":
            add_to_suppression(e["email"])     # everywhere, permanently
        hubspot_log_email(e["email"], e["text"], label)
        if label == "interested":
            slack(f"Positive reply from {e['email']}: book it! Owner: {owner_of(e['email'])}")
    elif e["type"] == "bounce":
        mark_invalid(e["email"])
    return "", 200
```

In the demo: `draft_first_touch()` writes template-based drafts for A/B contacts with an owner
(4 on the sample data), using the account's signal as the hook, and marks them
`DRAFT - needs human approval`.

## 9.6 Interview lines

> "Segment decides the template, the signal decides the first line, and the tier decides the channel
> mix. Claude only gets facts we have, returns JSON we validate, and a rep approves before anything
> goes out. Replies, bounces and unsubscribes come back by webhook, and an unsubscribe suppresses the
> person everywhere."

> "Deliverability is infrastructure: separate sending domains, SPF/DKIM/DMARC, warm-up, low daily
> volume per inbox, verified emails only."
