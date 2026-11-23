"""
pandas exercise: clean, dedupe, score, match against the CRM
=============================================================

Fill in each function using pandas, then run:
    python 04-pandas/exercises/ex01_clean_score.py

Input: data/leads_raw.csv (25 rows) and data/crm_accounts.csv
"""
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
DATA, OUT = REPO / "data", REPO / "output"

PERSONAL = {"gmail.com", "yahoo.com", "outlook.com", "hotmail.com"}
COUNTRY_MAP = {"germany": "DE", "netherlands": "NL", "austria": "AT"}
INDUSTRY_MAP = {"software": "Software", "saas": "Software", "fintech": "Fintech",
                "health tech": "Healthtech", "healthtech": "Healthtech"}


def load_leads():
    """Read leads_raw.csv with every column as text (dtype=str)."""
    raise NotImplementedError


def add_domain(df):
    """Return a copy with a `domain` column: from website, else from contact_email.
    Lowercase, no http(s)://, no www., no /path, part after @ for emails. Missing -> ""."""
    raise NotImplementedError


def drop_invalid(df):
    """Drop rows whose domain is "" or in PERSONAL. Return the remaining rows."""
    raise NotImplementedError


def standardise(df):
    """Return a copy where:
    - country: stripped; names mapped with COUNTRY_MAP (case-insensitive); codes uppercased
    - industry: stripped, lowercased, mapped with INDUSTRY_MAP; unmapped keep their original text
    - employees: a number column; "51-200" -> 125 (midpoint); unparseable -> NaN
    """
    raise NotImplementedError


def dedupe(df):
    """One row per domain, keeping the row with the most non-missing values
    (count "" as missing too). On a tie, keep the row that came first in the file.
    Return sorted by domain, index reset."""
    raise NotImplementedError


def score(df):
    """Add fit_score: +25 industry in {Software, Fintech, Healthtech}; +20 employees between
    20 and 500; +15 country in DE/AT/CH/NL/BE/LU. Add tier: "A" >= 50, "B" >= 35, else "C"."""
    raise NotImplementedError


def match_crm(df, crm):
    """Add `in_crm` (True/False) and `crm_owner` (owner from the CRM, NaN if none) by matching
    df.domain to crm.domain (lowercased). The CRM has a duplicate peopleco.de: use the first."""
    raise NotImplementedError


def run():
    df = load_leads()
    df = add_domain(df)
    df = drop_invalid(df)
    df = standardise(df)
    df = dedupe(df)
    df = score(df)
    df = match_crm(df, pd.read_csv(DATA / "crm_accounts.csv", dtype={"owner": str}))
    OUT.mkdir(exist_ok=True)
    df.sort_values("fit_score", ascending=False).to_csv(OUT / "leads_scored.csv", index=False)
    return df


# --------------------------------------------------------------------------- checks
def _checks():
    failures = []

    def check(label, got, expected):
        if got != expected:
            failures.append(f"{label}: expected {expected!r}, got {got!r}")

    df = run()
    check("rows", len(df), 19)
    check("unique domains", df["domain"].nunique(), 19)
    row = df.set_index("domain")
    check("peopleco employees", float(row.loc["peopleco.de", "employees"]), 120.0)
    check("brightforge tie keeps first row (51-200 -> 125)", float(row.loc["brightforge.io", "employees"]), 125.0)
    check("kranich from email", "kranich-logistik.de" in row.index, True)
    check("country mapped", row.loc["vektorcloud.nl", "country"], "NL")
    check("industry mapped", row.loc["brightforge.io", "industry"], "Software")
    check("altamira employees NaN", bool(pd.isna(row.loc["altamirapay.com", "employees"])), True)
    check("peopleco score", int(row.loc["peopleco.de", "fit_score"]), 60)
    check("peopleco tier", row.loc["peopleco.de", "tier"], "A")
    check("greenleaf score", int(row.loc["greenleafretail.com", "fit_score"]), 0)
    check("in crm count", int(df["in_crm"].sum()), 14)
    check("peopleco owner", row.loc["peopleco.de", "crm_owner"], "lena")
    check("output saved", (OUT / "leads_scored.csv").exists(), True)
    return failures


if __name__ == "__main__":
    try:
        problems = _checks()
    except NotImplementedError:
        print("Some functions still raise NotImplementedError. Fill them in and run again.")
    else:
        print("\n".join(problems) if problems else "All checks passed")
