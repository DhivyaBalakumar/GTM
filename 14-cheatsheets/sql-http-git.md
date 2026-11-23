# Cheat sheet: SQL, HTTP/requests, Git and terminal

## SQL

```sql
SELECT cols FROM t WHERE cond ORDER BY c DESC LIMIT 10;
IN (...)   LIKE '%x%'   IS NULL   BETWEEN a AND b   DISTINCT   AS alias
COUNT(*)  COUNT(col)  SUM()  AVG()  MIN()  MAX()  ROUND(x, 1)
GROUP BY c HAVING COUNT(*) > 1
JOIN t2 ON t2.id = t.t2_id        LEFT JOIN ... WHERE t2.id IS NULL      -- rows with no match
CASE WHEN c THEN x WHEN d THEN y ELSE z END
COALESCE(col, 'default')   NULLIF(x, 0)   LOWER()  UPPER()  TRIM()  SUBSTR(s, start, len)  INSTR(s, '@')
100.0 * SUM(flag) / COUNT(*)                                             -- a percentage
WITH x AS (SELECT ...) SELECT ... FROM x;
ROW_NUMBER() OVER (PARTITION BY c ORDER BY d DESC)                       -- dedupe / top per group
SUM(x) OVER (ORDER BY d)                                                 -- running total
INSERT INTO t (a, b) VALUES (1, 2) ON CONFLICT(a) DO UPDATE SET b = excluded.b;   -- upsert
-- runs in order: FROM, WHERE, GROUP BY, HAVING, SELECT, ORDER BY, LIMIT
```

## HTTP and requests

```python
r = requests.get(url, params={"limit": 100}, headers={"Authorization": f"Bearer {key}"}, timeout=10)
r = requests.post(url, json=body, headers=h, timeout=10)      # also .patch / .put / .delete
r.status_code   r.ok   r.json()   r.text   r.headers.get("Retry-After")   r.raise_for_status()
session = requests.Session(); session.headers.update(h)
except (requests.ConnectionError, requests.Timeout): ...   except requests.HTTPError as e: e.response.status_code
```

| Code | Meaning | Action |
| --- | --- | --- |
| 200 / 201 / 204 | OK / created / no content | Continue |
| 400 | Bad request | Fix, don't retry |
| 401 / 403 | Bad key / no permission | Fix key or scopes, don't retry |
| 404 | Not found | Handle (enrichment: "no data") |
| 409 | Conflict (duplicate) | Update instead |
| **429** | Rate limited | **Wait (Retry-After), retry** |
| **500 / 502 / 503 / 504** | Server problem | **Retry with backoff** |

Retry recipe: `wait = base * 2 ** (attempt - 1) + random.uniform(0, 0.5)`, max 5 tries, then raise.
Pagination: loop on `data["paging"]["next"]["after"]` until missing. Batching: `records[i:i+100]`.

## Git and terminal

```
git clone <url>   git status   git diff   git add .   git commit -m "msg"   git push   git pull
git log --oneline   git checkout -- file   git switch -c branch
pwd   cd folder   cd ..   dir / ls   mkdir x   python file.py   code .   Ctrl+C
python -m venv .venv   .venv\Scripts\Activate.ps1   pip install -r requirements.txt   pytest -v
```

`.gitignore`: `.venv/  .env  __pycache__/  *.log  output/  *.db`. Never commit keys; if you do,
rotate them.

## Cron

```
┌ minute (0-59) ┌ hour (0-23) ┌ day of month ┌ month ┌ day of week (0-6, Sun=0)
0 * * * *        every hour
30 7 * * 1-5     07:30 Mon-Fri
0 2 * * *        02:00 daily
```
