-- Solutions to 05-sql/exercises.md
-- Run: python 05-sql/run_sql.py 05-sql/solutions.sql

-- Q1 Accounts in the Netherlands, highest score first
SELECT name, score FROM accounts WHERE country = 'NL' ORDER BY score DESC;

-- Q2 Accounts with no owner
SELECT COUNT(*) AS no_owner FROM accounts WHERE owner IS NULL;

-- Q3 Open deals over 20,000
SELECT name, stage, amount_eur FROM deals
WHERE amount_eur > 20000 AND stage NOT IN ('closed_won', 'closed_lost')
ORDER BY amount_eur DESC;

-- Q4 Accounts per industry
SELECT industry, COUNT(*) AS accounts FROM accounts GROUP BY industry ORDER BY accounts DESC, industry;

-- Q5 Accounts and average score per owner, unassigned included
SELECT COALESCE(owner, 'unassigned') AS owner, COUNT(*) AS accounts, ROUND(AVG(score), 1) AS avg_score
FROM accounts
GROUP BY COALESCE(owner, 'unassigned')
ORDER BY accounts DESC;

-- Q6 Duplicate domains
SELECT LOWER(domain) AS domain, COUNT(*) AS copies
FROM accounts GROUP BY LOWER(domain) HAVING COUNT(*) > 1;

-- Q7 Open pipeline per stage
SELECT stage, SUM(amount_eur) AS open_eur, COUNT(*) AS deals
FROM deals WHERE stage NOT IN ('closed_won', 'closed_lost')
GROUP BY stage ORDER BY open_eur DESC;

-- Q8 Contacts per account, including zero
SELECT a.name, COUNT(c.id) AS contacts
FROM accounts a LEFT JOIN contacts c ON c.account_id = a.id
GROUP BY a.id, a.name
ORDER BY contacts, a.name;

-- Q9 Score 70+ with no open deal
SELECT a.name, a.score, a.owner
FROM accounts a
WHERE a.score >= 70
  AND NOT EXISTS (
      SELECT 1 FROM deals d
      WHERE d.account_id = a.id AND d.stage NOT IN ('closed_won', 'closed_lost')
  )
ORDER BY a.score DESC;

-- Q10 Contacts who replied
SELECT c.name, c.title, a.name AS account, a.owner, a.score
FROM contacts c JOIN accounts a ON a.id = c.account_id
WHERE c.replied = 1
ORDER BY a.score DESC;

-- Q11 Meeting rate per source
SELECT source, COUNT(*) AS leads, SUM(meeting_booked) AS meetings,
       ROUND(100.0 * SUM(meeting_booked) / COUNT(*), 1) AS meeting_pct
FROM leads GROUP BY source ORDER BY meeting_pct DESC;

-- Q12 Segment labels and counts
SELECT CASE WHEN employees >= 500 THEN 'Enterprise'
            WHEN employees >= 20 THEN 'Mid-market'
            ELSE 'Small' END AS segment,
       COUNT(*) AS accounts
FROM accounts GROUP BY segment ORDER BY accounts DESC;

-- Q13 Not contacted within an hour (or never)
SELECT email, source,
       ROUND((JULIANDAY(first_contacted_at) - JULIANDAY(created_at)) * 24 * 60) AS minutes_to_contact
FROM leads
WHERE first_contacted_at IS NULL
   OR (JULIANDAY(first_contacted_at) - JULIANDAY(created_at)) * 24 * 60 > 60
ORDER BY minutes_to_contact DESC;

-- Q14 Highest-value deal per owner
WITH ranked AS (
    SELECT owner, name, amount_eur,
           ROW_NUMBER() OVER (PARTITION BY owner ORDER BY amount_eur DESC) AS rn
    FROM deals
)
SELECT owner, name, amount_eur FROM ranked WHERE rn = 1 ORDER BY amount_eur DESC;

-- Q15 Win rate per owner (NULL when nothing closed)
SELECT owner,
       SUM(CASE WHEN stage = 'closed_won' THEN 1 ELSE 0 END) AS won,
       SUM(CASE WHEN stage = 'closed_lost' THEN 1 ELSE 0 END) AS lost,
       ROUND(100.0 * SUM(CASE WHEN stage = 'closed_won' THEN 1 ELSE 0 END)
             / NULLIF(SUM(CASE WHEN stage IN ('closed_won', 'closed_lost') THEN 1 ELSE 0 END), 0), 1)
         AS win_rate_pct
FROM deals
GROUP BY owner;
