-- SQL lesson 5: CTEs, subqueries and window functions
-- Run: python 05-sql/run_sql.py 05-sql/lessons/05_ctes_windows.sql

-- 1. Subquery: accounts scoring above the average
SELECT name, score FROM accounts
WHERE score > (SELECT AVG(score) FROM accounts)
ORDER BY score DESC;

-- 2. CTE (WITH): name a step, then use it like a table. Makes long queries readable.
WITH open_deals AS (
    SELECT account_id, SUM(amount_eur) AS open_eur
    FROM deals
    WHERE stage NOT IN ('closed_won', 'closed_lost')
    GROUP BY account_id
)
SELECT a.name, a.owner, o.open_eur
FROM open_deals o
JOIN accounts a ON a.id = o.account_id
ORDER BY o.open_eur DESC;

-- 3. Several CTEs in a row
WITH contact_counts AS (
    SELECT account_id, COUNT(*) AS n FROM contacts GROUP BY account_id
),
scored AS (
    SELECT a.id, a.name, a.score, COALESCE(cc.n, 0) AS contacts
    FROM accounts a LEFT JOIN contact_counts cc ON cc.account_id = a.id
)
SELECT * FROM scored WHERE score >= 70 AND contacts < 2 ORDER BY score DESC;

-- 4. Window function ROW_NUMBER: number rows WITHIN each group, without collapsing them
SELECT owner, name, score,
       ROW_NUMBER() OVER (PARTITION BY owner ORDER BY score DESC) AS rank_in_owner
FROM accounts
WHERE owner IS NOT NULL;

-- 5. The top account per rep (window + filter in a CTE)
WITH ranked AS (
    SELECT owner, name, score,
           ROW_NUMBER() OVER (PARTITION BY owner ORDER BY score DESC) AS rn
    FROM accounts
    WHERE owner IS NOT NULL
)
SELECT owner, name, score FROM ranked WHERE rn = 1;

-- 6. DEDUPE INSIDE THE DATABASE: keep one row per domain (the most recent)
WITH ranked AS (
    SELECT *, ROW_NUMBER() OVER (PARTITION BY LOWER(domain) ORDER BY created_at DESC) AS rn
    FROM accounts
)
SELECT id, name, domain, created_at FROM ranked WHERE rn = 1 ORDER BY LOWER(domain);

-- 7. RANK vs ROW_NUMBER: ties get the same rank
SELECT name, score,
       RANK() OVER (ORDER BY score DESC) AS rnk,
       ROW_NUMBER() OVER (ORDER BY score DESC) AS row_num
FROM accounts
LIMIT 6;

-- 8. Running total of won revenue by close date
SELECT name, closed_at, amount_eur,
       SUM(amount_eur) OVER (ORDER BY closed_at) AS running_won_eur
FROM deals
WHERE stage = 'closed_won';

-- 9. Share of each owner's pipeline (window over the whole result)
SELECT owner, SUM(amount_eur) AS open_eur,
       ROUND(100.0 * SUM(amount_eur) / SUM(SUM(amount_eur)) OVER (), 1) AS pct_of_total
FROM deals
WHERE stage NOT IN ('closed_won', 'closed_lost')
GROUP BY owner;
