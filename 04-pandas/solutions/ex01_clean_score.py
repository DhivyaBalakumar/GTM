"""Solution to the pandas exercise."""
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
    return pd.read_csv(DATA / "leads_raw.csv", dtype=str)


def _normalize(series):
    return (series.fillna("").str.strip().str.lower()
            .str.replace(r"^https?://", "", regex=True)
            .str.replace(r"^www\.", "", regex=True)
            .str.split("/").str[0]
            .str.split("@").str[-1])


def add_domain(df):
    df = df.copy()
    from_site = _normalize(df["website"])
    from_email = _normalize(df["contact_email"])
    df["domain"] = from_site.where(from_site != "", from_email)
    return df


def drop_invalid(df):
    return df[(df["domain"] != "") & (~df["domain"].isin(PERSONAL))].copy()


def _parse_employees(value):
    if not isinstance(value, str):
        return np.nan
    value = value.strip()
    if "-" in value:
        low, _, high = value.partition("-")
        return (int(low) + int(high)) // 2 if low.isdigit() and high.isdigit() else np.nan
    return float(value) if value.isdigit() else np.nan


def standardise(df):
    df = df.copy()
    country = df["country"].fillna("").str.strip()
    df["country"] = country.str.lower().map(COUNTRY_MAP).fillna(country.str.upper())
    industry = df["industry"].fillna("").str.strip()
    df["industry"] = industry.str.lower().map(INDUSTRY_MAP).fillna(industry)
    df["employees"] = df["employees"].apply(_parse_employees).astype(float)
    return df


def dedupe(df):
    df = df.copy()
    filled = df.notna() & (df.astype(str).apply(lambda col: col.str.strip()) != "")
    df["_filled"] = filled.sum(axis=1)
    df = (df.sort_values("_filled", ascending=False, kind="stable")
            .drop_duplicates(subset="domain", keep="first")
            .drop(columns="_filled")
            .sort_values("domain")
            .reset_index(drop=True))
    return df


def score(df):
    df = df.copy()
    points = np.where(df["industry"].isin(["Software", "Fintech", "Healthtech"]), 25, 0)
    points = points + np.where(df["employees"].between(20, 500), 20, 0)
    points = points + np.where(df["country"].isin(["DE", "AT", "CH", "NL", "BE", "LU"]), 15, 0)
    df["fit_score"] = points
    df["tier"] = np.select([df["fit_score"] >= 50, df["fit_score"] >= 35], ["A", "B"], default="C")
    return df


def match_crm(df, crm):
    crm = crm.copy()
    crm["domain"] = crm["domain"].str.lower().str.strip()
    crm = crm.drop_duplicates(subset="domain", keep="first")[["domain", "owner"]]
    merged = df.merge(crm.rename(columns={"owner": "crm_owner"}), on="domain", how="left", indicator=True)
    merged["in_crm"] = merged["_merge"] == "both"
    return merged.drop(columns="_merge")


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
    problems = _checks()
    print("\n".join(problems) if problems else "All checks passed")
