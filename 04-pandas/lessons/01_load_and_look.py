"""
pandas lesson 1: load and look
==============================

Run me:  python 04-pandas/lessons/01_load_and_look.py

ALWAYS look at the data before writing logic. In live coding, say:
"Let me print a few rows first."
"""
from pathlib import Path

import pandas as pd

DATA = Path(__file__).resolve().parents[2] / "data"
pd.set_option("display.width", 160)
pd.set_option("display.max_columns", 20)

print("=== 1. Load a CSV into a DataFrame ===")
df = pd.read_csv(DATA / "leads_raw.csv")
print(type(df))

print("\n=== 2. First and last rows ===")
print(df.head(3))          # first 3 rows (default 5)
print(df.tail(2))          # last 2

print("\n=== 3. Size and columns ===")
print("shape (rows, columns):", df.shape)
print("columns:", list(df.columns))

print("\n=== 4. Types and missing values ===")
df.info()
# Notice: `employees` is 'object' (text), not a number, because of values like "51-200" and "abc".
print("\nmissing values per column:")
print(df.isna().sum())

print("\n=== 5. A column is a Series ===")
countries = df["country"]
print(type(countries))
print(countries.head())

print("\n=== 6. value_counts: what values exist, and how often ===")
print(df["country"].value_counts())
# DE vs Germany, NL vs Netherlands: the same thing written differently. That's a cleaning job.
print(df["industry"].value_counts(dropna=False))   # include missing (NaN)

print("\n=== 7. unique and nunique ===")
print(df["source"].unique(), "| how many:", df["source"].nunique())

print("\n=== 8. describe: quick stats ===")
print(df.describe(include="all").T[["count", "unique", "top"]])

print("\n=== 9. Reading everything as text (a safer default for messy data) ===")
df_text = pd.read_csv(DATA / "leads_raw.csv", dtype=str)
print(df_text.dtypes.head(3))
# dtype=str stops pandas guessing types wrongly (e.g. turning ZIP codes into numbers).
# Then you convert the columns you need, on purpose, in the cleaning step.

print("\n=== 10. Rows and single values ===")
print(df.iloc[0])                  # first row by position (a Series)
print(df.loc[0, "company"])        # one value: row label 0, column "company"

# ---------------------------------------------------------------------------
# TRY IT
# 1. How many leads came from each source?
# 2. Which columns have the most missing values?
# 3. Load data/crm_accounts.csv and print its shape and the owner counts.
# ---------------------------------------------------------------------------
