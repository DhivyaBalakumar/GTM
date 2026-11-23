-- SQL lesson 3: JOINs
-- Run: python 05-sql/run_sql.py 05-sql/lessons/03_joins.sql
-- A JOIN combines rows from two tables where a key matches.
-- contacts.account_id points to accounts.id (a FOREIGN KEY -> PRIMARY KEY relationship).

-- 1. INNER JOIN: only rows that match in BOTH tables. Short aliases (a, c) keep it readable.
SELECT a.name AS account, c.name AS contact, c.title
FROM accounts a
JOIN contacts c ON c.account_id = a.id
ORDER BY a.name;

-- 2. LEFT JOIN: every account, with contacts if any (NULL where there are none)
SELECT a.name AS account, c.name AS contact
FROM accounts a
LEFT JOIN contacts c ON c.account_id = a.id
ORDER BY a.name;

-- 3. LEFT JOIN + IS NULL = "rows with NO match": accounts with no contacts yet (enrich these!)
SELECT a.name, a.owner
FROM accounts a
LEFT JOIN contacts c ON c.account_id = a.id
WHERE c.id IS NULL;

-- 4. Count per account after joining
SELECT a.name, COUNT(c.id) AS contacts
FROM accounts a
LEFT JOIN contacts c ON c.account_id = a.id
GROUP BY a.id, a.name
ORDER BY contacts DESC, a.name;

-- 5. Accounts with open deals and their value
SELECT a.name, d.name AS deal, d.stage, d.amount_eur
FROM deals d
JOIN accounts a ON a.id = d.account_id
WHERE d.stage NOT IN ('closed_won', 'closed_lost')
ORDER BY d.amount_eur DESC;

-- 6. Reported-style question: contacts who opened a sequence but didn't reply,
--    at companies with over 100 employees
SELECT c.name, c.title, a.name AS account, a.employees
FROM contacts c
JOIN accounts a ON a.id = c.account_id
WHERE c.opened_sequence = 1 AND c.replied = 0 AND a.employees > 100;

-- 7. Three tables: deal -> account -> champion contact
SELECT d.name AS deal, a.name AS account, c.name AS champion
FROM deals d
JOIN accounts a ON a.id = d.account_id
LEFT JOIN contacts c ON c.account_id = a.id AND c.role = 'champion'
WHERE d.stage NOT IN ('closed_won', 'closed_lost');

-- 8. Tier-A accounts with NO economic buyer contact (a buying-committee gap)
SELECT a.name, a.score
FROM accounts a
WHERE a.score >= 75
  AND NOT EXISTS (
      SELECT 1 FROM contacts c WHERE c.account_id = a.id AND c.role = 'economic_buyer'
  );

-- 9. Joining on something other than an id: match inbound lead emails to accounts by domain
SELECT l.email, l.source, a.name AS account, a.owner
FROM leads l
LEFT JOIN accounts a ON LOWER(a.domain) = SUBSTR(l.email, INSTR(l.email, '@') + 1)
ORDER BY l.id;
