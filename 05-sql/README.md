# Module 5: SQL

SQL is the language for asking questions of tables. If Python is the builder that *does* things, SQL
is the question-asker that tells you *what happened*. Target: **5–15 line queries** that filter,
count per group, join, find duplicates and score. About 15% of your technical prep. The live round
reportedly includes at least one SQL question.

## Setup (once)

```powershell
python 05-sql/setup_db.py          # builds output/gtm.db from the CSVs in data/
```

Tables it creates:

| Table | Rows | Columns |
| --- | --- | --- |
| `accounts` | 15 | id, name, domain, country, industry, employees, owner, score, created_at |
| `contacts` | 14 | id, account_id, name, email, title, role, opened_sequence, replied |
| `deals` | 12 | id, account_id, name, stage, amount_eur, owner, created_at, closed_at |
| `leads` | 16 | id, email, source, country, created_at, first_contacted_at, meeting_booked |

## Lessons

Each lesson is a `.sql` file full of comments and queries. Run it with:

```powershell
python 05-sql/run_sql.py 05-sql/lessons/01_select_where.sql
```

It prints each query and its result. Then edit the queries and re-run.

| # | File | You'll learn |
| --- | --- | --- |
| 1 | [01_select_where.sql](lessons/01_select_where.sql) | SELECT, FROM, WHERE, AND/OR, IN, BETWEEN, LIKE, IS NULL, ORDER BY, LIMIT, DISTINCT |
| 2 | [02_aggregate_group.sql](lessons/02_aggregate_group.sql) | COUNT, SUM, AVG, MIN, MAX, GROUP BY, HAVING, finding duplicates |
| 3 | [03_joins.sql](lessons/03_joins.sql) | INNER JOIN, LEFT JOIN, LEFT JOIN + IS NULL, joining three tables |
| 4 | [04_case_nulls_dates.sql](lessons/04_case_nulls_dates.sql) | CASE WHEN, COALESCE, string functions, dates, conversion rates |
| 5 | [05_ctes_windows.sql](lessons/05_ctes_windows.sql) | WITH (CTEs), subqueries, ROW_NUMBER, RANK, running totals |
| 6 | [06_create_insert_upsert.sql](lessons/06_create_insert_upsert.sql) | CREATE TABLE, keys, INSERT, UPDATE, DELETE, UNIQUE, upsert with ON CONFLICT |

## Exercises

[exercises.md](exercises.md) has 15 GTM questions. Write your answers in a file, run them with
`run_sql.py`, then compare with [solutions.sql](solutions.sql).

## The order SQL runs in (explains most confusing errors)

You **write** `SELECT … FROM … WHERE … GROUP BY … HAVING … ORDER BY … LIMIT`.
The database **runs** it as:

```
FROM → WHERE → GROUP BY → HAVING → SELECT → ORDER BY → LIMIT
```

So `WHERE` can't use an aggregate like `COUNT(*)` (groups don't exist yet); use `HAVING`.
And `WHERE` can't use a column alias defined in `SELECT`, but `ORDER BY` can.

## Key ideas

- **Primary key:** a column that uniquely identifies each row (`accounts.id`).
- **Foreign key:** a column pointing to another table's primary key (`contacts.account_id` → `accounts.id`).
- **NULL** means unknown/missing. `NULL = NULL` is not true; use `IS NULL`. `COUNT(column)` skips
  NULLs; `COUNT(*)` counts rows.
- **JOIN** combines tables on a key. **LEFT JOIN** keeps every row from the left table even with no
  match (the right side becomes NULL).
- Same ideas in pandas: `WHERE` = boolean filter, `GROUP BY` = `groupby`, `JOIN` = `merge`.

## Skip for now

Stored procedures, triggers, index tuning, database administration.
