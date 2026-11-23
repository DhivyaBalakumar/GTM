"""
Lesson 11: the standard library tools you'll actually use
=========================================================

Run me:  python 03-python/lessons/11_standard_library.py

All of these are built into Python; no pip install needed.
"""
import logging
import os
import random
import re
import time
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta, timezone
from itertools import cycle, islice
from urllib.parse import urlparse

print("=== 1. datetime: dates and times ===")
now = datetime.now(timezone.utc)                  # always prefer UTC in pipelines
print("now (UTC):", now.isoformat(timespec="seconds"))
today = date.today()
print("today:", today, "| 90 days ago:", today - timedelta(days=90))

funded = date.fromisoformat("2026-10-01")         # parse 'YYYY-MM-DD'
days_since = (date(2026, 11, 23) - funded).days
print("days since funding:", days_since, "| recent (<=90)?", days_since <= 90)

ts = datetime.fromisoformat("2026-11-20T16:40:12+00:00")    # an API timestamp
print("parsed:", ts, "| formatted:", ts.strftime("%d %b %Y %H:%M"))
# Webhooks often send milliseconds since 1970 ("epoch ms"):
print("from epoch ms:", datetime.fromtimestamp(1763900000000 / 1000, tz=timezone.utc))

print("\n=== 2. time: waiting and timing ===")
start = time.perf_counter()
time.sleep(0.2)                                   # wait (used between API retries)
print(f"took {time.perf_counter() - start:.2f}s")

print("\n=== 3. random: jitter for retries ===")
for attempt in range(1, 4):
    wait = 2 ** attempt + random.uniform(0, 0.5)  # backoff + small random extra
    print(f"attempt {attempt}: would wait {wait:.2f}s")
# Jitter stops many workers retrying at exactly the same moment.

print("\n=== 4. logging: timestamped notes instead of print ===")
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)-7s %(name)s: %(message)s")
log = logging.getLogger("pipeline")
log.debug("hidden: level is INFO, so DEBUG is not shown")
log.info("Read %d leads", 25)
log.warning("Skipping %s: no domain", "row 10")
log.error("Upsert failed for %s", "bad.io")
# To also write to a file:  logging.basicConfig(filename="pipeline.log", ...)
# Levels: DEBUG < INFO < WARNING < ERROR < CRITICAL

print("\n=== 5. os: environment variables (where API keys live) ===")
os.environ["DEMO_KEY"] = "abc123"                 # normally set by a .env file
print("DEMO_KEY:", os.getenv("DEMO_KEY"))
print("MISSING:", os.getenv("MISSING_KEY"), "| with default:", os.getenv("MISSING_KEY", "none"))
# In real projects:  from dotenv import load_dotenv; load_dotenv()  then os.getenv("HUBSPOT_TOKEN")

print("\n=== 6. Counter: counting made easy ===")
countries = ["DE", "NL", "DE", "AT", "DE", "NL", "CH"]
counts = Counter(countries)
print(counts, "| top 2:", counts.most_common(2), "| DE:", counts["DE"], "| FR:", counts["FR"])
domains = ["peopleco.de", "opal.de", "peopleco.de"]
print("duplicates:", [d for d, n in Counter(domains).items() if n > 1])

print("\n=== 7. defaultdict: grouping without setdefault ===")
by_owner = defaultdict(list)
for owner, company in [("lena", "PeopleCo"), ("tom", "Nordbank"), ("lena", "Solvia")]:
    by_owner[owner].append(company)              # missing keys start as []
print(dict(by_owner))

print("\n=== 8. itertools.cycle: round-robin ===")
reps = cycle(["lena", "jonas"])
print([next(reps) for _ in range(5)])
print(list(islice(cycle("AB"), 5)))              # first 5 items of an endless cycle

print("\n=== 9. urlparse: get the domain from a URL properly ===")
for url in ["https://www.peopleco.de/about?x=1", "http://brightforge.io", "peopleco.de"]:
    host = urlparse(url if "://" in url else "http://" + url).netloc
    print(url, "->", host.removeprefix("www."))

print("\n=== 10. re (regular expressions): patterns in text ===")
text = "Contact: Anna <ANNA@PeopleCo.de>, Jan <jan.weber@peopleco.de>"
emails = re.findall(r"[\w.+-]+@[\w-]+\.[\w.]+", text)
print("emails:", emails)
print(re.sub(r"\s+", " ", "Head   of\tIT  "))   # collapse whitespace
print(bool(re.search(r"iso\s*27001|soc\s*2", "We are hiring an ISO 27001 manager", re.I)))
# That last line is a real signal detector: does a job post mention ISO 27001 or SOC 2?
# Keep regex simple; for anything complex, plain string methods are easier to read.

# ---------------------------------------------------------------------------
# TRY IT
# 1. Using Counter, find the most common `source` in data/leads_raw.csv.
# 2. Write is_recent(iso_date, days=90) using date.fromisoformat.
# 3. Write a regex that detects "TISAX" or "NIS2" in a sentence, case-insensitive.
# ---------------------------------------------------------------------------
