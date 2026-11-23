# 1. LLMs, and when to use AI

## How a large language model works (just enough)

An LLM like Claude predicts text, one small piece (a **token**) at a time, based on patterns learned
from huge amounts of text. Consequences you must design around:

| Fact | Consequence for your pipeline |
| --- | --- |
| It generates plausible text | It can be **confidently wrong** (invent a funding round, a job title) |
| It works on tokens (~4 characters of English each) | You pay per input and output token; long prompts cost more |
| It has a **context window** (how much text it can read at once) | Send only what's needed: the relevant page text, not the whole website |
| Output varies between runs | Ask for a fixed format and validate it; use low temperature for classification |
| Its knowledge has a cutoff | For current facts (funding, hiring), give it the source text; don't ask it to remember |

## AI or a simple rule?

| Use a **rule** when… | Use **Claude** when… |
| --- | --- |
| The logic is fixed and must be exact: "employees between 20 and 500" | The input is messy text that needs judgement: a website, a job ad, call notes |
| It must be cheap and instant for millions of rows | Volume is moderate, or only for top accounts |
| It must be explainable and auditable | A human-like summary or draft is the output |
| Examples: dedupe by domain, country mapping, routing, score thresholds | Examples: "what does this company do and who are their customers?", "does this job post imply an ISO 27001 project?", drafting a first line |

Good systems **combine** them: rules do the exact, cheap work; AI handles the judgement; rules check the
AI's output.

## GTM use cases for Claude (from the job post: "research to proposals to CRM updates")

| Use case | Input | Output | Guardrail |
| --- | --- | --- | --- |
| Industry / ICP classification | Website text | `{"industry": ..., "sells_to_enterprise": true, "reason": ...}` | Allowed values only |
| Signal detection | Job post text | `{"compliance_signal": true, "frameworks": ["ISO 27001"], "evidence": "..."}` | Evidence must be a quote from the input |
| Account brief before a demo | Website + news + CRM fields | 5-line brief | Human reads it; sources cited |
| Personalised first line | Signal + persona | ≤ 30 words | Length + banned-phrase check; human sends |
| Call-notes to CRM fields | Transcript | Next step, budget, timeline, objections | Writes only to specific fields; review if low confidence |
| Security questionnaire help | Questions + approved answers | Draft answers | Only from approved knowledge |
| Reply classification | Email reply | interested / not now / unsubscribe / out of office | Unsubscribe always honoured |

## Cost thinking

- Price is per million tokens, different for input and output, and different per model (small models
  are much cheaper). Check current pricing at [docs.claude.com](https://docs.claude.com).
- Rough sizing: a 1,500-token prompt + 150-token answer, for 2,000 companies a month, is ~3.3M tokens:
  cheap on a small model.
- Reduce cost: small model for bulk classification; only run AI on accounts that pass rule-based fit
  checks; **cache** results (don't re-classify unchanged websites); trim input text; batch APIs for
  non-urgent work.

## Interview phrasing

> "Rules for anything exact and high-volume, like dedupe, routing and score thresholds. Claude for
> messy text that needs judgement: reading a website or job post, or drafting a brief. Every AI output
> comes back as JSON with allowed values, gets validated before it touches the CRM, and falls back
> safely if it's wrong. I'd use a small model for bulk work and only run it on accounts that pass the
> fit rules, to keep cost down."

Next: [02-prompts-structured-output-guardrails.md](02-prompts-structured-output-guardrails.md)
