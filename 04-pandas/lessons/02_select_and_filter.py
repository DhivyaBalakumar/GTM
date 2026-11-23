"""
pandas lesson 2: selecting and filtering
========================================

Run me:  python 04-pandas/lessons/02_select_and_filter.py
"""
from pathlib import Path

import pandas as pd

DATA = Path(__file__).resolve().parents[2] / "data"
pd.set_option("display.width", 160)
df = pd.read_csv(DATA / "crm_accounts.csv")

print("=== 1. Columns ===")
print(df["name"].head(3))               # one column -> Series
print(df[["name", "owner"]].head(3))    # several columns -> DataFrame (note the double [[ ]])

print("\n=== 2. Filter rows with a condition ===")
german = df[df["country"] == "DE"]
print(german[["name", "country"]])
# How it works: df["country"] == "DE" is a column of True/False; df[...] keeps the True rows.
print((df["country"] == "DE").head())

print("\n=== 3. Two conditions: use & (and), | (or), and BRACKETS around each ===")
hot_dach = df[(df["country"].isin(["DE", "AT", "CH"])) & (df["score"] >= 75)]
print(hot_dach[["name", "country", "score"]])
nl_or_be = df[(df["country"] == "NL") | (df["country"] == "BE")]
print(nl_or_be[["name", "country"]])
# Python's `and`/`or` DON'T work here; pandas needs & and |.

print("\n=== 4. isin: match a list ===")
print(df[df["industry"].isin(["Software", "Fintech"])][["name", "industry"]].head())

print("\n=== 5. ~ means NOT ===")
print(df[~df["country"].isin(["DE"])][["name", "country"]].head())

print("\n=== 6. Missing values in filters ===")
print("no owner:\n", df[df["owner"].isna()][["name", "owner"]])
print("has owner count:", df["owner"].notna().sum())

print("\n=== 7. Text filters ===")
print(df[df["name"].str.contains("tech", case=False, na=False)][["name"]])
print(df[df["domain"].str.endswith(".de", na=False)][["domain"]].head())

print("\n=== 8. between ===")
print(df[df["employees"].between(20, 500)][["name", "employees"]].head())   # inclusive both ends

print("\n=== 9. loc: rows by condition AND columns by name, in one go ===")
print(df.loc[df["score"] >= 80, ["name", "score", "owner"]])

print("\n=== 10. iloc: by position ===")
print(df.iloc[0:3, 0:3])        # first 3 rows, first 3 columns

print("\n=== 11. query(): an alternative, readable syntax ===")
print(df.query("score >= 80 and country == 'DE'")[["name", "score"]])

# ---------------------------------------------------------------------------
# TRY IT
# 1. Software companies with 20-500 employees and no owner.
# 2. Accounts created in November 2026 (hint: df["created_at"].str.startswith("2026-11")).
# 3. Count accounts per owner, but only for score >= 70.
# ---------------------------------------------------------------------------
