# Tool stack cheat sheet: every tool, which step, click or code

✔ = main use. "API" = has a public API you'd call from Python. Pricing and limits change; check the
vendor before quoting a number.

| Tool | Collect | Clean | Dedupe | Enrich | Verify | Score/Segment | Route | CRM | Outreach | Signals | Orchestrate | Report | How people use it |
| --- | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | --- |
| **Apollo.io** | ✔ |  |  | ✔ |  | (filters) |  |  | ✔ | (intent) |  |  | UI + API (search free of credits, enrichment 10/call) |
| **ZoomInfo** | ✔ |  | (Ops) | ✔ |  |  |  |  | (Engage) | ✔ |  |  | UI + API |
| **Cognism** | ✔ |  |  | ✔ |  |  |  |  |  |  |  |  | UI + API; strong EU, phone-verified |
| **Lusha** | ✔ |  |  | ✔ |  |  |  |  |  |  |  |  | Chrome extension + API |
| **Dealfront / Leadfeeder** | ✔ |  |  | ✔ |  |  |  |  |  | ✔ (visits) |  |  | UI + API; EU |
| **LinkedIn Sales Navigator** | ✔ |  |  |  |  |  |  |  | (InMail) | ✔ (job changes) |  |  | UI only (no data API) |
| **PhantomBuster / Apify** | ✔ |  |  |  |  |  |  |  |  |  |  |  | Scrapers: UI + API |
| **Outscraper / SerpAPI** | ✔ (Maps) |  |  |  |  |  |  |  |  |  |  |  | API |
| **Crunchbase / Dealroom** | ✔ |  |  | ✔ |  |  |  |  |  | ✔ (funding) |  |  | UI + API |
| **Vibe Prospecting (Explorium)** | ✔ |  |  | ✔ |  |  |  |  |  | ✔ (events) |  |  | Chat UI + API/MCP |
| **Clay** | ✔ | ✔ | ✔ | ✔ | ✔ | ✔ |  | ✔ (push) |  | ✔ |  ✔ (auto-run) |  | Tables (click) + webhooks + HTTP API columns |
| **Hunter.io** |  |  |  | ✔ (email) | ✔ |  |  |  |  |  |  |  | UI + API, free tier |
| **Dropcontact / Prospeo / FindyMail** |  |  |  | ✔ (email) | ✔ |  |  |  |  |  |  |  | UI + API |
| **BuiltWith / Wappalyzer** |  |  |  | ✔ (tech) |  | ✔ |  |  |  | ✔ (tech change) |  |  | UI + API |
| **PeopleDataLabs** |  |  |  | ✔ |  |  |  |  |  |  |  |  | API |
| **ZeroBounce / NeverBounce / MillionVerifier / Bouncer** |  |  |  |  | ✔ |  |  |  |  |  |  |  | CSV upload or API |
| **Claude (API / Claude Code)** |  | ✔ (titles) |  | ✔ (research) |  | ✔ (classify) |  |  | ✔ (drafts) | ✔ (read news/jobs) |  |  | Code; structured output + validation |
| **Python + pandas** | ✔ | ✔ | ✔ | ✔ |  | ✔ | ✔ | ✔ |  | ✔ | ✔ | ✔ | Code |
| **rapidfuzz / Splink / recordlinkage** |  |  | ✔ |  |  |  |  |  |  |  |  |  | Code |
| **OpenRefine** |  | ✔ | ✔ |  |  |  |  |  |  |  |  |  | Desktop UI |
| **Insycle / Dedupely / DemandTools** |  | ✔ | ✔ |  |  |  |  | ✔ |  |  |  |  | UI on top of the CRM |
| **HubSpot** | ✔ (forms) |  | ✔ (merge) | (Breeze) |  | ✔ (scoring) | ✔ (rotation) | ✔ | ✔ (sequences) | ✔ (visits) | ✔ (workflows) | ✔ | UI + API (service keys, batch 100) |
| **Salesforce** | ✔ |  | ✔ (rules) |  |  | ✔ | ✔ | ✔ | (Sales Engagement) |  | ✔ (Flow) | ✔ | UI + API (external-ID upsert, Bulk API) |
| **LeanData** |  |  | ✔ (L2A) |  |  |  | ✔ |  |  |  |  |  | Config UI (Salesforce) |
| **Chili Piper / Default** |  |  |  |  |  |  | ✔ |  |  |  |  |  | Config + webhooks |
| **Outreach / Salesloft** |  |  |  |  |  |  |  |  | ✔ |  |  | ✔ | UI + API |
| **lemlist / Instantly / Smartlead** |  |  |  |  |  |  |  |  | ✔ |  |  | ✔ | UI + API + reply webhooks |
| **HeyReach / Expandi** |  |  |  |  |  |  |  |  | ✔ (LinkedIn) |  |  |  | UI |
| **RB2B / Common Room / UserGems** |  |  |  |  |  |  |  |  |  | ✔ |  |  | UI + webhooks |
| **Bombora / G2 Buyer Intent** |  |  |  |  |  |  |  |  |  | ✔ |  |  | UI + CRM sync |
| **n8n / Zapier / Make** | ✔ |  |  |  |  |  |  | ✔ |  | ✔ | ✔ |  | Visual workflows + code nodes |
| **GitHub Actions / cron** |  |  |  |  |  |  |  |  |  |  | ✔ |  | YAML / crontab |
| **Prefect / Dagster / Airflow** |  |  |  |  |  |  |  |  |  |  | ✔ |  | Code |
| **Slack** |  |  |  |  |  |  | (alerts) |  |  | ✔ | ✔ (alerts) |  | Webhooks / apps |
| **BigQuery / Snowflake / Postgres / DuckDB** |  | ✔ | ✔ |  |  | ✔ |  |  |  |  |  | ✔ | SQL |
| **Fivetran / Airbyte** | ✔ (ELT) |  |  |  |  |  |  |  |  |  |  |  | Config |
| **dbt** |  | ✔ | ✔ |  |  | ✔ |  |  |  |  |  | ✔ | SQL + YAML tests |
| **Hightouch / Census** |  |  |  |  |  |  |  | ✔ (reverse ETL) |  |  |  |  | Config + SQL |
| **Looker Studio / Metabase / Power BI / Tableau** |  |  |  |  |  |  |  |  |  |  |  | ✔ | UI |

## Python libraries by step

| Step | Libraries |
| --- | --- |
| Calls | `requests`, `httpx` (async), `tenacity` / `urllib3.Retry` (retries), `python-dotenv` (secrets) |
| Webhooks | `flask` / `fastapi`, `hmac` + `hashlib` (signatures) |
| Clean + validate | `pandas`, `re`, `phonenumbers`, `email-validator`, `pycountry`, `pydantic` / `pandera` |
| Dedupe | `rapidfuzz`, `difflib`, `recordlinkage`, `splink`, `dedupe` |
| AI | `anthropic` |
| Score | plain Python + config, `scikit-learn` later |
| Storage | `sqlite3`, `duckdb`, `sqlalchemy`, `psycopg` |
| Orchestration | `prefect`, `dagster`, `apscheduler` |
| Tests | `pytest`, `responses` / `respx` (fake HTTP) |
| Stats | `statsmodels`, `scipy` |

## Concepts glossary (one line each)

| Term | One line |
| --- | --- |
| ICP | Description of the companies most likely to buy and succeed |
| Persona / buying committee | The roles inside the account who decide, champion, evaluate, block |
| Search vs enrichment | Finding who matches vs buying their contact details |
| Waterfall | Try provider A, then B, then C until a value is found; pay per hit |
| Pagination (page / offset / cursor / keyset) | Ways to fetch a large result in chunks |
| Rate limit / 429 / Retry-After | Max calls per window; "slow down"; how long to wait |
| Exponential backoff + jitter | Wait 1, 2, 4, 8 s (+ randomness) between retries |
| Batching | Many records per API call |
| Idempotent | Running twice gives the same result |
| Upsert | Update if the key exists, otherwise create |
| Unique property / external ID | The CRM field used as the upsert key |
| Normalisation | Writing the same thing the same way |
| Match key | A normalised value used only for comparing |
| Blocking | Only comparing records that share a cheap key |
| Survivorship / golden record | Field-by-field rules for the merged best record |
| Lineage | Which source each value came from |
| Field ownership | Which system or person may write each field |
| Quarantine | Holding area for rows that failed validation |
| Suppression | People/accounts that must not be contacted |
| Fit vs intent | Looks like a customer vs ready now |
| Signal decay | Older signals count less |
| Tier | A/B/C/D bucket from the score |
| Segment | Group that gets the same message |
| Round robin | Assign in turn within a team |
| Speed-to-lead / SLA | Max time before an inbound lead is contacted |
| Deliverability | Whether email lands in the inbox (SPF, DKIM, DMARC, warm-up, volume) |
| Reverse ETL | Warehouse → CRM sync |
| Heartbeat / dead man's switch | Alert when a job *didn't* run |
