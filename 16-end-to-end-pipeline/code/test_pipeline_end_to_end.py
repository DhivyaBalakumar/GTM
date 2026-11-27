"""Checks for the end-to-end pipeline. Run from the repo root:  pytest"""
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("pipeline_e2e", HERE / "pipeline_end_to_end.py")
p = importlib.util.module_from_spec(spec)
sys.modules["pipeline_e2e"] = p
spec.loader.exec_module(p)


def test_normalisers():
    assert p.normalise_domain("https://www.PeopleCo.de/about?x=1") == "peopleco.de"
    assert p.normalise_domain("anna@peopleco.de") == "peopleco.de"
    assert p.normalise_country("Germany") == "DE" and p.normalise_country("nl") == "NL"
    assert p.parse_employees("51-200") == 125 and p.parse_employees("abc") is None


def test_title_classifier_edge_cases():
    assert p.classify_title("Software Engineer Intern")[0] == "junior"
    assert p.classify_title("Product Owner") == ("ic", "other")
    assert p.classify_title("Owner") == ("c_level", "executive")
    assert p.classify_title("Chief Technology Officer") == ("c_level", "engineering")
    assert p.classify_title("CISO") == ("c_level", "security")


def test_retry_gives_up_after_max_attempts():
    calls = []

    def always_429():
        calls.append(1)
        raise p.RateLimited(retry_after=0)

    try:
        p.call_with_retry(always_429, max_attempts=3, sleep=lambda s: None)
    except p.RateLimited:
        pass
    assert len(calls) == 3


def test_full_run_and_idempotency():
    report, crm, cache = p.run(verbose=False)
    assert report["quarantined"] == 2
    assert report["contacts"] < report["clean"]                  # dedupe merged something
    assert all(report["checks"].values())
    assert report["crm"]["contacts_created"] > 0
    report2, _, _ = p.run(crm=crm, cache=cache, verbose=False)
    assert report2["crm"]["contacts_created"] == 0 and report2["crm"]["companies_created"] == 0
    assert report2["credits_used"] == 0                           # cache: never pay twice


def test_per_record_error_handling():
    def process(key, rec):
        if rec == "bad":
            raise ValueError("broken")
        return rec.upper()

    ok, failed, summary = p.process_all([("a", "x"), ("b", "bad"), ("c", "y")], process, "t")
    assert ok == ["X", "Y"] and failed[0]["key"] == "b"
    assert summary["alert"] is True                               # 1/3 > 10%


def test_enrich_failure_does_not_stop_run():
    report, _, _ = p.run(verbose=False)
    assert [f["key"] for f in report["enrich_failures"]] == ["greenleafretail.com"]


def test_drill_solutions_pass_and_drill_starts_as_todo():
    sys.path.insert(0, str(HERE))
    import pipeline_drill_checks

    def load(name):
        s = importlib.util.spec_from_file_location(name, HERE / f"{name}.py")
        m = importlib.util.module_from_spec(s)
        s.loader.exec_module(m)
        return m

    solutions = pipeline_drill_checks.run(load("pipeline_drill_solutions"))
    assert all(v == "pass" for v in solutions.values()), solutions
    drill = pipeline_drill_checks.run(load("pipeline_drill"))
    assert all(v in ("todo", "pass") for v in drill.values()), drill


def test_summarize_demo_validation_catches_invented_number():
    s = importlib.util.spec_from_file_location("summarize_demo", HERE / "summarize_demo.py")
    sd = importlib.util.module_from_spec(s)
    s.loader.exec_module(sd)
    assert sd.account_brief(sd.fake_model)["problems"] == []
    res = sd.map_reduce_summary(sd.fake_model, sd.CALL_NOTES)
    assert any("50000" in prob for prob in res["problems"])
