# Module 7: CRM and HubSpot

The CRM is where all your work lands. "Make our CRM the single source of truth" is the first line of
the job's data responsibilities. You need two things: how **sales teams use** a CRM, and how to
**change it through its API** safely.

| # | File | Covers |
| --- | --- | --- |
| 1 | [01-crm-concepts.md](01-crm-concepts.md) | Objects, properties, associations, pipelines, lifecycle stages, owners, data model, buying committees, single source of truth |
| 2 | [02-hubspot-api.md](02-hubspot-api.md) | Service keys and scopes, the objects/search/batch/associations/properties APIs, unique properties, upserts, rate limits, webhooks via apps |
| 3 | [hubspot_client.py](hubspot_client.py) | A small, commented HubSpot client: create a unique property, batch upsert companies, search by domain, page through all companies, associate a contact. Runs in `--dry-run` without a key |

## Hands-on (with a free HubSpot account)

1. Create a free HubSpot account (or a developer test account).
2. Create a **service key**: Development → Keys → Service keys → Create. Add scopes
   `crm.objects.companies.read`, `crm.objects.companies.write`, `crm.schemas.companies.write`,
   `crm.objects.contacts.read`, `crm.objects.contacts.write`.
3. Put it in `.env` as `HUBSPOT_TOKEN=...`
4. Try it:

```powershell
python 07-crm-hubspot/hubspot_client.py --dry-run     # prints the exact requests, sends nothing
python 07-crm-hubspot/hubspot_client.py               # really does it (needs HUBSPOT_TOKEN)
```

5. Run it twice and check in HubSpot that you still have the same number of companies. That's
   idempotency, proven on a real CRM.

HubSpot changes its developer platform regularly. If something here doesn't match what you see,
trust the [current HubSpot developer docs](https://developers.hubspot.com/docs/api/overview), and
note what changed (it's a good thing to mention in an interview).
