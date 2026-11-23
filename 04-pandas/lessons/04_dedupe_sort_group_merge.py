"""
pandas lesson 4: dedupe, sort, group and merge
==============================================

Run me:  python 04-pandas/lessons/04_dedupe_sort_group_merge.py
"""
from pathlib import Path

import pandas as pd

DATA = Path(__file__).resolve().parents[2] / "data"
pd.set_option("display.width", 160)

leads = pd.read_csv(DATA / "leads_raw.csv", dtype=str)
leads["domain"] = (leads["website"].fillna(leads["contact_email"]).fillna("")
                   .str.lower().str.strip()
                   .str.replace(r"^https?://", "", regex=True)
                   .str.replace(r"^www\.", "", regex=True)
                   .str.split("/").str[0]
                   .str.split("@").str[-1])
leads = leads[(leads["domain"] != "") & (~leads["domain"].isin(["gmail.com", "yahoo.com"]))]
print("rows after dropping personal/no-domain:", len(leads))

print("\n=== 1. Find duplicates ===")
dupes = leads[leads.duplicated(subset="domain", keep=False)].sort_values("domain")
print(dupes[["company", "domain", "employees", "industry"]])

print("\n=== 2. Dedupe, keeping the MOST COMPLETE row (the standard trick) ===")
# Step 1: count how many fields each row has filled.
leads["filled"] = leads.notna().sum(axis=1)
# Step 2: sort so the best row comes first, then keep the first per domain.
unique = (leads.sort_values("filled", ascending=False)
               .drop_duplicates(subset="domain", keep="first")
               .sort_values("domain"))
print("unique companies:", len(unique))
print(unique[["company", "domain", "employees", "filled"]].head(8))
# "Sort so the best is first, then keep first." Say this sentence in interviews.

print("\n=== 3. Sorting ===")
crm = pd.read_csv(DATA / "crm_accounts.csv")
print(crm.sort_values("score", ascending=False)[["name", "score"]].head(5))
print(crm.sort_values(["country", "score"], ascending=[True, False])[["country", "name", "score"]].head(6))
print(crm.nlargest(3, "score")[["name", "score"]])

print("\n=== 4. groupby: summaries per group ===")
print(crm.groupby("country").size())                        # rows per group
print(crm.groupby("owner")["score"].mean().round(1))         # average per group
print(crm.groupby("owner").agg(accounts=("id", "count"),
                               avg_score=("score", "mean"),
                               max_employees=("employees", "max")).round(1))
# dropna=False keeps the "no owner" group:
print(crm.groupby("owner", dropna=False).size())

print("\n=== 5. Duplicates INSIDE the CRM (a real data-quality check) ===")
crm["domain_key"] = crm["domain"].str.lower().str.strip()
dup_counts = crm.groupby("domain_key").size()
print(dup_counts[dup_counts > 1])     # peopleco.de appears twice: PeopleCo GmbH and PEOPLECO GMBH

print("\n=== 6. merge: join two tables on a shared key (like SQL JOIN) ===")
crm_small = crm[["domain_key", "owner", "score"]].drop_duplicates("domain_key")
merged = unique.merge(crm_small, left_on="domain", right_on="domain_key",
                      how="left", indicator=True)
print(merged[["company", "domain", "owner", "_merge"]].head(10))
print(merged["_merge"].value_counts())
# how="left" keeps every lead; owner is NaN when the company isn't in the CRM.
# indicator=True adds _merge: "both" = already in CRM, "left_only" = brand new.

print("\n=== 7. The four join types ===")
a = pd.DataFrame({"k": [1, 2, 3], "a": ["x", "y", "z"]})
b = pd.DataFrame({"k": [2, 3, 4], "b": ["p", "q", "r"]})
for how in ["inner", "left", "right", "outer"]:
    print(how, "->", a.merge(b, on="k", how=how).to_dict("records"))

print("\n=== 8. concat: stack tables with the same columns ===")
both = pd.concat([a, a], ignore_index=True)
print(both)

# ---------------------------------------------------------------------------
# TRY IT
# 1. How many unique leads are NOT in the CRM yet?
# 2. Average score per country in the CRM, highest first.
# 3. Join crm_deals.csv to crm_accounts.csv and sum amount_eur per owner.
# ---------------------------------------------------------------------------
