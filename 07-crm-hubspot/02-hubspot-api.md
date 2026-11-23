# 2. The HubSpot API

> Accurate as of late 2026 to the best of our research. HubSpot evolves its developer platform, so
> check [developers.hubspot.com](https://developers.hubspot.com/docs/api/overview) for the current
> details before you build.

## Authentication (changed in October 2026)

- HubSpot no longer lets you create the **legacy private apps** most older tutorials describe.
- For API calls into your own account, create a **service key** (Development → Keys → Service keys),
  choose **scopes**, and send it as `Authorization: Bearer <key>`.
- **Webhooks** can't be received with a service key. You build a small **app** with HubSpot's
  command-line tool (`hs project create`, choosing static auth and webhooks), install it in the
  account, and configure subscriptions and the target URL.
- Apps used by many customers (marketplace apps) use **OAuth**.

Scopes you'll typically need: `crm.objects.companies.read/write`, `crm.objects.contacts.read/write`,
`crm.objects.deals.read/write`, `crm.schemas.companies.write` (to create properties).

## The base URL and the objects API

Base: `https://api.hubapi.com`

| Action | Method and path |
| --- | --- |
| List companies (paginated) | `GET /crm/v3/objects/companies?limit=100&properties=name,domain&after=<cursor>` |
| Get one | `GET /crm/v3/objects/companies/{id}` |
| Create one | `POST /crm/v3/objects/companies` body `{"properties": {...}}` |
| Update one | `PATCH /crm/v3/objects/companies/{id}` body `{"properties": {...}}` |
| Delete (archive) | `DELETE /crm/v3/objects/companies/{id}` |

Replace `companies` with `contacts` or `deals` for other objects. List responses look like:

```json
{"results": [{"id": "1001", "properties": {"name": "PeopleCo GmbH", "domain": "peopleco.de"}}],
 "paging": {"next": {"after": "1001"}}}
```

Note: you must ask for the properties you want with `properties=`; otherwise you get only a few
defaults. Numbers often come back as **strings** (`"numberofemployees": "120"`), so convert them.

## Search

`POST /crm/v3/objects/companies/search`

```json
{"filterGroups": [{"filters": [{"propertyName": "domain", "operator": "EQ", "value": "peopleco.de"}]}],
 "properties": ["name", "domain", "hubspot_owner_id"], "limit": 10}
```

Good for "find records where…". Two cautions: search has its own, stricter rate limit, and the search
index can lag a few seconds behind writes, so "search, then create if not found" can still make
duplicates if two runs happen close together.

## Batch endpoints (always prefer these for pipelines)

| Action | Path |
| --- | --- |
| Batch read | `POST /crm/v3/objects/companies/batch/read` |
| Batch create | `POST /crm/v3/objects/companies/batch/create` |
| Batch update | `POST /crm/v3/objects/companies/batch/update` |
| **Batch upsert** | `POST /crm/v3/objects/companies/batch/upsert` |

Batch calls accept up to 100 records each.

### Batch upsert by a unique property

1. Create a property with **unique values** (e.g. `company_domain_key`, or an external ID). (You can
   create it in the UI, or with the properties API using `"hasUniqueValue": true`.)
2. Send:

```json
{"inputs": [
  {"idProperty": "company_domain_key", "id": "peopleco.de",
   "properties": {"name": "PeopleCo GmbH", "fit_score": "95", "score_reasons": "software; 120 staff; DE"}}
]}
```

HubSpot updates the record with that value if it exists and creates it if it doesn't. Run it twice:
no duplicates. That's the core of an idempotent CRM sync.

## Associations

Link a contact to a company with the v4 associations API, e.g. the default association:

`PUT /crm/v4/objects/contacts/{contactId}/associations/default/companies/{companyId}`

Labelled associations (e.g. "Champion") use association type IDs; batch versions exist too.

## Properties API

`POST /crm/v3/properties/companies`

```json
{"name": "fit_score", "label": "Fit score", "type": "number", "fieldType": "number", "groupName": "companyinformation"}
```

## Rate limits

Limits depend on the plan and app type. Ballpark: around 100–190 requests per 10 seconds for private
or service-key access, with a daily cap, and the search API at about 5 requests per second. On 429,
back off and retry (respect `Retry-After`). Batch endpoints are how you stay well under the limit.

## The safe-write checklist for HubSpot

- [ ] Batch upsert by a unique property (never blind creates).
- [ ] Batches of ≤ 100.
- [ ] Every call through a retry function (429/5xx).
- [ ] Never send empty values; send only fields you own.
- [ ] Don't change `hubspot_owner_id` on records that already have an owner.
- [ ] Log created vs updated counts; alert if creates spike on a re-run.
- [ ] A `--dry-run` that prints what would be sent.

## Interview phrasing

> "I'd mark domain as a unique property and write with the batch upsert endpoint in batches of 100,
> through a retry function that handles 429s. The pipeline only writes the fields it owns, like the
> score and reasons, never empty values and never the owner of an existing record. Running it twice
> gives the same result."

Code: [hubspot_client.py](hubspot_client.py)
