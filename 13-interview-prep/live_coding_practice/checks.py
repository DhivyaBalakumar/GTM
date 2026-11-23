"""Checks for problems.py and solutions.py. Each problem is checked separately so you see progress."""
import sqlite3
from pathlib import Path

import pandas as pd

from fakes import BadRequest, FakeCRM, FakeFlakyAPI, FakePagedAPI

DATA = Path(__file__).resolve().parents[2] / "data"


def build_db():
    con = sqlite3.connect(":memory:")
    for table, file in [("accounts", "crm_accounts.csv"), ("contacts", "crm_contacts.csv"),
                        ("deals", "crm_deals.csv"), ("leads", "inbound_leads.csv")]:
        pd.read_csv(DATA / file).to_sql(table, con, index=False)
    return con


def run(m):
    results = {}

    def problem(name, fn):
        try:
            fn()
            results[name] = "pass"
        except NotImplementedError:
            results[name] = "not done"
        except AssertionError as e:
            results[name] = f"FAIL: {e}"
        except Exception as e:
            results[name] = f"ERROR: {type(e).__name__}: {e}"

    def p1():
        cases = {"https://www.PeopleCo.de/about": "peopleco.de", "peopleco.de": "peopleco.de",
                 "anna@PeopleCo.de": "peopleco.de", "": "", None: ""}
        for raw, want in cases.items():
            got = m.normalize_domain(raw)
            assert got == want, f"normalize_domain({raw!r}) = {got!r}, expected {want!r}"

    def p2():
        rows = [{"website": "https://peopleco.de", "name": "Peopleco", "employees": ""},
                {"email": "anna@peopleco.de", "name": "PeopleCo GmbH", "employees": "120"},
                {"website": "", "email": "", "name": "nothing"},
                {"website": "opal.de", "name": "Opal", "employees": "25"}]
        out = m.dedupe(rows)
        assert len(out) == 2, f"expected 2 rows, got {len(out)}"
        assert any(r["name"] == "PeopleCo GmbH" for r in out), "should keep the most complete PeopleCo row"

    def p3():
        crm = FakeCRM()
        companies = [{"domain": "peopleco.de", "score": 90}, {"domain": "opal.de", "score": 70}]
        m.sync_companies(crm, companies)
        m.sync_companies(crm, [{"domain": "peopleco.de", "score": 95}, {"domain": "opal.de", "score": 70}])
        assert crm.count() == 2, f"CRM has {crm.count()} records after two runs, expected 2"
        assert crm.find_by_domain("peopleco.de")["score"] == 95, "second run should update the score"

    def p4():
        api = FakePagedAPI(total=2300)
        got = m.fetch_all_contacts(api)
        assert len(got) == 2300, f"got {len(got)} contacts, expected 2300"
        assert api.calls == 23, f"made {api.calls} calls, expected 23"

    def p5():
        api = FakeFlakyAPI(failures_before_success=2)
        assert m.enrich_with_retry(api, "peopleco.de")["employees"] == 120
        assert api.calls == 3, f"expected 3 calls (2 failures + success), got {api.calls}"
        bad = FakeFlakyAPI(permanent=True)
        try:
            m.enrich_with_retry(bad, "x")
            raise AssertionError("BadRequest should raise")
        except BadRequest:
            assert bad.calls == 1, "BadRequest must not be retried"
        never = FakeFlakyAPI(failures_before_success=99)
        try:
            m.enrich_with_retry(never, "x", max_tries=3)
            raise AssertionError("should raise RuntimeError after max_tries")
        except RuntimeError:
            assert never.calls == 3, f"expected exactly 3 tries, got {never.calls}"

    def p6():
        data = {"results": [{"properties": {"name": "A", "domain": "a.de", "numberofemployees": "51"}},
                            {"properties": {}}, {"properties": None},
                            {"properties": {"name": "B", "numberofemployees": "abc"}}]}
        got = m.parse_companies(data)
        assert got[0] == {"name": "A", "domain": "a.de", "employees": 51}, got[0]
        assert got[1] == {"name": "", "domain": "", "employees": 0}, got[1]
        assert got[2] == {"name": "", "domain": "", "employees": 0}, got[2]
        assert got[3]["employees"] == 0, got[3]
        assert m.parse_companies({}) == []

    def p7():
        def enrich(domain):
            if domain == "bad.io":
                raise TimeoutError("timeout")
            return {"employees": 10}
        rows = [{"domain": "a.de"}, {"domain": "bad.io"}, {"domain": "b.de"}]
        new_rows, failed = m.enrich_rows(rows, enrich)
        assert failed == 1, f"failed={failed}"
        assert new_rows[0]["employees"] == 10 and new_rows[2]["employees"] == 10
        assert "employees" not in rows[0], "don't modify the input rows; copy them"

    def p8():
        for n, want in [(19, "Small"), (20, "Mid-market"), (499, "Mid-market"), (500, "Enterprise")]:
            assert m.segment(n) == want, f"segment({n}) = {m.segment(n)!r}, expected {want!r}"

    def p9():
        leads = [{"source": "webinar", "created_at": "2026-10-15 14:00"},
                 {"source": "webinar", "created_at": "2026-10-20 09:00"},
                 {"source": "demo_form", "created_at": "2026-11-02 10:00"}]
        assert m.leads_per_source_month(leads) == {("webinar", "2026-10"): 2, ("demo_form", "2026-11"): 1}

    def p10():
        route = m.make_router()
        owners = {"peopleco.de": "tom"}
        assert route({"email": "anna@peopleco.de", "country": "DE"}, owners) == ("tom", "existing owner")
        assert route({"email": "x@a.de", "country": "DE"}, owners)[0] == "lena"
        assert route({"email": "x@b.at", "country": "AT"}, owners)[0] == "jonas"
        assert route({"email": "x@c.fr", "country": "FR"}, owners) == ("maria", "general round-robin")
        assert route({"email": "x@d.io", "country": ""}, owners) == ("head_of_sales", "fallback")

    def p11():
        seen, handled = set(), []
        events = [{"eventId": 1, "subscriptionId": 9, "occurredAt": 100},
                  {"eventId": 1, "subscriptionId": 9, "occurredAt": 100},
                  {"eventId": 2, "subscriptionId": 9, "occurredAt": 200}]
        assert m.process_events(events, seen, handled.append) == 2
        assert m.process_events(events[:1], seen, handled.append) == 0, "already-processed events must be skipped"
        assert len(handled) == 2

    def p12():
        con = build_db()
        for name in ("SQL_DUPLICATE_DOMAINS", "SQL_ACCOUNTS_WITHOUT_CONTACTS", "SQL_MEETING_RATE_BY_SOURCE"):
            sql = getattr(m, name)
            if "select" not in sql.lower():
                raise NotImplementedError
        dup = pd.read_sql(m.SQL_DUPLICATE_DOMAINS, con)
        assert dup.to_dict("records") == [{"domain": "peopleco.de", "copies": 2}], dup.to_dict("records")
        none = pd.read_sql(m.SQL_ACCOUNTS_WITHOUT_CONTACTS, con)
        assert list(none["name"]) == ["Corvex Analytics", "Fjord Systems", "Mosaic HR", "PEOPLECO GMBH"], list(none["name"])
        rate = pd.read_sql(m.SQL_MEETING_RATE_BY_SOURCE, con)
        assert rate.iloc[0]["source"] == "demo_form" and rate.iloc[0]["meeting_pct"] == 80.0, rate.to_dict("records")

    for name, fn in [("P1 normalise", p1), ("P2 dedupe", p2), ("P3 duplicates bug", p3), ("P4 pagination bug", p4),
                     ("P5 retry", p5), ("P6 nested JSON", p6), ("P7 enrich rows", p7), ("P8 boundary bug", p8),
                     ("P9 per source/month", p9), ("P10 routing", p10), ("P11 webhook once", p11), ("P12 SQL", p12)]:
        problem(name, fn)
    for name, status in results.items():
        print(f"{name:22} {status}")
    done = sum(s == "pass" for s in results.values())
    print(f"\n{done}/12 passing")
    return results
