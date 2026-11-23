-- SQL lesson 4: CASE WHEN, NULL handling, text, dates, rates
-- Run: python 05-sql/run_sql.py 05-sql/lessons/04_case_nulls_dates.sql

-- 1. CASE WHEN: if/else inside a query (scoring and labelling)
SELECT name, employees,
       CASE
           WHEN employees >= 500 THEN 'Enterprise'
           WHEN employees >= 20  THEN 'Mid-market'
           ELSE 'Small'
       END AS segment
FROM accounts;

-- 2. A rule-based fit score in SQL
SELECT name,
       (CASE WHEN industry IN ('Software', 'Fintech', 'Healthtech') THEN 25 ELSE 0 END)
     + (CASE WHEN employees BETWEEN 20 AND 500 THEN 20 ELSE 0 END)
     + (CASE WHEN country IN ('DE', 'AT', 'CH', 'NL', 'BE', 'LU') THEN 15 ELSE 0 END) AS fit
FROM accounts
ORDER BY fit DESC;

-- 3. COALESCE: first non-NULL value (a default for missing data)
SELECT name, COALESCE(owner, 'unassigned') AS owner FROM accounts;

-- 4. Counting with CASE: conditional counts in one query
SELECT owner,
       SUM(CASE WHEN stage = 'closed_won' THEN 1 ELSE 0 END) AS won,
       SUM(CASE WHEN stage = 'closed_lost' THEN 1 ELSE 0 END) AS lost
FROM deals
GROUP BY owner;

-- 5. Rates: multiply by 100.0 (a decimal!) or integer division gives 0
SELECT source,
       COUNT(*) AS leads,
       SUM(meeting_booked) AS meetings,
       ROUND(100.0 * SUM(meeting_booked) / COUNT(*), 1) AS meeting_pct
FROM leads
GROUP BY source
ORDER BY meeting_pct DESC;

-- 6. Win rate per owner (won / (won + lost)); NULLIF avoids dividing by zero
SELECT owner,
       ROUND(100.0 * SUM(stage = 'closed_won')
             / NULLIF(SUM(stage IN ('closed_won', 'closed_lost')), 0), 1) AS win_rate_pct
FROM deals
GROUP BY owner;

-- 7. Text functions: LOWER, UPPER, TRIM, LENGTH, SUBSTR, INSTR, REPLACE, || (concatenate)
SELECT email,
       SUBSTR(email, INSTR(email, '@') + 1) AS domain,
       UPPER(country) || '-' || source AS label
FROM leads
LIMIT 5;

-- 8. Personal-email leads
SELECT email FROM leads
WHERE SUBSTR(email, INSTR(email, '@') + 1) IN ('gmail.com', 'yahoo.com', 'outlook.com');

-- 9. Dates (SQLite stores them as text 'YYYY-MM-DD HH:MM'): leads per month
SELECT SUBSTR(created_at, 1, 7) AS month, COUNT(*) AS leads
FROM leads
GROUP BY month
ORDER BY month;
-- Postgres/BigQuery equivalent: DATE_TRUNC('month', created_at)

-- 10. Speed to lead in minutes (JULIANDAY gives days as a decimal)
SELECT email, source,
       ROUND((JULIANDAY(first_contacted_at) - JULIANDAY(created_at)) * 24 * 60) AS minutes_to_contact
FROM leads
WHERE first_contacted_at IS NOT NULL
ORDER BY minutes_to_contact DESC;

-- 11. Inbound leads nobody contacted within 24 hours (or at all)
SELECT email, source, created_at, first_contacted_at
FROM leads
WHERE first_contacted_at IS NULL
   OR JULIANDAY(first_contacted_at) - JULIANDAY(created_at) > 1;

-- 12. Days to close for won deals
SELECT name, JULIANDAY(closed_at) - JULIANDAY(created_at) AS days_to_close
FROM deals
WHERE stage = 'closed_won';
