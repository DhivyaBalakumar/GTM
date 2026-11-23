-- SQL lesson 2: aggregates, GROUP BY, HAVING
-- Run: python 05-sql/run_sql.py 05-sql/lessons/02_aggregate_group.sql

-- 1. Aggregates summarise many rows into one
SELECT COUNT(*) AS accounts, AVG(score) AS avg_score, MIN(score) AS lowest, MAX(score) AS highest
FROM accounts;

-- 2. COUNT(*) counts rows; COUNT(column) skips NULLs
SELECT COUNT(*) AS all_rows, COUNT(owner) AS with_owner FROM accounts;

-- 3. SUM: total pipeline value
SELECT SUM(amount_eur) AS total_eur FROM deals WHERE stage NOT IN ('closed_won', 'closed_lost');

-- 4. GROUP BY: one result row per group
SELECT country, COUNT(*) AS accounts FROM accounts GROUP BY country ORDER BY accounts DESC;

-- 5. Several aggregates per group, rounded
SELECT owner, COUNT(*) AS accounts, ROUND(AVG(score), 1) AS avg_score
FROM accounts
GROUP BY owner
ORDER BY accounts DESC;

-- 6. Group by two columns
SELECT owner, stage, COUNT(*) AS deals
FROM deals
GROUP BY owner, stage
ORDER BY owner, stage;

-- 7. HAVING filters GROUPS (WHERE filters rows before grouping)
SELECT country, COUNT(*) AS accounts
FROM accounts
GROUP BY country
HAVING COUNT(*) >= 2;

-- 8. WHERE and HAVING together: tier-A accounts (score >= 75) per owner, only owners with 2+
SELECT owner, COUNT(*) AS tier_a
FROM accounts
WHERE score >= 75
GROUP BY owner
HAVING COUNT(*) >= 2;

-- 9. FIND DUPLICATES (a classic): the same domain more than once, ignoring case
SELECT LOWER(domain) AS domain, COUNT(*) AS copies, GROUP_CONCAT(name, ' | ') AS names
FROM accounts
GROUP BY LOWER(domain)
HAVING COUNT(*) > 1;

-- 10. COUNT(DISTINCT ...)
SELECT COUNT(DISTINCT country) AS countries, COUNT(DISTINCT owner) AS owners FROM accounts;

-- 11. Won revenue per owner
SELECT owner, SUM(amount_eur) AS won_eur, COUNT(*) AS wins
FROM deals
WHERE stage = 'closed_won'
GROUP BY owner;

-- 12. Leads per source
SELECT source, COUNT(*) AS leads, SUM(meeting_booked) AS meetings
FROM leads
GROUP BY source
ORDER BY leads DESC;
