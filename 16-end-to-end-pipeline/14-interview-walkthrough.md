# Telling the pipeline story in an interview

## The 2-minute walkthrough (draw the one-page diagram while you talk)

> "I think of it as eleven steps with one rule: the CRM is the single source of truth, and every step
> is safe to re-run.
>
> **Collect:** I pull from the databases like Apollo or Clay, inbound sources like forms and
> webinars, signal sources, and always the CRM itself. Search is cheap and enrichment costs credits,
> so I search wide and enrich only what passes the ICP filters. API calls paginate, back off on 429s
> and respect a credit budget.
>
> **Clean:** everything maps into one schema, and each field type is normalised, domain above all,
> because it's the account key. Rows that fail validation go to quarantine with a reason.
>
> **Dedupe:** email for contacts, domain for companies, fuzzy names only inside blocks with strict
> thresholds, and field-by-field survivorship with lineage. I dedupe against the CRM too, which
> usually turns up duplicates already in there.
>
> **Enrich:** only missing or stale fields, through a waterfall with a cache, then verify emails.
>
> **Suppress:** customers, open deals, unsubscribes, competitors and role inboxes never get cold
> email. A signal on an open-deal account becomes a task for the AE instead.
>
> **Score and segment:** fit plus intent with written reasons, then vertical, size and persona pick
> the sequence. **Route:** never steal an owned account, then territory and round robin.
>
> **Write back:** batch upserts by unique key, only fields the pipeline owns, never blanks.
> **Outreach:** Claude drafts from facts we have, a rep approves, replies and unsubscribes sync back.
>
> **Underneath:** a schedule, data checks between steps, a Slack summary every run and an alert when
> something breaks. And I check whether tier A actually books more meetings than tier B; if not, the
> weights change."

## Mapping it to real work

The outbound workflow for ConsultKumar (a UAE business-setup client) follows the same shape:
prospects pulled from Apollo and Clay, enriched and deduplicated, segmented by ICP, email and
LinkedIn sequences drafted with Claude, results logged for follow-up, later packaged as reusable
Claude Code agent skills. Be ready to say exactly which steps were done in tools by clicking and
which in code, and what you'd change at higher volume (this module is the "higher volume" answer).

Related repos in this portfolio:

| Repo | Which steps it shows |
| --- | --- |
| [GTM-Skills-Reusable](https://github.com/DhivyaBalakumar/GTM-Skills-Reusable) | Data model, account pipeline, scoring, signal outbound, inbound routing, CRM update agent, reliability |
| [GTM-Full-pipeline-Mock](https://github.com/DhivyaBalakumar/GTM-Full-pipeline-Mock) | Six messy sources → clean → dedupe → enrich → score → segment → route → mock CRM, with a lead-tracing walkthrough |
| [Real-time Data Pipeline with Signal Detection and Alerts](https://github.com/DhivyaBalakumar/Real-time-Data-Pipeline-with-Signal-Detection-and-Alerts) | Stream join, anomaly scoring, alert cooldowns (the signal-alert pattern) |
| [YouTube ETL Pipeline and Hit-or-Flop Prediction](https://github.com/DhivyaBalakumar/YouTube-ETL-Pipeline-and-Hit-or-Flop-Prediction) | Scheduled API pulls, quotas, retries, HubSpot batch upsert, signed webhooks |
| [KnowBaseWiki Funnel and Conversion Analytics](https://github.com/DhivyaBalakumar/KnowBaseWiki-Funnel-and-Conversion-Analytics-) | Funnel, cohort and A/B analysis (the reporting step) |

## Likely questions, short answers

| Question | Answer in one breath |
| --- | --- |
| How do you avoid duplicates in the CRM? | Upsert by a unique property (domain/email), dedupe against the CRM before writing, alert if creates spike on re-runs |
| What happens on a 429? | Exponential backoff with jitter, respect Retry-After, max attempts; throttle proactively so it's rare |
| Apollo returns 120k matches but caps at 50k? | Slice the query (country × size band) so each slice is under the cap; dedupe the union |
| Two sources disagree on employee count? | Survivorship rule: freshest trusted provider for firmographics, human edit beats everything, keep lineage |
| How do you keep enrichment costs down? | Dedupe first, enrich only ICP-passing and missing fields, waterfall cheap → expensive, cache with TTL, budget per run |
| How do you know the score works? | Meeting and win rate by tier; A must beat B. If not, recalibrate |
| Clay or Python? | Clay to explore and for non-engineers; Python for the core data layer where you need tests, versioning, volume and cost control. Often both |
| What if a source changes its format? | Data contract checks: row counts, quarantine rate and null rates per run; the run stops before writing |
| How do you use Claude safely in the pipeline? | Only where rules can't; closed label sets; JSON output validated; facts passed in, never invented; human approval for anything sent |
| GDPR? | Legitimate interest documented, source disclosed on first contact, opt-outs suppressed permanently, data minimised |
| Reply rate dropped from 6% to 3%? | Check deliverability first (bounces, spam placement), then whether the segment or list source changed, then the copy, using the funnel by step and source |

## Practise

1. Run `python 16-end-to-end-pipeline/code/pipeline_end_to_end.py` and trace one person, e.g.
   `lena@opalanalytics.de`, through every step's output.
2. Change one rule in `CONFIG` (e.g. remove `UK` from countries, or set `credit_budget` to 5) and
   predict the result before you run it.
3. Explain each chapter's "interview lines" out loud in under 30 seconds each.
