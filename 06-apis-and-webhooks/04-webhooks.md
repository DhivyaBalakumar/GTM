# 4. Webhooks

## The idea: a doorbell instead of checking the door

Normally your code keeps asking an API "anything new?" every few minutes. That's **polling**: wasteful
and slow. A **webhook** flips it: the other system **calls your code** (sends an HTTP POST to your URL)
the moment something happens.

| | Polling | Webhook |
| --- | --- | --- |
| Who starts | You, on a schedule | The other system, on an event |
| Speed | Up to one interval late | Seconds |
| Cost | Many empty requests | Only real events |
| Use for | Bulk syncs, sources without webhooks | Inbound leads, stage changes, form fills |

**Why it matters at Secfix:** "inbound routing" and "alerts that tell the right rep which account to
call today" need speed. A demo request triggers a webhook → your code scores it, assigns the owner and
pings the rep in seconds.

## The pieces

- **Endpoint:** a URL on your side, e.g. `https://yourapp.com/hubspot/webhook`. In Python, a tiny Flask
  app with one route.
- **Subscription:** you tell the other system which events you want (contact created, deal stage
  changed…).
- **Event payload:** JSON describing what happened. HubSpot sends a **list** of events per request:

```json
[{"eventId": 101, "subscriptionId": 9001, "portalId": 4455, "occurredAt": 1763900000000,
  "subscriptionType": "deal.propertyChange", "objectId": 5001,
  "propertyName": "dealstage", "propertyValue": "demo_booked", "attemptNumber": 0}]
```

Note: the payload often contains only IDs, not the full record. Your code then calls the API to fetch
the details it needs.

## The five rules of a good receiver

1. **Reply 200 fast** (within a few seconds). Do slow work *after* replying (a queue or background
   job). Senders treat slow replies as failures and retry.
2. **Expect duplicates.** If the sender didn't get your 200 in time, it sends the event again. Store each
   event's key (e.g. `eventId`, `subscriptionId`, `occurredAt`) and skip ones you've already handled.
   That's **idempotency** again.
3. **Verify the signature.** Anyone who finds your URL could POST fake events. Senders sign each
   request with a shared secret (HubSpot's v3 signature is an HMAC-SHA256 over the method, URL, body
   and a timestamp header). Recompute it and reject mismatches with 401.
4. **Handle retries and ordering.** Senders retry failed deliveries (HubSpot retries for up to about
   a day). Events can arrive out of order, so use `occurredAt`, not arrival time.
5. **Log everything** and alert if events stop arriving.

## Signature verification, the idea

```python
import base64, hashlib, hmac

def is_valid(secret, method, url, body, timestamp, signature):
    message = f"{method}{url}{body}{timestamp}".encode()
    expected = base64.b64encode(hmac.new(secret.encode(), message, hashlib.sha256).digest()).decode()
    return hmac.compare_digest(expected, signature)   # constant-time comparison
```

Also reject requests whose timestamp is more than ~5 minutes old (stops replay attacks). Check the
current HubSpot docs for the exact header names and format.

## Testing locally

- Send fake events to your own receiver with `requests.post(...)` (lesson 5 does this).
- To receive real events on your laptop, use **ngrok** (or a similar tunnel): it gives your local
  server a temporary public HTTPS URL to paste into the subscription settings.

## HubSpot specifics (as of late 2026)

Service keys are for making API calls; they **can't receive webhooks**. For webhooks you create a
small app with HubSpot's command-line tool (`hs project create`, choosing static auth and webhooks),
install it in your account, and set the target URL and subscriptions.

## In production

Instead of a Python `set()` (lost on restart), store processed event keys in a database table with a
unique constraint. Put incoming events on a queue and process them with a worker, so the endpoint
always answers instantly.

## Interview phrasing

> "The CRM calls my endpoint the moment a demo request lands. I verify the signature, reply 200
> immediately, and process in the background: skip events I've already handled by event ID, fetch the
> record, score it, assign the owner and alert the rep in Slack. A webhook gets the lead to a rep in
> seconds instead of at the next hourly run."

Next: run [lessons/04_webhook_receiver.py](lessons/04_webhook_receiver.py)
