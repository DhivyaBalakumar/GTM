"""
The reliable-pipeline pattern, in one file (split into modules in real projects).
================================================================================

    python 10-production-habits/examples/pipeline_skeleton.py --dry-run
    python 10-production-habits/examples/pipeline_skeleton.py --limit 5

Shows: config in one place, logging to file + screen, fatal vs per-record errors, a dry run,
a summary line, exit codes, and a failure alert hook. The "CRM" here is a local JSON file so you can
see idempotency without any account.
"""
import argparse
import csv
import json
import logging
import sys
import time
from pathlib import Path

# ----------------------------------------------------------------------------- config (one place)
REPO = Path(__file__).resolve().parents[2]
INPUT = REPO / "data" / "leads_raw.csv"
OUT = REPO / "output"
CRM_FILE = OUT / "fake_crm.json"
LOG_FILE = OUT / "pipeline.log"
PERSONAL = {"gmail.com", "yahoo.com", "outlook.com", "hotmail.com"}
TARGET_COUNTRIES = {"DE", "AT", "CH", "NL", "BE", "LU"}
MAX_FAILURE_RATE = 0.10

log = logging.getLogger("pipeline")


def setup_logging():
    OUT.mkdir(exist_ok=True)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)-7s %(message)s",
                        handlers=[logging.FileHandler(LOG_FILE, encoding="utf-8"), logging.StreamHandler()])


def send_failure_alert(message):
    """Real version: post to Slack (see slack_alert.py). Here we just log loudly."""
    log.critical("ALERT: %s", message)


# ----------------------------------------------------------------------------- steps
def extract(path, limit=None):
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")      # fatal: stop the run
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    return rows[:limit] if limit else rows


def domain_of(row):
    for value in (row.get("website"), row.get("contact_email")):
        if value:
            v = value.strip().lower().split("@")[-1]
            for p in ("https://", "http://", "www."):
                v = v.removeprefix(p)
            return v.split("/")[0]
    return ""


def transform(row):
    """Per-record logic. Raises ValueError for records that can't be used."""
    domain = domain_of(row)
    if not domain or domain in PERSONAL:
        raise ValueError("no company domain")
    employees = row.get("employees", "").strip()
    if employees and not employees.isdigit():
        raise ValueError(f"unparseable employees {employees!r}")
    country = row.get("country", "").strip().upper()[:2]
    score = (20 if employees and 20 <= int(employees) <= 500 else 0) + (15 if country in TARGET_COUNTRIES else 0)
    return {"domain": domain, "name": row.get("company") or None, "country": country,
            "employees": int(employees) if employees else None, "fit_score": score}


def load(records, dry_run):
    """Upsert into the fake CRM by domain; never write blanks. Returns created/updated counts."""
    crm = json.loads(CRM_FILE.read_text()) if CRM_FILE.exists() else {}
    created = updated = 0
    for r in records:
        clean = {k: v for k, v in r.items() if v not in (None, "")}
        if r["domain"] in crm:
            crm[r["domain"]].update(clean)
            updated += 1
        else:
            crm[r["domain"]] = clean
            created += 1
    if not dry_run:
        CRM_FILE.write_text(json.dumps(crm, indent=2))
    return created, updated


# ----------------------------------------------------------------------------- main
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()
    setup_logging()
    start = time.perf_counter()
    try:
        rows = extract(INPUT, args.limit)
        good, failed = {}, []
        for row in rows:
            try:
                rec = transform(row)
                good[rec["domain"]] = rec                     # last one wins; real code: best one wins
            except ValueError as e:
                failed.append(row.get("company") or row.get("contact_email"))
                log.warning("Skipped %s: %s", row.get("company") or row.get("contact_email"), e)
        created, updated = load(list(good.values()), args.dry_run)
        rate = len(failed) / max(len(rows), 1)
        log.info("SUMMARY read=%d unique=%d failed=%d (%.0f%%) | created=%d updated=%d | dry_run=%s | %.1fs",
                 len(rows), len(good), len(failed), rate * 100, created, updated, args.dry_run,
                 time.perf_counter() - start)
        if rate > MAX_FAILURE_RATE:
            send_failure_alert(f"{rate:.0%} of records failed (limit {MAX_FAILURE_RATE:.0%}). Check the source data.")
    except Exception as e:
        log.exception("Run failed")
        send_failure_alert(f"Pipeline crashed: {e}")
        sys.exit(1)                                             # non-zero exit: the scheduler marks it failed


if __name__ == "__main__":
    main()
