-- SQL lesson 1: SELECT, WHERE, ORDER BY, LIMIT
-- Run: python 05-sql/run_sql.py 05-sql/lessons/01_select_where.sql
-- Keywords are not case-sensitive (select = SELECT); writing them in CAPITALS is a convention.
-- Every statement ends with a semicolon.

-- 1. Everything from a table (fine for exploring; name columns in real queries)
SELECT * FROM accounts LIMIT 5;

-- 2. Pick columns, and rename one with AS
SELECT name, country, score AS fit_score FROM accounts LIMIT 5;

-- 3. WHERE filters rows (text values go in single quotes)
SELECT name, country FROM accounts WHERE country = 'DE';

-- 4. Comparisons: =  !=  <>  >  <  >=  <=
SELECT name, score FROM accounts WHERE score >= 75;

-- 5. AND / OR, with brackets to make the logic clear
SELECT name, country, score
FROM accounts
WHERE (country = 'DE' OR country = 'AT') AND score >= 70;

-- 6. IN: match a list (cleaner than many ORs)
SELECT name, country FROM accounts WHERE country IN ('NL', 'BE', 'LU');

-- 7. BETWEEN is inclusive at both ends: 20 and 500 are included
SELECT name, employees FROM accounts WHERE employees BETWEEN 20 AND 500 ORDER BY employees;

-- 8. LIKE: patterns. % = any characters, _ = exactly one character
SELECT name, title FROM contacts WHERE title LIKE '%CTO%' OR title LIKE 'Head of%';

-- 9. IS NULL / IS NOT NULL (never "= NULL")
SELECT name, owner FROM accounts WHERE owner IS NULL;

-- 10. ORDER BY: sort (ASC is the default; DESC = biggest first), then LIMIT: top N
SELECT name, score FROM accounts ORDER BY score DESC LIMIT 5;

-- 11. Sort by two columns
SELECT country, name, score FROM accounts ORDER BY country ASC, score DESC;

-- 12. DISTINCT: unique values
SELECT DISTINCT country FROM accounts ORDER BY country;

-- 13. Calculations in SELECT
SELECT name, amount_eur, amount_eur * 1.08 AS amount_usd_approx FROM deals LIMIT 5;

-- 14. Reported interview question: "select rows where a value is higher than X"
SELECT name, amount_eur FROM deals WHERE amount_eur > 15000 ORDER BY amount_eur DESC;

-- 15. NOT
SELECT name, stage FROM deals WHERE stage NOT IN ('closed_won', 'closed_lost');
