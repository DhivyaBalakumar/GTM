"""
Lesson 10: files, CSV and JSON
==============================

Run me:  python 03-python/lessons/10_files_csv_json.py

Data arrives as files: CSV exports from Apollo or the CRM, JSON from APIs.
"""
import csv
import json
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths. Python looks for relative paths in the folder you RUN FROM, which causes
# FileNotFoundError when you run from somewhere else. This builds the path from THIS
# file's location instead, so it works from any folder.
# ---------------------------------------------------------------------------
REPO = Path(__file__).resolve().parents[2]    # lessons -> 03-python -> repo root
DATA = REPO / "data"
OUT = REPO / "output"
OUT.mkdir(exist_ok=True)                       # create output/ if it doesn't exist
print("data folder:", DATA)

print("\n=== 1. Plain text files ===")
note = OUT / "note.txt"
with open(note, "w", encoding="utf-8") as f:   # "w" = write (replaces the file)
    f.write("First line\n")
    f.write("Second line\n")
with open(note, "a", encoding="utf-8") as f:   # "a" = append
    f.write("Third line\n")
with open(note, encoding="utf-8") as f:        # default mode "r" = read
    for line in f:
        print("read:", line.strip())
# `with` closes the file automatically, even if an error happens.
# Always pass encoding="utf-8" on Windows, or names like "Müller" can break.

print("\n=== 2. Reading a CSV into a list of dictionaries ===")
with open(DATA / "leads_raw.csv", newline="", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))     # each row -> {"company": ..., "website": ...}
print("rows:", len(rows))
print("columns:", list(rows[0].keys()))
print("first row:", rows[0])
# Note: every value is a STRING, and empty cells are "" (not None).
print("employees of row 2:", repr(rows[1]["employees"]))

print("\n=== 3. Filtering and writing a CSV ===")
with_email = [r for r in rows if r["contact_email"]]
german = [r for r in with_email if r["country"].strip().upper() in {"DE", "GERMANY"}]
out_file = OUT / "german_leads.csv"
with open(out_file, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["company", "contact_email", "city"],
                            extrasaction="ignore")   # ignore columns we didn't list
    writer.writeheader()
    writer.writerows(german)
print(f"wrote {len(german)} rows to {out_file.name}")
# newline="" stops blank lines appearing between rows on Windows.

print("\n=== 4. JSON text <-> Python ===")
text = '{"name": "PeopleCo", "employees": 120, "tags": ["software"], "owner": null}'
data = json.loads(text)              # text -> dict   (loads = load String)
print(data, type(data))
print(json.dumps(data))              # dict -> text
print(json.dumps(data, indent=2))    # pretty
# JSON null -> None, true -> True, arrays -> lists, objects -> dicts.

print("\n=== 5. JSON files ===")
with open(DATA / "sample_api_response.json", encoding="utf-8") as f:
    response = json.load(f)          # file -> dict
for item in response["results"]:
    p = item.get("properties", {})
    print(item["id"], p.get("name"), p.get("domain"), p.get("numberofemployees"))

saved = OUT / "first_result.json"
with open(saved, "w", encoding="utf-8") as f:
    json.dump(response["results"][0], f, indent=2, ensure_ascii=False)   # dict -> file
print("saved", saved.name)

print("\n=== 6. Why save RAW API responses first ===")
print("""
In a pipeline, save the raw API answer to a file (or table) BEFORE cleaning it.
If your cleaning code has a bug, you fix it and re-run from the saved file
without calling the API again (saving time and rate limit).
""")

print("=== 7. Handling a missing file clearly ===")
try:
    with open(DATA / "does_not_exist.csv", encoding="utf-8") as f:
        pass
except FileNotFoundError as e:
    print("Could not find the input file:", e.filename)

print("\n=== 8. pathlib helpers ===")
p = DATA / "leads_raw.csv"
print(p.name, p.stem, p.suffix, p.exists(), p.parent.name)
print([x.name for x in sorted(DATA.glob("*.csv"))])

# ---------------------------------------------------------------------------
# TRY IT
# 1. Write every lead with a gmail/yahoo email to output/personal_emails.csv.
# 2. Count rows per `source` and save the counts as JSON.
# 3. Load output/first_result.json back and print its name.
# ---------------------------------------------------------------------------
