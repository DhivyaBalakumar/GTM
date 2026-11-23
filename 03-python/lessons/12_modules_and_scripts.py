"""
Lesson 12: modules, scripts, command-line flags and project structure
=====================================================================

Run me:
    python 03-python/lessons/12_modules_and_scripts.py
    python 03-python/lessons/12_modules_and_scripts.py --limit 3
    python 03-python/lessons/12_modules_and_scripts.py --dry-run --limit 2

A MODULE is just a .py file. You can import functions from your own files the same way
you import pandas. Real pipelines are split into small files, each with one job.
"""
import argparse
import logging

print("=== 1. Importing styles ===")
import math                      # import the whole module
from math import sqrt            # import one name
import datetime as dt            # alias
print(math.floor(4.7), sqrt(16), dt.date(2026, 11, 27))

print("\n=== 2. Importing YOUR OWN code ===")
print("""
If you have two files in the same folder:

    transform.py
        def normalize_domain(value): ...

    run.py
        from transform import normalize_domain
        print(normalize_domain("www.x.de"))

Python finds transform.py because it's next to run.py. (Packages and folders work the
same way, with an __init__.py file or by running with `python -m`.)
""")

print("=== 3. A typical GTM project layout ===")
print("""
    my-pipeline/
        README.md            what it does, how to run it, design decisions
        requirements.txt     packages to install
        .env.example         names of the keys needed (no real values)
        .gitignore           .venv/, .env, logs, output files
        src/
            config.py        settings: thresholds, team lists, batch size
            extract.py       read CSVs, call APIs (with retries, pagination)
            transform.py     normalise, dedupe (pure functions)
            score.py         scoring and routing rules (pure functions)
            load.py          write to the CRM (batch upserts, dry run)
            run_pipeline.py  main(): runs the steps in order, logs a summary
        tests/
            test_transform.py
            test_score.py

Why split it: each file is short, easy to test and easy to hand over.
""")

print("=== 4. `if __name__ == '__main__':` ===")
print("""
Code under this line runs only when you run the file directly
(python run.py), NOT when another file imports it. So you can import
functions from a file without triggering its main program.
""")

print("=== 5. argparse: command-line flags like --dry-run ===")


def parse_args():
    parser = argparse.ArgumentParser(description="Example pipeline runner")
    parser.add_argument("--dry-run", action="store_true",
                        help="do everything except writing to the CRM")
    parser.add_argument("--limit", type=int, default=None,
                        help="only process the first N records")
    return parser.parse_args()


def main():
    args = parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    log = logging.getLogger("runner")
    records = [f"company_{i}" for i in range(1, 11)]
    if args.limit:
        records = records[: args.limit]
    log.info("Processing %d records (dry_run=%s)", len(records), args.dry_run)
    written = 0 if args.dry_run else len(records)
    log.info("SUMMARY read=%d written=%d dry_run=%s", len(records), written, args.dry_run)


if __name__ == "__main__":
    main()
    print("\nTry: --help, --limit 3, --dry-run")
