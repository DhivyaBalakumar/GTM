"""
pandas lesson 5: getting data OUT (CSV, records for APIs, SQL) and dates
========================================================================

Run me:  python 04-pandas/lessons/05_output.py
"""
import json
import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
DATA, OUT = REPO / "data", REPO / "output"
OUT.mkdir(exist_ok=True)

crm = pd.read_csv(DATA / "crm_accounts.csv")

print("=== 1. Save to CSV ===")
crm.to_csv(OUT / "crm_copy.csv", index=False)     # index=False: don't write the 0,1,2... column
print("saved crm_copy.csv")

print("\n=== 2. Table -> list of dictionaries (what APIs want) ===")
records = crm.head(2).to_dict(orient="records")
print(records)

print("\n=== 3. THE NaN TRAP: NaN is not valid JSON ===")
row_with_nan = crm[crm["owner"].isna()].head(1)
print(row_with_nan[["name", "owner"]])
bad = row_with_nan.to_dict(orient="records")
print("owner value:", bad[0]["owner"], type(bad[0]["owner"]))
try:
    json.dumps(bad, allow_nan=False)               # requests' json= behaves like this for APIs
except ValueError as e:
    print("ValueError:", e)
# Fix: convert NaN -> None (None becomes JSON null, or you can skip the field entirely)
clean = row_with_nan.astype(object).where(row_with_nan.notna(), None).to_dict(orient="records")
print("fixed:", json.dumps(clean))
# Even better for CRMs: DROP empty fields so you never overwrite real data with blanks.
no_blanks = [{k: v for k, v in r.items() if v is not None} for r in clean]
print("no blanks:", no_blanks)

print("\n=== 4. numpy ints are not JSON either ===")
value = crm["employees"].iloc[0]
print(type(value))                                 # numpy.int64
print(json.dumps({"employees": int(value)}))       # convert with int()

print("\n=== 5. To SQL and back (SQLite is built into Python) ===")
con = sqlite3.connect(":memory:")                  # a temporary database in memory
crm.to_sql("accounts", con, index=False)
pd.read_csv(DATA / "crm_deals.csv").to_sql("deals", con, index=False)
q = """
SELECT a.owner, COUNT(d.id) AS deals, SUM(d.amount_eur) AS pipeline_eur
FROM deals d JOIN accounts a ON a.id = d.account_id
WHERE d.stage NOT IN ('closed_won', 'closed_lost')
GROUP BY a.owner
ORDER BY pipeline_eur DESC
"""
print(pd.read_sql(q, con))

print("\n=== 6. Dates ===")
deals = pd.read_csv(DATA / "crm_deals.csv", parse_dates=["created_at", "closed_at"])
print(deals.dtypes[["created_at", "closed_at"]])
deals["days_to_close"] = (deals["closed_at"] - deals["created_at"]).dt.days
print(deals.loc[deals["closed_at"].notna(), ["name", "days_to_close"]])
deals["month"] = deals["created_at"].dt.to_period("M").astype(str)
print(deals.groupby("month").size())
recent = deals[deals["created_at"] >= pd.Timestamp("2026-10-01")]
print("deals created since 1 Oct:", len(recent))

print("\n=== 7. Speed-to-lead from inbound_leads.csv ===")
inbound = pd.read_csv(DATA / "inbound_leads.csv", parse_dates=["created_at", "first_contacted_at"])
inbound["minutes_to_contact"] = (inbound["first_contacted_at"] - inbound["created_at"]).dt.total_seconds() / 60
print(inbound.groupby("source")["minutes_to_contact"].median().round(0))
print("never contacted:", inbound["first_contacted_at"].isna().sum())

# ---------------------------------------------------------------------------
# TRY IT
# 1. Save only tier-A accounts (score >= 75) to output/tier_a.csv.
# 2. Write a function df_to_api_records(df) that returns records with NaN fields removed.
# 3. Meeting rate (%) per source from inbound_leads.csv.
# ---------------------------------------------------------------------------
