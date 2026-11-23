# Module 4: pandas (tables of data)

pandas holds data as a **DataFrame**: a table with named columns, like Excel you control with code.
One line can clean a whole column of 10,000 rows. This is the "clean, deduplicate, score" step in the
job post, and the first thing a live-coding task usually asks for ("here's a CSV…").

## Lessons (run each one and read the output next to the code)

| # | File | You'll learn |
| --- | --- | --- |
| 1 | [01_load_and_look.py](lessons/01_load_and_look.py) | DataFrame vs Series, read_csv, head, shape, info, describe, value_counts |
| 2 | [02_select_and_filter.py](lessons/02_select_and_filter.py) | Columns, loc/iloc, boolean filters, &, \|, isin, str.contains |
| 3 | [03_clean_and_transform.py](lessons/03_clean_and_transform.py) | str methods, apply, map, to_numeric, missing values (NaN), new columns |
| 4 | [04_dedupe_sort_group_merge.py](lessons/04_dedupe_sort_group_merge.py) | drop_duplicates keeping the best row, sort_values, groupby/agg, merge with indicator |
| 5 | [05_output.py](lessons/05_output.py) | to_csv, to_dict("records"), the NaN-in-JSON trap, to_sql, read_sql, dates |

## Exercise

[exercises/ex01_clean_score.py](exercises/ex01_clean_score.py): turn `data/leads_raw.csv` (25 messy
rows) into 19 clean, unique, scored companies, find which are already in the CRM, and save them.
Solution: [solutions/ex01_clean_score.py](solutions/ex01_clean_score.py).

## The 15 lines you'll use 90% of the time

```python
df = pd.read_csv("file.csv", dtype=str)                 # load (all as text: convert on purpose)
df.head(); df.shape; df.info(); df.isna().sum()          # look
df[df["country"] == "DE"]                                # filter
df[(df["a"] > 5) & (df["b"] == "x")]                     # two conditions: & and brackets
df["domain"] = df["website"].apply(normalize_domain)     # new column from a function
df["employees"] = pd.to_numeric(df["employees"], errors="coerce")   # text -> number, bad -> NaN
df["industry"] = df["industry"].str.strip().str.lower()  # clean a text column
df = df.dropna(subset=["domain"])                        # drop rows missing a key
df = df.sort_values("filled", ascending=False).drop_duplicates("domain", keep="first")  # dedupe, keep best
df.groupby("country")["score"].mean()                    # average per group
df["country"].value_counts()                             # count per value
df.merge(crm, on="domain", how="left", indicator=True)   # join two tables
records = df.astype(object).where(df.notna(), None).to_dict(orient="records")   # -> list of dicts, NaN -> None
df.to_csv("clean.csv", index=False)                      # save
```

## Skip for now

Pivot tables, multi-indexes, plotting, performance tuning.
