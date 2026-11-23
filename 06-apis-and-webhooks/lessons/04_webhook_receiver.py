"""
API lesson 4: a webhook receiver
================================

Run me (and leave me running):
    python 06-apis-and-webhooks/lessons/04_webhook_receiver.py
Then, in another terminal, send events:
    python 06-apis-and-webhooks/lessons/05_send_test_events.py

What this shows:
  1. Verify the signature (reject fake requests with 401)
  2. Reply 200 FAST: put events on a queue and process them in a background worker
  3. Skip duplicate events (the same event can arrive twice)
  4. Act only on the events you care about
"""
import base64
import hashlib
import hmac
import logging
import os
import queue
import threading
import time

from flask import Flask, jsonify, request

SECRET = os.getenv("WEBHOOK_SECRET", "practice-secret")    # shared with the sender
MAX_AGE_SECONDS = 300

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)-7s %(message)s", datefmt="%H:%M:%S")
log = logging.getLogger("webhook")
app = Flask(__name__)

events_queue = queue.Queue()
processed = set()          # production: a database table with a UNIQUE constraint


def expected_signature(method, url, body, timestamp):
    message = f"{method}{url}{body}{timestamp}".encode("utf-8")
    digest = hmac.new(SECRET.encode("utf-8"), message, hashlib.sha256).digest()
    return base64.b64encode(digest).decode()


def signature_ok(req):
    signature = req.headers.get("X-Signature-v3", "")
    timestamp = req.headers.get("X-Request-Timestamp", "")
    if not signature or not timestamp.isdigit():
        return False
    if abs(time.time() * 1000 - int(timestamp)) > MAX_AGE_SECONDS * 1000:
        return False                                          # too old: possible replay
    expected = expected_signature(req.method, req.url, req.get_data(as_text=True), timestamp)
    return hmac.compare_digest(expected, signature)           # constant-time comparison


@app.post("/webhook")
def receive():
    if not signature_ok(request):
        log.warning("Rejected request with a bad or missing signature")
        return jsonify({"error": "invalid signature"}), 401
    events = request.get_json(silent=True)
    if not isinstance(events, list):
        return jsonify({"error": "expected a list of events"}), 400
    for event in events:
        events_queue.put(event)                               # hand off; don't do slow work here
    return jsonify({"received": len(events)}), 200            # answer within milliseconds


def handle(event):
    """The slow part: runs in the background worker."""
    if event.get("subscriptionType") == "deal.propertyChange" and event.get("propertyValue") == "demo_booked":
        time.sleep(0.5)                                       # pretend: fetch deal, look up owner, post to Slack
        log.info("ACTION: deal %s booked a demo -> alert the AE in Slack", event.get("objectId"))
    elif event.get("subscriptionType") == "contact.creation":
        log.info("ACTION: new contact %s -> enrich, score and route", event.get("objectId"))
    else:
        log.info("ignored event type %s (%s)", event.get("subscriptionType"), event.get("propertyValue"))


def worker():
    while True:
        event = events_queue.get()
        key = (event.get("eventId"), event.get("subscriptionId"), event.get("occurredAt"))
        if key in processed:
            log.info("DUPLICATE skipped: event %s (attempt %s)", key[0], event.get("attemptNumber"))
            continue
        processed.add(key)
        try:
            handle(event)
        except Exception:
            log.exception("Failed to handle event %s", key)   # log, don't crash the worker


if __name__ == "__main__":
    threading.Thread(target=worker, daemon=True).start()
    print("Webhook receiver on http://localhost:5051/webhook  (Ctrl+C to stop)")
    app.run(port=5051, debug=False)
