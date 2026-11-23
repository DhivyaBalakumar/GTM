"""
A small, readable HubSpot client: the core operations a GTM pipeline needs.
=========================================================================

Dry run (no key needed, prints the exact requests it WOULD send):
    python 07-crm-hubspot/hubspot_client.py --dry-run
Real run (needs HUBSPOT_TOKEN in .env, a service key with company read/write + schema write scopes):
    python 07-crm-hubspot/hubspot_client.py

What main() demonstrates:
  1. Create a unique property `company_domain_key` (once; 409 means it already exists: fine)
  2. Batch upsert companies keyed on that property (run twice -> no duplicates)
  3. Search a company by domain
  4. Page through all companies

Check HubSpot's current docs if an endpoint has changed: https://developers.hubspot.com/docs/api/overview
"""
import argparse
import json
import logging
import os
import random
import time

import requests

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:      # python-dotenv not installed: environment variables still work
    pass

BASE = "https://api.hubapi.com"
UNIQUE_PROPERTY = "company_domain_key"
BATCH_SIZE = 100                       # HubSpot batch endpoints accept up to 100 inputs
RETRYABLE = {429, 500, 502, 503, 504}
log = logging.getLogger("hubspot")


class HubSpot:
    def __init__(self, token=None, dry_run=False):
        self.dry_run = dry_run
        self.token = token or os.getenv("HUBSPOT_TOKEN")
        if not self.token and not dry_run:
            raise ValueError("HUBSPOT_TOKEN is missing. Add your service key to .env, or use --dry-run.")
        self.session = requests.Session()     # reuses the connection and headers for every call
        self.session.headers.update({"Authorization": f"Bearer {self.token}",
                                     "Content-Type": "application/json"})

    # ------------------------------------------------------------------ the one place HTTP happens
    def request(self, method, path, max_tries=5, **kwargs):
        url = BASE + path
        if self.dry_run and method != "GET":
            log.info("[dry-run] %s %s\n%s", method, url, json.dumps(kwargs.get("json"), indent=2)[:1500])
            return None
        if self.dry_run:
            log.info("[dry-run] %s %s params=%s", method, url, kwargs.get("params"))
            return None
        kwargs.setdefault("timeout", 15)
        for attempt in range(1, max_tries + 1):
            wait = 2 ** (attempt - 1) + random.uniform(0, 0.5)
            try:
                r = self.session.request(method, url, **kwargs)
            except (requests.ConnectionError, requests.Timeout) as e:
                log.warning("%s %s: network error %s (attempt %d)", method, path, e, attempt)
            else:
                if r.status_code not in RETRYABLE:
                    if r.status_code >= 400:
                        log.error("%s %s -> %d %s", method, path, r.status_code, r.text[:500])
                    r.raise_for_status()
                    return r.json() if r.content else None
                wait = float(r.headers.get("Retry-After", wait))
                log.warning("%s %s -> %d, retrying in %.1fs", method, path, r.status_code, wait)
            if attempt < max_tries:
                time.sleep(wait)
        raise RuntimeError(f"Gave up after {max_tries} tries: {method} {path}")

    # ------------------------------------------------------------------ properties
    def ensure_unique_property(self, name=UNIQUE_PROPERTY, label="Company domain key"):
        body = {"name": name, "label": label, "type": "string", "fieldType": "text",
                "groupName": "companyinformation", "hasUniqueValue": True}
        try:
            self.request("POST", "/crm/v3/properties/companies", json=body)
            log.info("%s unique property %s", "Would create" if self.dry_run else "Created", name)
        except requests.HTTPError as e:
            if e.response is not None and e.response.status_code == 409:
                log.info("Property %s already exists", name)
            else:
                raise

    # ------------------------------------------------------------------ writes
    @staticmethod
    def _clean(properties):
        """Never send blanks: drop None/"" and convert everything to strings (HubSpot's format)."""
        return {k: str(v) for k, v in properties.items() if v is not None and v != ""}

    def upsert_companies(self, companies):
        """companies: list of dicts that each include 'domain'. Returns created/updated counts."""
        totals = {"created": 0, "updated": 0, "batches": 0}
        inputs = [{"idProperty": UNIQUE_PROPERTY, "id": c["domain"],
                   "properties": self._clean({**c, UNIQUE_PROPERTY: c["domain"]})}
                  for c in companies if c.get("domain")]
        for start in range(0, len(inputs), BATCH_SIZE):
            batch = inputs[start:start + BATCH_SIZE]
            result = self.request("POST", "/crm/v3/objects/companies/batch/upsert", json={"inputs": batch})
            totals["batches"] += 1
            for item in (result or {}).get("results", []):
                totals["created" if item.get("new") else "updated"] += 1
        return totals

    # ------------------------------------------------------------------ reads
    def search_company_by_domain(self, domain):
        body = {"filterGroups": [{"filters": [{"propertyName": "domain", "operator": "EQ", "value": domain}]}],
                "properties": ["name", "domain", "hubspot_owner_id", "fit_score"], "limit": 10}
        result = self.request("POST", "/crm/v3/objects/companies/search", json=body)
        return (result or {}).get("results", [])

    def get_all_companies(self, properties=("name", "domain", "hubspot_owner_id")):
        results, params = [], {"limit": 100, "properties": ",".join(properties)}
        while True:
            data = self.request("GET", "/crm/v3/objects/companies", params=params)
            if data is None:                         # dry run
                return results
            results.extend(data.get("results", []))
            after = data.get("paging", {}).get("next", {}).get("after")
            if not after:
                return results
            params["after"] = after

    # ------------------------------------------------------------------ associations
    def associate_contact_to_company(self, contact_id, company_id):
        path = f"/crm/v4/objects/contacts/{contact_id}/associations/default/companies/{company_id}"
        return self.request("PUT", path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="print requests instead of sending them")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)-7s %(message)s")

    hs = HubSpot(dry_run=args.dry_run)
    hs.ensure_unique_property()
    companies = [
        {"domain": "peopleco.de", "name": "PeopleCo GmbH", "industry": "COMPUTER_SOFTWARE",
         "numberofemployees": 120, "country": "Germany"},
        {"domain": "nordbanktech.nl", "name": "Nordbank Tech B.V.", "numberofemployees": 80,
         "country": "Netherlands", "description": ""},          # the blank is dropped, not sent
    ]
    log.info("Upsert result: %s", hs.upsert_companies(companies))
    log.info("Search peopleco.de: %s", hs.search_company_by_domain("peopleco.de"))
    log.info("Companies in the portal: %d", len(hs.get_all_companies()))
    log.info("Run me again: the second upsert should report created=0.")


if __name__ == "__main__":
    main()
