"""
Run every statement in a .sql file against output/gtm.db and print the results.

Run:  python 05-sql/run_sql.py 05-sql/lessons/01_select_where.sql

The comment lines (-- ...) directly above each query are printed as its title.
"""
import sqlite3
import sys
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[1]
DB = REPO / "output" / "gtm.db"
pd.set_option("display.width", 160)
pd.set_option("display.max_columns", 20)


def statements(text):
    """Split SQL text into (comment, statement) pairs, respecting ; inside strings."""
    buffer, comments = [], []
    for line in text.splitlines():
        stripped = line.strip()
        if not buffer and stripped.startswith("--"):
            comments.append(stripped.lstrip("-").strip())
            continue
        if not stripped and not buffer:
            comments = []
            continue
        buffer.append(line)
        joined = "\n".join(buffer)
        if sqlite3.complete_statement(joined):
            yield " ".join(c for c in comments if c), joined.strip()
            buffer, comments = [], []


def main():
    if len(sys.argv) != 2:
        print("Usage: python 05-sql/run_sql.py path/to/file.sql")
        sys.exit(1)
    if not DB.exists():
        print("Database not found. Run: python 05-sql/setup_db.py")
        sys.exit(1)
    text = Path(sys.argv[1]).read_text(encoding="utf-8")
    con = sqlite3.connect(DB)
    for i, (title, sql) in enumerate(statements(text), start=1):
        print("=" * 100)
        print(f"[{i}] {title}" if title else f"[{i}]")
        print("-" * 100)
        print(sql)
        print("-" * 100)
        try:
            if sql.lstrip().upper().startswith(("SELECT", "WITH")):
                print(pd.read_sql(sql, con).to_string(index=False))
            else:
                cur = con.execute(sql)
                con.commit()
                print(f"OK ({cur.rowcount if cur.rowcount != -1 else 0} rows affected)")
        except Exception as e:
            print(f"ERROR: {e}")
        print()
    con.close()


if __name__ == "__main__":
    main()
