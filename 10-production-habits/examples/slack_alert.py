"""
Post a message to Slack with an incoming webhook.
=================================================

1. In Slack: create an app (api.slack.com/apps) -> Incoming Webhooks -> activate -> add to a channel.
2. Copy the webhook URL into .env as SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
3. Run:  python 10-production-habits/examples/slack_alert.py

Without SLACK_WEBHOOK_URL it just prints what it would send.
"""
import os

import requests

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def send_slack(text, url=None):
    url = url or os.getenv("SLACK_WEBHOOK_URL")
    if not url:
        print("[no SLACK_WEBHOOK_URL] would send:\n" + text)
        return False
    r = requests.post(url, json={"text": text}, timeout=10)
    r.raise_for_status()
    return True


def call_today_alert(owner, company, reasons, score):
    return f"📞 *{owner}*, call *{company}* today (score {score}): " + "; ".join(reasons)


def failure_alert(step, error, log_link="<logs>"):
    return f"🔴 *Account pipeline failed* at step `{step}`: {error}\nLogs: {log_link}"


if __name__ == "__main__":
    send_slack(call_today_alert("lena", "PeopleCo GmbH",
                                ["hiring an ISO 27001 manager (2 days ago)", "Series A last month",
                                 "120 staff, Berlin, software"], 95))
    send_slack(failure_alert("load", "HTTP 401 Unauthorized: check the HubSpot service key"))
