"""
pandas lesson 3: cleaning and transforming columns
==================================================

Run me:  python 04-pandas/lessons/03_clean_and_transform.py
"""
from pathlib import Path

import numpy as np
import pandas as pd

DATA = Path(__file__).resolve().parents[2] / "data"
pd.set_option("display.width", 160)
df = pd.read_csv(DATA / "leads_raw.csv", dtype=str)

print("=== 1. .str methods clean a whole text column at once ===")
df["industry_clean"] = df["industry"].str.strip().str.lower()
print(df[["industry", "industry_clean"]].head(6))

print("\n=== 2. map: replace values using a dictionary ===")
COUNTRY = {"germany": "DE", "netherlands": "NL", "austria": "AT"}
df["country_clean"] = df["country"].str.strip().str.lower().map(COUNTRY).fillna(df["country"].str.upper())
print(df[["country", "country_clean"]].drop_duplicates().head(8))

INDUSTRY = {"saas": "Software", "software": "Software", "fintech": "Fintech", "health tech": "Healthtech"}
df["industry_std"] = df["industry_clean"].map(INDUSTRY).fillna(df["industry"])
print(df["industry_std"].value_counts(dropna=False))

print("\n=== 3. apply: run YOUR function on every value ===")


def normalize_domain(value):
    if not isinstance(value, str) or not value.strip():
        return ""
    v = value.strip().lower()
    if "@" in v:
        v = v.split("@")[-1]
    for prefix in ("https://", "http://", "www."):
        if v.startswith(prefix):
            v = v[len(prefix):]
    return v.split("/")[0]


df["domain"] = df["website"].apply(normalize_domain)
# Fall back to the email's domain where the website was empty:
no_site = df["domain"] == ""
df.loc[no_site, "domain"] = df.loc[no_site, "contact_email"].apply(normalize_domain)
print(df[["website", "contact_email", "domain"]].head(12))

print("\n=== 4. apply across a whole ROW (axis=1) ===")


def label(row):
    return f"{row['company'] or '?'} ({row['country']})"


df["label"] = df.apply(label, axis=1)
print(df["label"].head(3))
# Row-wise apply is slower; fine for thousands of rows, avoid for millions.

print("\n=== 5. Numbers from messy text ===")
print(pd.to_numeric(pd.Series(["120", "51-200", "abc", None]), errors="coerce"))
# errors="coerce" turns anything unparseable into NaN instead of crashing.


def parse_employees(value):
    if not isinstance(value, str):
        return np.nan
    value = value.strip()
    if "-" in value:
        low, _, high = value.partition("-")
        if low.isdigit() and high.isdigit():
            return (int(low) + int(high)) // 2
        return np.nan
    return int(value) if value.isdigit() else np.nan


df["employees_num"] = df["employees"].apply(parse_employees)
print(df[["employees", "employees_num"]].head(13))

print("\n=== 6. Missing values: NaN ===")
print("missing employees:", df["employees_num"].isna().sum())
print(df["industry"].fillna("Unknown").value_counts().head(3))   # fill blanks
print("rows with a domain:", len(df.dropna(subset=["website"])))  # drop rows missing website
# NaN is "not a number": pandas' missing value. NaN != NaN, so use isna(), never == np.nan.

print("\n=== 7. Conditional columns with np.where and np.select ===")
df["is_dach"] = np.where(df["country_clean"].isin(["DE", "AT", "CH"]), "yes", "no")
conditions = [df["employees_num"] >= 500, df["employees_num"] >= 20, df["employees_num"] < 20]
df["segment"] = np.select(conditions, ["Enterprise", "Mid-market", "Small"], default="Unknown")
print(df[["company", "employees_num", "is_dach", "segment"]].head(8))

print("\n=== 8. Vectorised scoring (fast, readable) ===")
score = pd.Series(0, index=df.index)
score += np.where(df["industry_std"].isin(["Software", "Fintech", "Healthtech"]), 25, 0)
score += np.where(df["employees_num"].between(20, 500), 20, 0)
score += np.where(df["country_clean"].isin(["DE", "AT", "CH", "NL", "BE", "LU"]), 15, 0)
df["fit_score"] = score
print(df[["company", "industry_std", "employees_num", "country_clean", "fit_score"]].head(8))

print("\n=== 9. Renaming and dropping columns ===")
slim = df.rename(columns={"contact_email": "email"}).drop(columns=["label", "industry_clean"])
print(list(slim.columns))

# ---------------------------------------------------------------------------
# TRY IT
# 1. Add an `email_is_personal` column (gmail.com / yahoo.com).
# 2. Add a `tier` column from fit_score using np.select (A >= 50, B >= 35, else C).
# 3. Title-case the `city` column and strip spaces.
# ---------------------------------------------------------------------------
