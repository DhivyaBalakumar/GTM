# 7. GTM metrics: how success is measured

## Funnel and pipeline metrics

| Metric | Formula / meaning | Why it matters |
| --- | --- | --- |
| Pipeline (value) | Sum of open deal values | Future revenue |
| Pipeline generated | Value of new opportunities created this period | The output of BDRs and your systems |
| Conversion rate (per stage) | Next stage / this stage, e.g. SQL → opportunity | Finds where the funnel leaks |
| Win rate | Won / (won + lost) | Sales effectiveness |
| Sales cycle | Days from opportunity created to won | Speed |
| Average deal size / ACV | Average yearly contract value | Revenue per win |
| Meetings booked | Per BDR per week | BDR output |
| Speed to lead | Minutes from inbound form to first rep contact | Inbound conversion |

## Efficiency metrics

| Metric | Meaning |
| --- | --- |
| CAC (customer acquisition cost) | Sales + marketing spend ÷ new customers |
| LTV (lifetime value) | Average revenue per customer × years they stay |
| LTV : CAC | Healthy is often quoted as ~3 : 1 or better |
| Payback period | Months for a customer's revenue to repay their CAC |

## Metrics for *your* systems (a GTM Engineer's own scorecard)

The job post's success definition: reps spend less time on manual work, and more pipeline comes from
systems that run reliably and are actually used. So measure:

| What | How |
| --- | --- |
| Hours saved per rep per week | Before/after time on research, data entry, list building |
| Adoption | % of reps using the alerts / briefs; clicks; replies to alerts |
| Pipeline from system-generated leads | Opportunities whose source is your scoring/signals |
| Speed to lead | Median minutes, before and after routing automation |
| Data quality | Duplicate rate, % of accounts with industry/size/owner filled |
| Reliability | Successful runs %, time to detect failures, incidents |

## Simple SQL for these (you'll learn SQL in [05-sql](../05-sql))

```sql
-- Meeting rate by lead source
SELECT source,
       COUNT(*) AS leads,
       SUM(meeting_booked) AS meetings,
       ROUND(100.0 * SUM(meeting_booked) / COUNT(*), 1) AS meeting_pct
FROM leads
GROUP BY source
ORDER BY meeting_pct DESC;
```

## Interview question: "Sales says leads are bad; marketing says sales is slow. Who's right?"

> "Probably both, partly. I'd get data before opinions: agree on a shared definition of a qualified
> lead, then look at conversion by source and by rep, and at speed to lead. If good-fit leads convert
> well when contacted quickly but sit for days, it's a routing and speed problem. If leads that are
> contacted quickly still don't convert, it's targeting or scoring. Then fix the system, not the
> blame: maybe tighter scoring plus instant routing and alerts."

Next: [08-the-compliance-market.md](08-the-compliance-market.md)
