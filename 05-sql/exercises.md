# SQL exercises (15 GTM questions)

Write your answers in a file such as `output/my_answers.sql` (one query per question, each ending with
`;`), then run `python 05-sql/run_sql.py output/my_answers.sql`. Compare with
[solutions.sql](solutions.sql) only after trying.

Tables: `accounts`, `contacts`, `deals`, `leads` (see the [README](README.md)).

## Warm-up

1. List the names and scores of all accounts in the Netherlands, highest score first.
2. How many accounts have no owner?
3. List deals worth more than €20,000 that are still open (not won or lost).

## Grouping

4. Count accounts per industry, most common first.
5. For each owner: number of accounts and average score (1 decimal). Include unassigned accounts as
   `'unassigned'`.
6. Which domains appear more than once in `accounts` (ignore upper/lower case)?
7. Total open pipeline (€) per deal stage.

## Joins

8. For every account, show how many contacts it has (including zero), fewest first.
9. Accounts with a score of 70+ that have **no open deal**. (These need outreach.)
10. Contacts who replied, with their account name, owner and the account's score.

## CASE, rates and dates

11. Meeting rate (%) per lead source, best first.
12. Label each account Enterprise (500+), Mid-market (20–499) or Small, and count per label.
13. Inbound leads not contacted within 1 hour of arriving (or never contacted). Show email, source and
    minutes to contact.

## Windows and CTEs

14. The highest-value deal for each owner (one row per owner).
15. Win rate per owner, where win rate = won / (won + lost), as a percentage. Owners with no closed
    deals should show NULL, not an error.
