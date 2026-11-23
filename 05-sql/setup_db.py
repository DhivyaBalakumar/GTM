"""
Build output/gtm.db (SQLite) from the CSV files in data/.

Run:  python 05-sql/setup_db.py

SQLite is a database stored in a single file, built into Python. Perfect for practice:
the SQL is almost identical to Postgres, MySQL, BigQuery or Snowflake for everything here.
"""
import sqlite3
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[1]
DATA, OUT = REPO / "data", REPO / "output"
DB = OUT / "gtm.db"

TABLES = {
    "accounts": "crm_accounts.csv",
    "contacts": "crm_contacts.csv",
    "deals": "crm_deals.csv",
    "leads": "inbound_leads.csv",
}


def main():
    OUT.mkdir(exist_ok=True)
    with sqlite3.connect(DB) as con:
        for table, filename in TABLES.items():
            df = pd.read_csv(DATA / filename)
            df.to_sql(table, con, if_exists="replace", index=False)
            print(f"{table:9} {len(df):3} rows  columns: {', '.join(df.columns)}")
    print(f"\nDatabase ready: {DB}")
    print("Next: python 05-sql/run_sql.py 05-sql/lessons/01_select_where.sql")


if __name__ == "__main__":
    main()
