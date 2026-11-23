"""
Classify companies with Claude: validated JSON, retries, fallbacks, logging
==========================================================================

Offline demo (no key; a fake model returns good AND bad answers so you can watch validation work):
    python 09-claude-and-ai/claude_scoring.py
Live (needs `pip install anthropic` and ANTHROPIC_API_KEY in .env):
    python 09-claude-and-ai/claude_scoring.py --live
"""
import argparse
import hashlib
import json
import logging
import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

MODEL = "claude-haiku-5-5"          # small, cheap model for bulk work; check current model names
PROMPT_VERSION = "classify-v1"
ALLOWED_INDUSTRIES = {"Software", "Fintech", "Healthtech", "Automotive", "Other"}
MIN_CONFIDENCE = 0.6
log = logging.getLogger("claude")

SYSTEM = f"""You classify European B2B companies for a security-compliance software vendor.
Reply with ONLY a JSON object, no other text, with exactly these keys:
  "industry": one of {sorted(ALLOWED_INDUSTRIES)}
  "sells_to_enterprise": true or false (does the text say they sell to large companies, banks or car makers?)
  "compliance_signal": true or false (does the text mention ISO 27001, SOC 2, TISAX, NIS2, DORA or security certification work?)
  "confidence": a number from 0 to 1
  "reason": at most 20 words, based only on the text
If the text does not say, use "Other", false, and a confidence below 0.5. Never invent facts."""

COMPANIES = [
    {"domain": "peopleco.de", "text": "PeopleCo builds HR software for enterprises across Germany. "
                                      "We're hiring an ISO 27001 Compliance Manager to lead our certification."},
    {"domain": "nordbanktech.nl", "text": "Nordbank Tech provides payment APIs to European banks, "
                                          "including a new partnership with a major Dutch bank."},
    {"domain": "greenleafretail.com", "text": "Greenleaf runs 40 organic grocery stores in Texas."},
    {"domain": "vague.io", "text": "We do innovative things for the future."},
]


# --------------------------------------------------------------------------- the model call
def call_claude(text):
    import anthropic                                  # imported here so the offline demo needs no install
    client = anthropic.Anthropic()                    # reads ANTHROPIC_API_KEY
    response = client.messages.create(
        model=MODEL, max_tokens=300, temperature=0, system=SYSTEM,
        messages=[{"role": "user", "content": f"<website>\n{text}\n</website>"}],
    )
    log.info("tokens in=%d out=%d", response.usage.input_tokens, response.usage.output_tokens)
    return response.content[0].text


FAKE_ANSWERS = {   # what a model MIGHT return, including the kinds of mistakes you must catch
    "peopleco.de": ['{"industry": "Software", "sells_to_enterprise": true, "compliance_signal": true, '
                    '"confidence": 0.93, "reason": "HR software for enterprises; hiring an ISO 27001 compliance manager"}'],
    "nordbanktech.nl": ['Sure! Here is the JSON you asked for: {"industry": "Fintech"}',          # prose: invalid
                        '{"industry": "Fintech", "sells_to_enterprise": true, "compliance_signal": false, '
                        '"confidence": 0.88, "reason": "Payment APIs sold to European banks"}'],      # retry works
    "greenleafretail.com": ['{"industry": "Retail", "sells_to_enterprise": false, "compliance_signal": false, '
                            '"confidence": 0.9, "reason": "Grocery stores"}',                       # not allowed
                            '{"industry": "Grocery", "sells_to_enterprise": false, "compliance_signal": false, '
                            '"confidence": 0.9, "reason": "Grocery stores"}'],                      # still wrong
    "vague.io": ['{"industry": "Other", "sells_to_enterprise": false, "compliance_signal": false, '
                 '"confidence": 0.3, "reason": "Text gives no concrete information"}'],
}


def make_fake_model():
    calls = {}

    def fake(domain, _text):
        answers = FAKE_ANSWERS[domain]
        i = calls.get(domain, 0)
        calls[domain] = i + 1
        return answers[min(i, len(answers) - 1)]
    return fake


# --------------------------------------------------------------------------- validation
def parse_and_validate(text):
    """Return (data, None) if valid, or (None, reason) if not."""
    try:
        data = json.loads(text.strip())
    except (json.JSONDecodeError, AttributeError):
        return None, "not valid JSON"
    if not isinstance(data, dict):
        return None, "not a JSON object"
    if data.get("industry") not in ALLOWED_INDUSTRIES:
        return None, f"industry not allowed: {data.get('industry')!r}"
    for key in ("sells_to_enterprise", "compliance_signal"):
        if not isinstance(data.get(key), bool):
            return None, f"{key} must be true/false"
    conf = data.get("confidence")
    if not isinstance(conf, (int, float)) or not 0 <= conf <= 1:
        return None, "confidence must be a number from 0 to 1"
    reason = data.get("reason")
    if not isinstance(reason, str) or not reason.strip() or len(reason.split()) > 25:
        return None, "reason missing or longer than 25 words"
    return data, None


# --------------------------------------------------------------------------- the safe wrapper
def classify(company, model_fn, max_attempts=2):
    """Call the model, validate, retry once, then fall back. Never returns unvalidated data."""
    for attempt in range(1, max_attempts + 1):
        try:
            raw = model_fn(company["domain"], company["text"])
        except Exception as e:                                  # API down, rate limited after SDK retries...
            log.warning("%s: model call failed (%s)", company["domain"], e)
            continue
        data, problem = parse_and_validate(raw)
        audit = {"domain": company["domain"], "prompt_version": PROMPT_VERSION, "attempt": attempt,
                 "input_sha": hashlib.sha256(company["text"].encode()).hexdigest()[:10],
                 "valid": data is not None, "problem": problem}
        log.info("audit %s", json.dumps(audit))
        if data:
            status = "ok" if data["confidence"] >= MIN_CONFIDENCE else "needs_review (low confidence)"
            return {"domain": company["domain"], "status": status, **data}
    return {"domain": company["domain"], "status": "needs_review (invalid AI output)"}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", action="store_true", help="call the real Claude API")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)-7s %(message)s")

    if args.live:
        if not os.getenv("ANTHROPIC_API_KEY"):
            raise SystemExit("ANTHROPIC_API_KEY is not set. Add it to .env or run without --live.")
        model_fn = lambda _domain, text: call_claude(text)   # noqa: E731
    else:
        print("(offline demo: a fake model returns realistic good and bad answers)\n")
        model_fn = make_fake_model()

    results = [classify(c, model_fn) for c in COMPANIES]
    print("\nRESULTS (only these validated fields would be written to the CRM, as ai_* properties):")
    for r in results:
        print(f"  {r['domain']:22} {r['status']:32} {r.get('industry', '-'):10} {r.get('reason', '')}")
    ok = sum(r["status"] == "ok" for r in results)
    print(f"\nSUMMARY ok={ok} needs_review={len(results) - ok}")


if __name__ == "__main__":
    main()
