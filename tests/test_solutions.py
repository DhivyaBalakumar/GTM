"""
Checks that every solution in the repo passes its own checks.
Run from the repo root:  pytest

(The API exercise needs the practice server running, so it's skipped automatically if it isn't.)
"""
import importlib.util
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]


def load(path):
    path = REPO / path
    sys.path.insert(0, str(path.parent))
    try:
        spec = importlib.util.spec_from_file_location(f"sol_{path.stem}_{abs(hash(path))}", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        sys.path.remove(str(path.parent))


@pytest.mark.parametrize("path", [
    "03-python/solutions/ex01_strings.py",
    "03-python/solutions/ex02_collections.py",
    "03-python/solutions/ex03_functions_and_rules.py",
    "03-python/solutions/ex04_errors_and_files.py",
    "04-pandas/solutions/ex01_clean_score.py",
])
def test_exercise_solution(path):
    assert load(path)._checks() == []


def test_live_coding_solutions():
    folder = REPO / "13-interview-prep" / "live_coding_practice"
    sys.path.insert(0, str(folder))
    try:
        solutions = load("13-interview-prep/live_coding_practice/solutions.py")
        import checks
        results = checks.run(solutions)
    finally:
        sys.path.remove(str(folder))
    assert all(status == "pass" for status in results.values()), results


def test_api_solution_if_server_running():
    requests = pytest.importorskip("requests")
    try:
        requests.post("http://localhost:5050/admin/reset", timeout=1)
    except requests.ConnectionError:
        pytest.skip("practice API not running (python 06-apis-and-webhooks/practice_server.py)")
    assert load("06-apis-and-webhooks/solutions/ex01_api_client.py")._checks() == []
