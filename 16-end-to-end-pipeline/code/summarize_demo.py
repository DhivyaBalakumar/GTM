"""
Summarizing data and text, the way a GTM pipeline does it
=========================================================

Run me (from the repo root):

    python 16-end-to-end-pipeline/code/summarize_demo.py          # offline, fake model
    python 16-end-to-end-pipeline/code/summarize_demo.py --live   # real Claude for part 2 (needs ANTHROPIC_API_KEY)

Read alongside 16-end-to-end-pipeline/17-summarizing-data-and-text.md.

PART 1  Summarizing DATA  (numbers):  Counter, fill rates, pandas groupby / pivot_table / crosstab,
        funnel + speed-to-lead, the same in SQL, a run summary for Slack.
PART 2  Summarizing TEXT  (words):    an account brief and a call/notes summary with an LLM:
        facts in, JSON out, validated; map-reduce for long text; an extractive fallback.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sqlite3
import sys
from collections import Counter
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
DATA = HERE.parents[1] / "data"

spec = importlib.util.spec_from_file_location("pipeline_e2e", HERE / "pipeline_end_to_end.py")
pipe = importlib.util.module_from_spec(spec)
sys.modules["pipeline_e2e"] = pipe
spec.loader.exec_module(pipe)


def section(title):
    print(f"\n{'=' * 8} {title} {'=' * 8}")


# =============================================================================================== #
# PART 1: SUMMARIZING DATA
# =============================================================================================== #
def part1():
    report, crm, _ = pipe.run(verbose=False)

    section("1.1 Count things with Counter (pure Python)")
    print("tiers:            ", dict(report["tiers"]))
    print("suppression:      ", dict(report["suppressed"]))
    print("most common tier: ", report["tiers"].most_common(1))

    section("1.2 Fill rate per field (how complete is the data?)")
    scored = pd.read_csv(HERE / "output" / "scored_contacts.csv")
    fill = (scored.notna().mean() * 100).round(0).astype(int).sort_values()
    print(fill.head(6).to_string())

    section("1.3 groupby + agg: one row per group, several numbers")
    by_tier = scored.groupby("tier").agg(contacts=("email", "count"),
                                         avg_score=("score", "mean"),
                                         avg_fit=("fit", "mean"),
                                         with_owner=("owner", "count")).round(1)
    print(by_tier.to_string())

    section("1.4 pivot_table and crosstab: two dimensions at once")
    scored["vertical"] = scored["segment"].str.split(":").str[0]
    print(pd.crosstab(scored["vertical"], scored["tier"]).to_string())
    deals = pd.read_csv(DATA / "crm_deals.csv")
    pivot = deals.pivot_table(index="owner", columns="stage", values="amount_eur",
                              aggfunc="sum", fill_value=0)
    print("\npipeline EUR by owner x stage:\n" + pivot.to_string())

    section("1.5 Funnel + speed-to-lead from inbound leads")
    inbound = pd.read_csv(DATA / "inbound_leads.csv", parse_dates=["created_at", "first_contacted_at"])
    inbound["minutes_to_first_touch"] = (inbound["first_contacted_at"] - inbound["created_at"]).dt.total_seconds() / 60
    funnel = inbound.groupby("source").agg(leads=("id", "count"),
                                           contacted=("first_contacted_at", "count"),
                                           meetings=("meeting_booked", "sum"),
                                           median_minutes=("minutes_to_first_touch", "median"))
    funnel["meeting_rate_%"] = (100 * funnel["meetings"] / funnel["leads"]).round(0)
    print(funnel.sort_values("meeting_rate_%", ascending=False).round(0).to_string())

    won = deals[deals["stage"].isin(["closed_won", "closed_lost"])]
    win_rate = (won["stage"] == "closed_won").mean()
    print(f"\nwin rate on closed deals: {win_rate:.0%} ({(won['stage'] == 'closed_won').sum()}/{len(won)})")

    section("1.6 The same summaries in SQL (sqlite in memory)")
    con = sqlite3.connect(":memory:")
    scored.to_sql("scored", con, index=False)
    deals.to_sql("deals", con, index=False)
    q1 = """SELECT tier, COUNT(*) AS contacts, ROUND(AVG(score), 1) AS avg_score
            FROM scored GROUP BY tier ORDER BY tier"""
    q2 = """SELECT owner,
                   SUM(CASE WHEN stage NOT IN ('closed_won','closed_lost') THEN amount_eur ELSE 0 END) AS open_eur,
                   SUM(CASE WHEN stage = 'closed_won' THEN amount_eur ELSE 0 END) AS won_eur,
                   COUNT(*) AS deals
            FROM deals GROUP BY owner HAVING COUNT(*) >= 2 ORDER BY open_eur DESC"""
    print(pd.read_sql(q1, con).to_string(index=False))
    print()
    print(pd.read_sql(q2, con).to_string(index=False))

    section("1.7 A run summary for Slack (summarizing the pipeline itself)")
    c = report["crm"]
    text = (f"GTM run: {report['collected']} in, {report['quarantined']} quarantined, "
            f"{report['contacts']} contacts at {report['accounts']} accounts, "
            f"{sum(report['suppressed'].values())} suppressed, tiers "
            + ", ".join(f"{t}={n}" for t, n in sorted(report["tiers"].items()))
            + f" | CRM +{c['contacts_created']} new / {c['contacts_updated']} updated"
            f" | {report['credits_used']} credits | {len(report['enrich_failures'])} enrich failures"
            f" | checks {'all pass' if all(report['checks'].values()) else 'FAILED'}")
    print(text)
    return report


# =============================================================================================== #
# PART 2: SUMMARIZING TEXT
# =============================================================================================== #
BRIEF_SCHEMA = {"one_liner": str, "why_now": list, "talking_points": list, "risks": list}

ACCOUNT_FACTS = {   # facts we HAVE; the model may only use these
    "company": "Opal Analytics", "domain": "opalanalytics.de", "country": "DE", "employees": 25,
    "industry": "software", "signals": ["funding_seed"], "contact": "Lena Vogel, CEO",
    "crm_notes": [
        "2026-10-15 Lena: account created from Clay list.",
        "2026-11-03 Lena Vogel downloaded the SOC 2 checklist.",
        "2026-11-20 Website visit: pricing page, 3 times this week.",
    ],
}

CALL_NOTES = [   # a long text split into chunks, like a transcript
    "Discovery call with Kite Labs, Ravi (founder). 8 people, selling to two banks in Frankfurt.",
    "Bank procurement asked for ISO 27001 or a SOC 2 Type II report before signing. Deadline end of Q1.",
    "They tried spreadsheets for policies, gave up. No security person. Budget not set yet.",
    "Next step: Ravi will forward the bank's security questionnaire. Follow-up call next Tuesday.",
]


def fake_model(prompt: str) -> str:
    """Stands in for Claude offline. Returns what a model MIGHT return, including one bad answer,
    so you can watch validation catch it."""
    if "ACCOUNT BRIEF" in prompt:
        return json.dumps({
            "one_liner": "25-person German software company, recently seed-funded, showing buying intent.",
            "why_now": ["Seed funding (signal: funding_seed)", "Downloaded SOC 2 checklist on 2026-11-03",
                        "Viewed pricing page 3 times this week"],
            "talking_points": ["First enterprise customers usually ask for ISO 27001 / SOC 2",
                               "Pick up from the SOC 2 checklist they downloaded"],
            "risks": ["No security lead known", "Small team: budget may be tight"],
        })
    if "CHUNK" in prompt:
        chunk = prompt.split("CHUNK:", 1)[1].strip()
        return json.dumps({"facts": [chunk.split(".")[0] + "."]})
    if "COMBINE" in prompt:
        return json.dumps({"summary": "Kite Labs (8 people) needs ISO 27001 or SOC 2 Type II for two bank "
                                      "customers by end of Q1; no security person, budget not set.",
                           "next_steps": ["Ravi sends bank questionnaire", "Follow-up call next Tuesday"],
                           "deal_size_eur": 50000})          # <- invented number: validation must catch it
    return "{}"


def live_model(prompt: str) -> str:
    import anthropic                                         # pip install anthropic
    client = anthropic.Anthropic()
    msg = client.messages.create(model="claude-haiku-5-5", max_tokens=600, temperature=0,
                                 messages=[{"role": "user", "content": prompt}])
    return msg.content[0].text


def validate(obj: dict, schema: dict, allowed_extra=()) -> list[str]:
    problems = [f"missing {k}" for k in schema if k not in obj]
    problems += [f"{k} should be {t.__name__}" for k, t in schema.items() if k in obj and not isinstance(obj[k], t)]
    problems += [f"unexpected field {k}" for k in obj if k not in schema and k not in allowed_extra]
    return problems


def account_brief(model) -> dict:
    prompt = ("ACCOUNT BRIEF. Use ONLY the facts below; if something isn't in the facts, don't say it. "
              "Return JSON with keys one_liner (str, <= 25 words), why_now (list of str, each citing a fact), "
              "talking_points (list, max 3), risks (list, max 3).\n"
              f"FACTS: {json.dumps(ACCOUNT_FACTS)}")
    brief = json.loads(model(prompt))
    problems = validate(brief, BRIEF_SCHEMA)
    if len(brief.get("one_liner", "").split()) > 25:
        problems.append("one_liner too long")
    return {"brief": brief, "problems": problems}


def map_reduce_summary(model, chunks) -> dict:
    """Long text: summarise each chunk (map), then combine the chunk summaries (reduce)."""
    facts = []
    for ch in chunks:                                        # MAP
        facts += json.loads(model(f"Extract the key facts as JSON {{'facts': [...]}}. CHUNK: {ch}"))["facts"]
    combined = json.loads(model("COMBINE these facts into JSON with keys summary (<= 40 words) and "
                                f"next_steps (list). Do not add numbers that aren't in the facts. FACTS: {facts}"))
    problems = validate(combined, {"summary": str, "next_steps": list})
    source_text = " ".join(chunks)                           # grounding check: no invented numbers
    for k, v in combined.items():
        for token in str(v).replace(",", " ").split():
            digits = "".join(ch for ch in token if ch.isdigit())
            if digits and digits not in source_text:
                problems.append(f"'{k}' contains a number not in the source: {token}")
    return {"facts": facts, "summary": combined, "problems": problems}


def extractive_summary(sentences, keywords, n=2):
    """No-AI fallback: keep the n sentences with the most keywords, in original order."""
    scored = [(sum(k in s.lower() for k in keywords), i, s) for i, s in enumerate(sentences)]
    top = sorted(sorted(scored, reverse=True)[:n], key=lambda x: x[1])
    return [s for _, _, s in top]


def part2(model):
    section("2.1 Account brief: facts in, JSON out, validated")
    res = account_brief(model)
    print(json.dumps(res["brief"], indent=2))
    print("validation problems:", res["problems"] or "none")

    section("2.2 Map-reduce summary of long call notes (with a grounding check)")
    res = map_reduce_summary(model, CALL_NOTES)
    print("map step facts:", res["facts"])
    print("reduce step:", json.dumps(res["summary"], indent=2))
    print("validation problems:", res["problems"] or "none")
    if res["problems"]:
        print("-> rejected fields are dropped before anything is written to the CRM")

    section("2.3 Extractive fallback (no AI): keep the sentences that matter")
    print(extractive_summary(CALL_NOTES, ["iso", "soc", "deadline", "next step", "budget"], n=2))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--live", action="store_true", help="use real Claude for part 2")
    args = ap.parse_args()
    part1()
    if args.live and not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit("--live needs ANTHROPIC_API_KEY in your environment (.env)")
    part2(live_model if args.live else fake_model)
