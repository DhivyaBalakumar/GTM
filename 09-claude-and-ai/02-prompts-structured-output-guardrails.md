# 2. Prompts, structured output and guardrails

## The API call

```python
import anthropic                       # pip install anthropic

client = anthropic.Anthropic()         # reads ANTHROPIC_API_KEY from the environment
response = client.messages.create(
    model="claude-haiku-5-5",          # small, fast, cheap model for bulk work (check current model names)
    max_tokens=300,                    # cap on the answer's length
    system="You classify B2B companies. Reply with JSON only.",          # standing instructions
    messages=[{"role": "user", "content": "Website text: ..."}],         # the actual request
)
text = response.content[0].text        # the answer
print(response.usage.input_tokens, response.usage.output_tokens)        # for cost tracking
```

| Concept | Meaning |
| --- | --- |
| API key | Your password for the API, in `.env` as `ANTHROPIC_API_KEY` |
| SDK | The `anthropic` Python library that wraps the HTTP calls |
| `model` | Which Claude: a small one for bulk work, a larger one for hard reasoning |
| `system` | Standing instructions: role, rules, output format |
| `messages` | The conversation: what you're asking now |
| `max_tokens` | Maximum answer length |
| `temperature` | Randomness (lower = more consistent; good for classification) |
| usage | Tokens used, for cost tracking |

The API has rate limits and returns 429/529 when busy: the same retry ideas apply (the SDK retries some
errors for you).

## Writing a good prompt

1. **Role and task:** "You classify European B2B companies for a security-compliance vendor."
2. **Context:** what the categories mean, what Secfix sells, the ICP.
3. **The input,** clearly delimited: `<website>...</website>`.
4. **Output format,** exactly: "Reply with only a JSON object with keys industry (one of: Software,
   Fintech, Healthtech, Automotive, Other), sells_to_enterprise (true/false), confidence (0-1),
   reason (max 20 words)."
5. **Rules:** "If the text doesn't say, use Other and confidence below 0.5. Never guess facts not in
   the text."
6. **Examples** (one or two input→output pairs) improve consistency a lot.

## Structured output and validation

Your code must be able to read the answer, so ask for JSON with fixed keys and **validate before
using it**:

```python
import json

ALLOWED = {"Software", "Fintech", "Healthtech", "Automotive", "Other"}

def parse_and_validate(text):
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return None, "not valid JSON"
    if data.get("industry") not in ALLOWED:
        return None, f"industry not allowed: {data.get('industry')!r}"
    if not isinstance(data.get("sells_to_enterprise"), bool):
        return None, "sells_to_enterprise must be true/false"
    conf = data.get("confidence")
    if not isinstance(conf, (int, float)) or not 0 <= conf <= 1:
        return None, "confidence must be 0-1"
    if not isinstance(data.get("reason"), str) or len(data["reason"].split()) > 25:
        return None, "reason missing or too long"
    return data, None
```

On failure: **retry once** (optionally telling the model what was wrong), then **fall back** (skip the
record, mark it "needs review", or use the rule-based result). Never write unvalidated AI output into
the CRM.

## Guardrails for an AI agent that writes to the CRM

| Guardrail | What it means |
| --- | --- |
| Fixed output schema, validated | Bad output is rejected before any write |
| Field allow-list | The agent may write `ai_industry`, `ai_brief`, `ai_reason`; never `owner`, deal stage, amount |
| Separate AI fields | Write to `ai_*` properties rather than overwriting human fields |
| Confidence threshold | Low confidence → a review queue, not the CRM |
| Human in the loop | People approve anything sent externally (emails) |
| Evidence required | For facts (signals), the output must quote the source text |
| Logging | Store the prompt version, input hash, output and decision for every call |
| Cost and rate controls | Small model, caching, max calls per run, budget alert |
| Kill switch | A config flag to turn the AI step off instantly |
| Data minimisation | Don't send personal data the task doesn't need |

## Evaluating AI output (how you know it works)

1. Build a small **labelled set**: 30–50 companies where you know the right answer.
2. Run the prompt over them; measure accuracy, and look at every miss.
3. Change the prompt; re-run; compare. Keep the prompt **versioned** (in Git).
4. In production, spot-check a sample weekly and track the rate of validation failures.

## Interview phrasing

> "The model returns a fixed JSON shape: allowed industries, a boolean, a confidence and a short
> reason. My code validates every field; a failure gets one retry, then the record goes to a review
> list. The agent can only write AI-specific fields, never owners or deal stages, low-confidence
> answers go to a human, and every prompt and answer is logged with the prompt version. I measure it
> against a labelled sample before trusting it."

Code: [claude_scoring.py](claude_scoring.py)
