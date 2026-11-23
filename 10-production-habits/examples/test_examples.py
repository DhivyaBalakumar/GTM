"""
pytest examples. Run:  pytest 10-production-habits/examples/test_examples.py -v

Each test is a function starting with test_ that uses assert.
"""
from unittest.mock import Mock, patch

import pytest
import requests


# ----------------------------------------------------------------------------- code under test
def normalize_domain(value):
    if not value:
        return ""
    v = value.strip().lower().split("@")[-1]
    for prefix in ("https://", "http://", "www."):
        v = v.removeprefix(prefix)
    return v.split("/")[0]


def segment(employees):
    if employees is None:
        return "Unknown"
    if employees >= 500:
        return "Enterprise"
    if employees >= 20:
        return "Mid-market"
    return "Small"


def require_key(key):
    if not key:
        raise ValueError("API key missing")
    return key


def fetch_employees(domain):
    """Calls an API. In tests we replace requests.get so nothing goes over the network."""
    r = requests.get("https://api.example.com/enrich", params={"domain": domain}, timeout=10)
    if r.status_code == 404:
        return None
    r.raise_for_status()
    return r.json()["employees"]


# ----------------------------------------------------------------------------- tests
def test_normalize_url():
    assert normalize_domain("https://www.PeopleCo.de/about") == "peopleco.de"


def test_normalize_email_and_blank():
    assert normalize_domain("anna@peopleco.de") == "peopleco.de"
    assert normalize_domain("") == ""
    assert normalize_domain(None) == ""


@pytest.mark.parametrize("employees, expected", [
    (None, "Unknown"), (19, "Small"), (20, "Mid-market"), (499, "Mid-market"), (500, "Enterprise"),
])
def test_segment_boundaries(employees, expected):
    assert segment(employees) == expected


def test_missing_key_raises():
    with pytest.raises(ValueError, match="missing"):
        require_key("")


@patch("requests.get")
def test_fetch_employees_ok(mock_get):
    mock_get.return_value = Mock(status_code=200, json=lambda: {"employees": 120})
    mock_get.return_value.raise_for_status = lambda: None
    assert fetch_employees("peopleco.de") == 120
    mock_get.assert_called_once()                     # we called the API exactly once


@patch("requests.get")
def test_fetch_employees_404_means_no_data(mock_get):
    mock_get.return_value = Mock(status_code=404)
    assert fetch_employees("unknown.io") is None
