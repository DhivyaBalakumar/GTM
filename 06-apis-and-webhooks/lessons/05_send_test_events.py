"""
API lesson 5: send test events to your webhook receiver
=======================================================

Receiver must be running:  python 06-apis-and-webhooks/lessons/04_webhook_receiver.py
Run me:                     python 06-apis-and-webhooks/lessons/05_send_test_events.py

Watch the RECEIVER's terminal: you'll see actions, a skipped duplicate and a rejected fake.
"""
import base64
import hashlib
import hmac
import json
import os
import time
from pathlib import Path

import requests

URL = "http://localhost:5051/webhook"
SECRET = os.getenv("WEBHOOK_SECRET", "practice-secret")
EVENTS = json.loads((Path(__file__).resolve().parents[2] / "data" / "webhook_events.json").read_text())


def send(events, secret=SECRET):
    body = json.dumps(events)
    timestamp = str(int(time.time() * 1000))
    message = f"POST{URL}{body}{timestamp}".encode("utf-8")
    signature = base64.b64encode(hmac.new(secret.encode(), message, hashlib.sha256).digest()).decode()
    headers = {"Content-Type": "application/json", "X-Signature-v3": signature, "X-Request-Timestamp": timestamp}
    r = requests.post(URL, data=body, headers=headers, timeout=10)
    return r.status_code, r.json()


print("1. Sending 4 events (event 101 appears twice, like a sender retry):")
print("  ", send(EVENTS))
time.sleep(2)

print("2. Sending event 102 again later (another duplicate):")
print("  ", send([EVENTS[2]]))
time.sleep(1)

print("3. A forged request signed with the wrong secret:")
print("  ", send([EVENTS[0]], secret="attacker-guess"))

print("\nNow look at the receiver's terminal: 2 actions, 1 ignored, 2 duplicates skipped, 1 rejected.")
