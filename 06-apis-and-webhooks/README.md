# Module 6: APIs and webhooks

Every connection in a GTM system is an API: pulling companies from a data provider, enrichment,
writing to the CRM, posting to Slack, asking Claude. This module is what the live-coding round leans
on most after Python.

## Theory (read in order)

| # | File | Covers |
| --- | --- | --- |
| 1 | [01-how-apis-work.md](01-how-apis-work.md) | Requests and responses, URLs, methods, status codes, headers, JSON bodies, auth, reading API docs |
| 2 | [02-rate-limits-and-retries.md](02-rate-limits-and-retries.md) | Rate limits, 429, Retry-After, exponential backoff, jitter, what to retry and what not, timeouts |
| 3 | [03-pagination-batching-idempotency.md](03-pagination-batching-idempotency.md) | Cursor/offset pagination, batching, upserts, idempotency keys |
| 4 | [04-webhooks.md](04-webhooks.md) | Webhooks vs polling, receivers, fast 200s, duplicate events, signatures, retries, ngrok |

## Hands-on code

All lessons run against a **practice API on your own laptop** ([practice_server.py](practice_server.py))
that behaves like a real one: it needs an API key, rate-limits you, randomly fails, paginates and
limits batch sizes. No accounts or keys needed.

```powershell
# Terminal 1: start the practice API (leave it running)
python 06-apis-and-webhooks/practice_server.py

# Terminal 2: run the lessons
python 06-apis-and-webhooks/lessons/01_requests_basics.py
python 06-apis-and-webhooks/lessons/02_retry_backoff.py
python 06-apis-and-webhooks/lessons/03_pagination_and_batching.py
```

Webhooks:

```powershell
# Terminal 1: your webhook receiver
python 06-apis-and-webhooks/lessons/04_webhook_receiver.py
# Terminal 2: send it events (including a duplicate)
python 06-apis-and-webhooks/lessons/05_send_test_events.py
```

| # | File | You'll learn |
| --- | --- | --- |
| 1 | [lessons/01_requests_basics.py](lessons/01_requests_basics.py) | GET/POST with requests, params, headers, JSON, status codes, 401/404, timeouts |
| 2 | [lessons/02_retry_backoff.py](lessons/02_retry_backoff.py) | Watching 429s and 503s happen, then a proper retry function |
| 3 | [lessons/03_pagination_and_batching.py](lessons/03_pagination_and_batching.py) | Fetching every page, batch upserts, proving idempotency |
| 4 | [lessons/04_webhook_receiver.py](lessons/04_webhook_receiver.py) | A Flask receiver that dedupes events and replies fast |
| 5 | [lessons/05_send_test_events.py](lessons/05_send_test_events.py) | Sending test webhook events, with and without a valid signature |

## Exercise

[exercises/ex01_api_client.py](exercises/ex01_api_client.py): write `request_with_retry`,
`get_all_companies` and `upsert_in_batches` yourself, then run the file with the practice server on.
Solution: [solutions/ex01_api_client.py](solutions/ex01_api_client.py).

## Practise against real public APIs too

- `https://api.github.com/users/octocat` (open it in your browser: that's a GET request)
- `https://httpbin.org/status/429` and `/status/503` (returns whatever status you ask for)
- `https://httpbin.org/anything` (echoes back what you sent)
