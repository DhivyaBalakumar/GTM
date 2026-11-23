"""
Exercise 4: errors and files (putting it together, plain Python, no pandas)
===========================================================================

Fill in each function, then run:
    python 03-python/exercises/ex04_errors_and_files.py

Uses data/leads_raw.csv (25 rows with deliberate problems).
"""
import csv
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
LEADS = REPO / "data" / "leads_raw.csv"
OUT = REPO / "output"

PERSONAL_DOMAINS = {"gmail.com", "yahoo.com", "outlook.com", "hotmail.com"}


def safe_int(value, default=None):
    """int(value), or `default` if it can't be converted (never raises)."""
    raise NotImplementedError


def load_csv(path):
    """Read a CSV into a list of dicts. If the file doesn't exist, raise FileNotFoundError
    with a helpful message that includes the path."""
    raise NotImplementedError


def domain_for(row):
    """Domain from row["website"], falling back to row["contact_email"]; "" if neither.
    Normalise: lowercase, strip, remove http(s):// and www., drop any /path, take the part
    after @ for emails."""
    raise NotImplementedError


def clean_leads(rows):
    """Return (kept, dropped).

    For each row add row["domain"] = domain_for(row).
    Drop (put in `dropped`) rows with no domain or a personal email domain.
    Then keep ONE row per domain: the one with the most non-empty values.
    `kept` must be sorted by domain.
    """
    raise NotImplementedError


def write_outputs(kept, dropped, out_dir):
    """Write kept rows to out_dir/leads_clean.csv (all columns, header first) and a summary to
    out_dir/summary.json like {"kept": 19, "dropped": 2}. Create out_dir if needed.
    Return the summary dict."""
    raise NotImplementedError


# --------------------------------------------------------------------------- checks
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
    try:
        problems = _checks()
    except NotImplementedError:
        print("Some functions still raise NotImplementedError. Fill them in and run again.")
    else:
        print("\n".join(problems) if problems else "All checks passed")
