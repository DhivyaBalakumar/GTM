"""Checks shared by pipeline_drill.py and pipeline_drill_solutions.py. You don't need to edit this."""


def _check(name, fn):
    try:
        fn()
        return "pass"
    except NotImplementedError:
        return "todo"
    except AssertionError as e:
        return f"FAIL {e}"
    except Exception as e:                                       # noqa: BLE001
        return f"ERROR {e.__class__.__name__}: {e}"


def run(m):
    results = {}

    def c1():
        assert m.normalise_country("Germany") == "DE", "Germany -> DE"
        assert m.normalise_country(" de ") == "DE", "' de ' -> DE"
        assert m.normalise_country("Atlantis") is None, "unknown -> None"
        assert m.normalise_country("") is None and m.normalise_country(None) is None, "blank -> None"
    results["1 normalise_country"] = _check("1", c1)

    def c2():
        assert m.parse_employees("120") == 120
        assert m.parse_employees("1,200") == 1200, "commas"
        assert m.parse_employees("51-200") == 125, "range midpoint"
        assert m.parse_employees("500+") == 500, "'500+' -> 500"
        assert m.parse_employees("abc") is None and m.parse_employees(None) is None
    results["2 parse_employees"] = _check("2", c2)

    def c3():
        assert m.classify_seniority("Software Engineer Intern") == "junior", "intern first"
        assert m.classify_seniority("CTO") == "c_level"
        assert m.classify_seniority("Director of Sales") == "vp_head", "director is not cto"
        assert m.classify_seniority("Engineering Manager") == "manager"
        assert m.classify_seniority("Developer") == "ic"
        assert m.classify_seniority("") is None
    results["3 classify_seniority"] = _check("3", c3)

    def c4():
        assert m.email_kind("anna@peopleco.de") == "work"
        assert m.email_kind("Max@GMAIL.com") == "personal", "case-insensitive"
        assert m.email_kind("info@corvex.de") == "role"
        assert m.email_kind("not-an-email") is None
    results["4 email_kind"] = _check("4", c4)

    def c5():
        recs = [{"source": "webinar", "title": "Head of IT", "phone": "+491"},
                {"source": "crm", "title": "", "phone": None},
                {"source": "apollo", "title": "CTO", "phone": "+492"}]
        g = m.survivorship(recs, ["title", "phone"], ["crm", "apollo", "webinar"])
        assert g["title"] == "CTO", "crm title is blank, so apollo wins"
        assert g["phone"] == "+492"
        assert g["lineage"] == {"title": "apollo", "phone": "apollo"}
    results["5 survivorship"] = _check("5", c5)

    def c6():
        rows = [{"e": "A@x.de"}, {"e": "a@x.de "}, {"e": ""}, {"e": "b@x.de"}]
        g = m.group_by_key(rows, lambda r: r["e"].strip().lower())
        assert set(g) == {"a@x.de", "b@x.de"}, "blank keys skipped"
        assert len(g["a@x.de"]) == 2
    results["6 group_by_key"] = _check("6", c6)

    def c7():
        calls = []
        a = ("a", 1, lambda d: calls.append("a") or {"industry": "software"})
        b = ("b", 3, lambda d: calls.append("b") or {"employees": 40, "industry": "saas"})
        cache = {}
        filled, spent = m.enrich_waterfall("x.de", ["industry", "employees"], [a, b], cache, budget=10)
        assert filled == {"industry": "software", "employees": 40}, "A fills industry, B only employees"
        assert spent == 4
        filled2, spent2 = m.enrich_waterfall("x.de", ["industry", "employees"], [a, b], cache, budget=10)
        assert spent2 == 0 and calls == ["a", "b"], "second call uses the cache"
        _, spent3 = m.enrich_waterfall("y.de", ["industry", "employees"], [a, b], {}, budget=2)
        assert spent3 == 1, "stops before exceeding the budget"
    results["7 enrich_waterfall"] = _check("7", c7)

    def c8():
        rules = [(lambda r: r["unsub"], "unsubscribed"), (lambda r: r["customer"], "existing_customer")]
        assert m.first_match(rules, {"unsub": True, "customer": True}) == "unsubscribed", "order matters"
        assert m.first_match(rules, {"unsub": False, "customer": True}) == "existing_customer"
        assert m.first_match(rules, {"unsub": False, "customer": False}, default="ok") == "ok"
    results["8 first_match"] = _check("8", c8)

    def c9():
        rules = [(20, "software", lambda r: r["industry"] == "software"),
                 (15, "DACH", lambda r: r["country"] in {"DE", "AT", "CH"}),
                 (70, "funding", lambda r: r["funded"]),
                 (-30, "personal email", lambda r: r["personal"])]
        tiers = [(80, "A"), (60, "B"), (40, "C"), (0, "D")]
        s, t, why = m.score_with_reasons({"industry": "software", "country": "DE", "funded": True,
                                          "personal": False}, rules, tiers)
        assert (s, t) == (100, "A"), "capped at 100"
        assert why == ["software", "DACH", "funding"]
        s, t, _ = m.score_with_reasons({"industry": "x", "country": "US", "funded": False,
                                        "personal": True}, rules, tiers)
        assert (s, t) == (0, "D"), "floored at 0"
    results["9 score_with_reasons"] = _check("9", c9)

    def c10():
        leads = [{"email": "a@x.de", "domain": "x.de"}, {"email": "b@y.de", "domain": "y.de"},
                 {"email": "c@y.de", "domain": "y.de"}, {"email": "d@z.de", "domain": "z.de"},
                 {"email": "e@w.de", "domain": "w.de"}]
        out = m.route(leads, {"x.de": "maria"}, ["lena", "jonas"])
        assert out["a@x.de"] == "maria", "keep existing owner"
        assert out["b@y.de"] == out["c@y.de"] == "lena", "one owner per account"
        assert out["d@z.de"] == "jonas" and out["e@w.de"] == "lena", "round robin over new domains"
    results["10 route"] = _check("10", c10)

    def c11():
        props = {"gtm_score": 90, "industry": "software", "hubspot_owner_id": "tom", "city": "", "phone": None}
        existing = {"industry": "fintech", "hubspot_owner_id": "lena"}
        out = m.build_payload(props, existing, human_owned={"hubspot_owner_id"}, fill_if_empty={"industry"})
        assert out == {"gtm_score": 90}, f"got {out}"
        out = m.build_payload(props, {}, human_owned={"hubspot_owner_id"}, fill_if_empty={"industry"})
        assert out == {"gtm_score": 90, "industry": "software", "hubspot_owner_id": "tom"}
    results["11 build_payload"] = _check("11", c11)

    def c12():
        last = {}
        assert m.should_alert(("x.de", "funding"), 1, last, 14) is True
        assert m.should_alert(("x.de", "funding"), 5, last, 14) is False, "inside cooldown"
        assert m.should_alert(("x.de", "hiring"), 5, last, 14) is True, "different signal type"
        assert m.should_alert(("x.de", "funding"), 15, last, 14) is True, "cooldown over"
    results["12 should_alert"] = _check("12", c12)

    def c13():
        rows = [{"tier": "A", "score": 90}, {"tier": "B", "score": 70}, {"tier": "B", "score": 65}]
        s = m.summarise(rows, "tier", "score")
        assert s == {"A": {"count": 1, "avg": 90.0}, "B": {"count": 2, "avg": 67.5}}, f"got {s}"
    results["13 summarise"] = _check("13", c13)

    def c14():
        def proc(x):
            if x < 0:
                raise ValueError("negative")
            return x * 2
        ok, failed, alert = m.process_all([1, -1, 2, 3], proc)
        assert ok == [2, 4, 6] and failed[0]["record"] == -1 and alert is True
        ok, failed, alert = m.process_all([1] * 20 + [-1], proc)
        assert alert is False, "1 in 21 is under 10%"
        try:
            m.process_all([None], lambda x: x + 1)          # TypeError must NOT be swallowed
            raise AssertionError("only ValueError should be caught")
        except TypeError:
            pass
    results["14 process_all"] = _check("14", c14)
    return results


def report(module):
    results = run(module)
    for name, status in results.items():
        mark = "✔" if status == "pass" else "·" if status == "todo" else "✘"
        print(f"{mark} {name:22} {status}")
    done = sum(s == "pass" for s in results.values())
    print(f"\n{done}/{len(results)} passing")
    return results
