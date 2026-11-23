# Cheat sheet: Python and pandas

## Python

```python
# strings
s.lower()  s.upper()  s.strip()  s.replace(a, b)  s.split(",")  ", ".join(lst)
s.startswith("http")  s.endswith(".de")  "x" in s  s[0]  s[-1]  s[2:5]  f"{x:.1f}"  f"{p:.0%}"

# lists
lst.append(x)  lst.extend([..])  lst.pop()  lst[-1]  lst[1:3]  len(lst)  sorted(lst, reverse=True)
x in lst  lst[i:i+10]  (batching)  max(lst)  sum(lst)

# dicts
d["k"]  d.get("k")  d.get("k", default)  d["k"] = v  d.update({...})  del d["k"]
for k, v in d.items():   "k" in d   d.setdefault(k, []).append(x)
{c["domain"]: c for c in rows}           # lookup table

# sets
s = set()  s.add(x)  x in s  a & b  a | b  a - b

# control flow
if a and b: ... elif not c: ... else: ...
for i, x in enumerate(lst, start=1):   for a, b in zip(l1, l2):   while True: ... break / continue
x = "A" if score >= 75 else "B"

# functions
def f(a, b=1, *args, **kwargs) -> int:
    """docstring"""
    return a + b

# comprehensions and sorting
[f(x) for x in lst if cond]   {k: v for k, v in pairs}   any(...)  all(...)
sorted(rows, key=lambda r: r["score"], reverse=True)[:5]

# errors
try: ...
except ValueError as e: ...
else: ...
finally: ...
raise ValueError("message")

# files
with open(p, encoding="utf-8") as f: rows = list(csv.DictReader(f))
with open(p, "w", newline="", encoding="utf-8") as f: w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(rows)
json.loads(text)  json.dumps(obj, indent=2)  json.load(f)  json.dump(obj, f)
Path(__file__).resolve().parent / "data" / "x.csv"

# standard library
os.getenv("KEY")  time.sleep(2)  random.uniform(0, 0.5)  datetime.now(timezone.utc)
date.fromisoformat("2026-11-20")  timedelta(days=90)  Counter(lst).most_common(3)
defaultdict(list)  next(cycle(["a", "b"]))  re.search(r"iso\s*27001", text, re.I)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__); log.info("x=%s", x)
```

## pandas

```python
df = pd.read_csv(p, dtype=str)       df.to_csv(p, index=False)
df.head()  df.shape  df.columns  df.info()  df.describe()  df.isna().sum()  df["c"].value_counts()

df["c"]  df[["a", "b"]]  df.loc[mask, ["a", "b"]]  df.iloc[0:3]
df[df["n"] > 5]   df[(a) & (b)]   df[(a) | (b)]   df[~mask]   df["c"].isin([...])   df["n"].between(20, 500)
df["c"].str.lower().str.strip()   .str.replace(r"^www\.", "", regex=True)   .str.split("@").str[-1]
df["c"].str.contains("x", case=False, na=False)

df["new"] = df["c"].apply(func)             df["new"] = df.apply(func, axis=1)
df["c"].map({"germany": "DE"})               pd.to_numeric(df["c"], errors="coerce")
np.where(cond, a, b)                          np.select([c1, c2], [v1, v2], default=v3)
df.fillna({"c": "Unknown"})   df.dropna(subset=["domain"])   df.rename(columns={...})   df.drop(columns=[...])

df.sort_values("c", ascending=False)         df.nlargest(5, "score")
df.sort_values("filled", ascending=False).drop_duplicates(subset="domain", keep="first")   # dedupe, keep best
df.duplicated(subset="domain", keep=False)

df.groupby("c").size()   df.groupby("a")["b"].mean()
df.groupby("owner").agg(n=("id", "count"), avg=("score", "mean"))
df.merge(o, on="k", how="left", indicator=True)   pd.concat([a, b], ignore_index=True)

pd.read_csv(p, parse_dates=["created_at"])   df["d"].dt.days   df["d"].dt.to_period("M")
df.to_dict(orient="records")
df.astype(object).where(df.notna(), None).to_dict(orient="records")    # NaN -> None for JSON
df.to_sql("t", con, if_exists="replace", index=False)   pd.read_sql(query, con)
```
