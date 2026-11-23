"""Solution to exercise 4."""
import csv
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
LEADS = REPO / "data" / "leads_raw.csv"
OUT = REPO / "output"

PERSONAL_DOMAINS = {"gmail.com", "yahoo.com", "outlook.com", "hotmail.com"}


def safe_int(value, default=None):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def load_csv(path):
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _normalize(value):
    if not value:
        return ""
    v = value.strip().lower()
    if "@" in v:
        v = v.split("@")[-1]
    for prefix in ("https://", "http://", "www."):
        if v.startswith(prefix):
            v = v[len(prefix):]
    return v.split("/")[0]


def domain_for(row):
    return _normalize(row.get("website")) or _normalize(row.get("contact_email"))


def _filled(row):
    return sum(1 for v in row.values() if v not in (None, "") and str(v).strip())


def clean_leads(rows):
    dropped, best = [], {}
    for original in rows:
        row = dict(original)
        row["domain"] = domain_for(row)
        if not row["domain"] or row["domain"] in PERSONAL_DOMAINS:
            dropped.append(row)
            continue
        if row["domain"] not in best or _filled(row) > _filled(best[row["domain"]]):
            best[row["domain"]] = row
    kept = sorted(best.values(), key=lambda r: r["domain"])
    return kept, dropped


def write_outputs(kept, dropped, out_dir):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    fields = list(kept[0].keys()) if kept else []
    with open(out_dir / "leads_clean.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(kept)
    summary = {"kept": len(kept), "dropped": len(dropped)}
    (out_dir / "summary.json").write_text(json.dumps(summary), encoding="utf-8")
    return summary


def _checks():
    failures = []

    def check(label, got, expected):
        if got != expected:
            failures.append(f"{label}: expected {expected!r}, got {got!r}")

    check("safe_int ok", safe_int("12"), 12)
    check("safe_int bad", safe_int("abc"), None)
    check("safe_int None default", safe_int(None, 0), 0)
    try:
        load_csv(REPO / "data" / "nope.csv")
        failures.append("load_csv should raise FileNotFoundError for a missing file")
    except FileNotFoundError as e:
        if "nope.csv" not in str(e):
            failures.append("FileNotFoundError message should include the path")
    rows = load_csv(LEADS)
    check("rows read", len(rows), 25)
    check("domain website", domain_for({"website": "https://www.PeopleCo.de/about", "contact_email": ""}), "peopleco.de")
    check("domain email fallback", domain_for({"website": "", "contact_email": "julia@kranich-logistik.de"}), "kranich-logistik.de")
    check("domain none", domain_for({"website": "", "contact_email": ""}), "")
    kept, dropped = clean_leads(rows)
    check("kept", len(kept), 19)
    check("dropped", len(dropped), 2)
    check("sorted", [r["domain"] for r in kept] == sorted(r["domain"] for r in kept), True)
    people = [r for r in kept if r["domain"] == "peopleco.de"]
    check("peopleco kept most complete", people[0]["company"] if people else None, "PeopleCo GmbH")
    summary = write_outputs(kept, dropped, OUT)
    check("summary", summary, {"kept": 19, "dropped": 2})
    check("csv written", (OUT / "leads_clean.csv").exists(), True)
    check("json written", json.loads((OUT / "summary.json").read_text()) if (OUT / "summary.json").exists() else None,
          {"kept": 19, "dropped": 2})
    return failures


if __name__ == "__main__":
    problems = _checks()
    print("\n".join(problems) if problems else "All checks passed")
