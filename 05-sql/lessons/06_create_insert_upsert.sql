-- SQL lesson 6: creating tables, changing data, and UPSERT
-- Run: python 05-sql/run_sql.py 05-sql/lessons/06_create_insert_upsert.sql
-- (Safe to re-run: it drops and recreates its own practice table.)

-- 1. Start fresh
DROP TABLE IF EXISTS companies_practice;

-- 2. CREATE TABLE with types, a primary key and a UNIQUE constraint on domain
CREATE TABLE companies_practice (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    domain TEXT NOT NULL UNIQUE,
    name TEXT,
    employees INTEGER,
    score INTEGER DEFAULT 0,
    updated_at TEXT
);

-- 3. INSERT rows
INSERT INTO companies_practice (domain, name, employees, score, updated_at)
VALUES ('peopleco.de', 'PeopleCo GmbH', 120, 95, '2026-11-20'),
       ('opal.de', 'Opal Analytics', 25, 72, '2026-11-20');

-- 4. Look
SELECT * FROM companies_practice;

-- 5. Inserting the same domain again FAILS because of UNIQUE (this is what protects you from duplicates)
INSERT INTO companies_practice (domain, name) VALUES ('peopleco.de', 'Peopleco duplicate');

-- 6. UPDATE: change existing rows (ALWAYS with a WHERE, or you change every row!)
UPDATE companies_practice SET score = 99, updated_at = '2026-11-23' WHERE domain = 'peopleco.de';

-- 7. UPSERT: insert, or update if the unique key already exists
INSERT INTO companies_practice (domain, name, employees, score, updated_at)
VALUES ('peopleco.de', 'PeopleCo GmbH', 125, 97, '2026-11-24'),
       ('kitelabs.io', 'Kite Labs', 8, 35, '2026-11-24')
ON CONFLICT(domain) DO UPDATE SET
    employees = excluded.employees,
    score = excluded.score,
    updated_at = excluded.updated_at;

-- 8. Result: peopleco updated (not duplicated), kitelabs created
SELECT * FROM companies_practice ORDER BY domain;

-- 9. Run the upsert again: still 3 rows. That's IDEMPOTENCY: running twice = running once.
INSERT INTO companies_practice (domain, name, employees, score, updated_at)
VALUES ('peopleco.de', 'PeopleCo GmbH', 125, 97, '2026-11-24'),
       ('kitelabs.io', 'Kite Labs', 8, 35, '2026-11-24')
ON CONFLICT(domain) DO UPDATE SET
    employees = excluded.employees, score = excluded.score, updated_at = excluded.updated_at;

SELECT COUNT(*) AS rows_after_second_run FROM companies_practice;

-- 10. "Never overwrite with blanks": keep the old value when the new one is NULL
INSERT INTO companies_practice (domain, name, employees)
VALUES ('opal.de', NULL, NULL)
ON CONFLICT(domain) DO UPDATE SET
    name = COALESCE(excluded.name, companies_practice.name),
    employees = COALESCE(excluded.employees, companies_practice.employees);

SELECT domain, name, employees FROM companies_practice WHERE domain = 'opal.de';

-- 11. DELETE (also ALWAYS with a WHERE)
DELETE FROM companies_practice WHERE domain = 'kitelabs.io';
SELECT domain FROM companies_practice;

-- 12. Clean up
DROP TABLE companies_practice;
