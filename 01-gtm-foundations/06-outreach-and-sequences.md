# 6. Outreach and sequences

## Sequence (cadence)

A planned series of outreach steps over days, run by a tool (HubSpot sequences, Outreach, Salesloft,
lemlist, Instantly). Example for a tier-B account:

| Day | Step |
| --- | --- |
| 1 | Email 1: short, relevant, one question |
| 3 | LinkedIn connection request |
| 5 | Email 2: a useful resource (e.g. NIS2 checklist) |
| 8 | Call |
| 12 | Email 3: "should I close the loop?" |

A reply or a booked meeting **exits** the contact from the sequence automatically.

## What makes cold outreach work

- **Relevant:** tied to a real signal ("saw you're hiring a compliance manager").
- **Short:** 50–120 words, one clear ask.
- **About them, not you:** their problem (an enterprise deal stuck on security review), not your
  features.
- **Personalised at scale:** the first line uses data (signal, industry, tech), often written with AI
  and checked by rules.

Example:

> Subject: ISO 27001 for the ING partnership?
>
> Hi Anna, congrats on the ING partnership. Banks usually ask partners for ISO 27001 before go-live,
> and getting it the traditional way takes 6–12 months. We help fintechs like yours get certified in
> weeks with automated evidence collection and an expert alongside. Worth a 20-minute look next
> week?

## Deliverability basics (why emails land in spam)

| Term | Meaning |
| --- | --- |
| SPF, DKIM, DMARC | DNS records that prove your emails really come from your domain |
| Warm-up | Slowly increasing sending volume on a new mailbox |
| Sending limits | Sending too many per mailbox per day gets you flagged |
| Bounce rate | Emails to addresses that don't exist; high bounces hurt your reputation, so verify emails first |
| Secondary domains | Outbound often sends from e.g. `getsecfix.com` to protect the main domain |

A GTM Engineer often owns the data side: verified emails, no duplicates in sequences, no contacting
existing customers or open deals, unsubscribes respected (GDPR).

## Metrics

| Metric | Meaning | Rough healthy range for B2B cold outbound |
| --- | --- | --- |
| Open rate | Opened / delivered | Unreliable now (privacy features inflate it) |
| Reply rate | Replies / delivered | ~2–8% |
| Positive reply rate | Interested replies / delivered | ~0.5–3% |
| Meeting rate | Meetings booked / contacted | ~0.5–2% |
| Bounce rate | Bounced / sent | Under 2–3% |

## Interview question: "Reply rates dropped 30%. What do you check?"

Work from data and infrastructure to message:

1. **Is it real?** Same time period, same segment? Did tracking change?
2. **Deliverability:** bounce rate up? Spam placement? Did DNS records (SPF/DKIM/DMARC) break? Did
   volume per mailbox jump?
3. **Data:** a new list source with worse emails? Wrong segment targeted? Duplicates?
4. **Targeting:** are we hitting the ICP, or did scoring change?
5. **Message:** new copy? Stale signals? Seasonality (holidays)?
6. **Fix and measure:** change one thing at a time; compare against a control group.

Next: [07-metrics.md](07-metrics.md)
