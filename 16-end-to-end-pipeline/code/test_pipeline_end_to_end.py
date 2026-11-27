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
    assert p.classify_title("Product Owner")[0] != "c_level"
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
