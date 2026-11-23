# 2. Testing with pytest

## Why

Tests let you change code without fear, and they prove your logic does what you claim. In a take-home,
a few good tests on the decision logic signal "production habits" more than anything else.

## The basics

A test is a function whose name starts with `test_`, in a file whose name starts with `test_`, that
uses `assert`:

```python
# tests/test_transform.py
from transform import normalize_domain

def test_strips_protocol_www_and_path():
    assert normalize_domain("https://www.PeopleCo.de/about") == "peopleco.de"

def test_uses_email_domain():
    assert normalize_domain("anna@peopleco.de") == "peopleco.de"

def test_empty_values():
    assert normalize_domain("") == ""
    assert normalize_domain(None) == ""
```

Run: `pytest` (finds all tests) or `pytest -v` (shows each one). A failing assert shows the expected
and actual values.

## What to test (the decisions that matter)

| Test | Example |
| --- | --- |
| Normalisation | URLs, emails, case, blanks, None |
| Parsing | "51-200" → 125, "abc" → None |
| Dedupe | Keeps the most complete row; drops empty keys |
| **Boundaries** | 20 employees is in the ICP, 19 is not; score 75 is tier A, 74 is B |
| Routing | Existing owner wins; fallback when no country |
| Validation | Bad AI output is rejected |
| Idempotency | Running the load twice creates nothing the second time (with a fake CRM) |

Don't test that pandas or requests work; test **your** logic.

## parametrize: many cases, one test

```python
import pytest

@pytest.mark.parametrize("employees, expected", [
    (19, "Small"), (20, "Mid-market"), (499, "Mid-market"), (500, "Enterprise"), (None, "Unknown"),
])
def test_segment(employees, expected):
    assert segment(employees) == expected
```

## Expected errors

```python
def test_missing_key_raises():
    with pytest.raises(ValueError):
        require_key("")
```

## Testing code that calls APIs (without calling them)

Keep API calls in a few small functions, and **pass them in** or replace them in tests:

```python
def enrich_all(domains, fetch):          # fetch is a function: real or fake
    return {d: fetch(d) for d in domains}

def test_enrich_all_handles_missing():
    fake = {"a.de": {"employees": 10}}.get
    assert enrich_all(["a.de", "b.de"], fake) == {"a.de": {"employees": 10}, "b.de": None}
```

Or use `unittest.mock.patch` to replace `requests.get` (see
[examples/test_examples.py](examples/test_examples.py)).

## Other kinds of checking

- **Dry runs on real data** before the first real write.
- **Small batch first** (10 records), check in the CRM, then the full run.
- **Data-quality checks** after each run (duplicates = 0, etc.).

Next: [03-scheduling-and-monitoring.md](03-scheduling-and-monitoring.md)
