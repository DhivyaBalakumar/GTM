# Module 15: Deep dives

Long-form, very explanatory guides on the foundations that everything else builds on. Read them
alongside the hands-on modules, and run the companion code as you go.

| # | Guide | Covers | Companion code |
| --- | --- | --- | --- |
| 1 | [01-data-types-and-structures.md](01-data-types-and-structures.md) | Data types vs data structures; str, int, float, bool, None, NaN; converting types; missing values; mutability and the copy trap; lists, tuples, dicts, sets; nested API data; pandas Series and DataFrames; choosing the right structure; common bugs; practice questions | [code/types_and_structures_demo.py](code/types_and_structures_demo.py) |
| 2 | [02-json-apis-and-pandas.md](02-json-apis-and-pandas.md) | How the three fit together; JSON in detail and the four kinds you'll meet; APIs (requests, methods, status codes, auth, docs); `requests`; rate limits, retries, pagination, batching, idempotency; which APIs this role uses; pandas in detail and in this role; an end-to-end example; interview Q&A | [code/json_apis_pandas_demo.py](code/json_apis_pandas_demo.py) (needs the practice API running) |
| 3 | [03-deduplication.md](03-deduplication.md) | Dedupe from zero to advanced in 11 levels: exact matches, normalising, keys, survivorship, golden records, pandas and SQL, fuzzy matching, entity resolution, prevention with upserts, measuring; interview answers | [code/dedupe_demo.py](code/dedupe_demo.py) |

Practice drill: [code/core_patterns_drill.py](code/core_patterns_drill.py) rebuilds the 6 core patterns
from their recipes and checks your answers (guide: [HOW_TO_LEARN_THE_CODE.md](../HOW_TO_LEARN_THE_CODE.md);
reference answers: [code/core_patterns_solutions.py](code/core_patterns_solutions.py)).

One-page summary of guide 1: [14-cheatsheets/data-types-and-structures.md](../14-cheatsheets/data-types-and-structures.md).

```powershell
python 15-deep-dives/code/types_and_structures_demo.py
python 15-deep-dives/code/dedupe_demo.py

# Terminal 1
python 06-apis-and-webhooks/practice_server.py
# Terminal 2
python 15-deep-dives/code/json_apis_pandas_demo.py
```

When to read them: guide 1 alongside Python lessons 1–4 (week 1); guide 2 alongside the pandas and API
modules (week 2); guide 3 alongside pandas lesson 4 and module 08 (data quality).
