# 1. How APIs work

## The restaurant analogy

An **API** (application programming interface) is how one program asks another for data or actions.
The API is the **menu** (what you're allowed to ask for) and the **waiter** (who carries your request
to the kitchen and brings the answer back). Your code never touches HubSpot's database directly; it
asks through HubSpot's API.

## A request has four parts

| Part | Letter analogy | Example |
| --- | --- | --- |
| **URL** (endpoint) | The address | `https://api.hubapi.com/crm/v3/objects/companies` |
| **Method** | What you want done | GET read · POST create · PATCH update · PUT replace · DELETE remove |
| **Headers** (incl. API key) | Your ID card and envelope labels | `Authorization: Bearer <key>`, `Content-Type: application/json` |
| **Body** (POST/PATCH) | What's inside the letter | `{"properties": {"name": "PeopleCo"}}` |

## URLs, piece by piece

```
https://api.example.com/crm/v3/objects/companies?limit=10&after=abc
└─┬──┘ └──────┬──────┘└───────────┬───────────┘└───────┬───────┘
scheme      host            path (endpoint)      query parameters
```

Query parameters (`?key=value&key2=value2`) filter or page results. In `requests` you pass them as a
dictionary: `params={"limit": 10, "after": "abc"}`.

## The response has two parts

1. A **status code**: how it went.
2. A **body**: the data, usually JSON (and headers such as `Retry-After`).

## Status codes you must know

| Code | Meaning | What your code should do |
| --- | --- | --- |
| **200** OK, **201** Created, **204** No content | Success | Carry on |
| **400** Bad request | Your request is wrong (missing field, bad JSON) | Log the response body; fix the request; **don't retry** |
| **401** Unauthorised | Missing or wrong key | Check the key; **don't retry** |
| **403** Forbidden | Key is valid but lacks permission (scope) | Add the scope; **don't retry** |
| **404** Not found | No such record or endpoint | Handle it (record deleted? enrichment has no data?) |
| **409** Conflict | Duplicate, e.g. a unique value already exists | Update instead of create |
| **429** Too many requests | You're rate-limited | **Wait and retry** (respect `Retry-After`) |
| **500, 502, 503, 504** | The server has a problem | **Wait and retry** a few times |

Rule of thumb: **2xx = fine. 4xx = your fault (don't retry, except 429). 5xx = their fault (retry).**

## Headers that matter

| Header | Direction | Meaning |
| --- | --- | --- |
| `Authorization: Bearer <token>` | Request | Who you are |
| `Content-Type: application/json` | Request/response | The body is JSON (`requests` sets it when you use `json=`) |
| `Retry-After: 2` | Response (with 429/503) | Wait this many seconds before retrying |
| `X-RateLimit-Remaining` (names vary) | Response | Requests left in the current window |

## Authentication

| Method | How it works | Example |
| --- | --- | --- |
| API key / bearer token | A secret string sent in a header | HubSpot service keys, Anthropic API key |
| OAuth 2.0 | The user clicks "Allow"; your app gets an access token (short-lived) and a refresh token | "Connect HubSpot" buttons in apps |
| Basic auth | Username and password, encoded, in a header | Older APIs |

Keys go in a `.env` file, never in code or Git. **Scopes** limit what a key can do (read companies,
write companies…). Give keys only the scopes they need (least privilege; important at a security
company).

## JSON bodies

```python
import requests

r = requests.post(
    "https://api.example.com/companies",
    json={"properties": {"name": "PeopleCo", "domain": "peopleco.de"}},  # dict -> JSON automatically
    headers={"Authorization": f"Bearer {TOKEN}"},
    timeout=10,                                                           # ALWAYS set a timeout
)
print(r.status_code)
data = r.json()          # JSON body -> dict
```

## REST vs others

- **REST:** resources at URLs, standard methods (what HubSpot, most APIs use).
- **GraphQL:** one endpoint; you send a query naming exactly the fields you want.
- **SDKs:** official libraries (`hubspot-api-client`, `anthropic`) wrap the same HTTP calls in Python
  functions. Knowing raw HTTP means you understand what the SDK is doing.

## How to read API documentation (a skill in itself)

For any endpoint, find:

1. **Method and URL.**
2. **Auth**: which header, which scopes.
3. **Parameters and body**: required vs optional, types, an example.
4. **Response**: an example body, and where the next-page cursor is.
5. **Limits**: rate limits, max batch size, max page size.
6. **Errors**: which codes and what they mean.

Then try one call by hand (browser, Postman or a 5-line script) before writing the pipeline.

## Check yourself

1. You get a 401. Should you retry? What do you check?
2. What's the difference between `params=` and `json=` in `requests`?
3. Why must every request have a `timeout`?

Next: [02-rate-limits-and-retries.md](02-rate-limits-and-retries.md)
