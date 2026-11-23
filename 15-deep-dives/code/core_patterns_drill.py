"""
Core patterns drill: rebuild the 6 patterns from their recipes
==============================================================

Run me:  python 15-deep-dives/code/core_patterns_drill.py

For each function: read the recipe (the comments), then write the code underneath WITHOUT looking at
the lessons. Run this file to check. Do it again from scratch 2-3 days later (delete your code, keep
the comments). Reference answers: core_patterns_solutions.py. Guide: HOW_TO_LEARN_THE_CODE.md.

Patterns 3-5 use small fake APIs below, so no server or internet is needed.
"""
import logging
import random
import time

log = logging.getLogger("drill")


# ----------------------------------------------------------------------------- 1. normalise
def normalize_domain(value):
    # 1. if the value is empty or None, return ""
    # 2. strip spaces and lowercase it
    # 3. if there's an @, keep the part after it (an email)
    # 4. remove https://, http:// and www. from the start
    # 5. cut at the first / and keep the left part
    raise NotImplementedError


# ----------------------------------------------------------------------------- 2. dedupe
def dedupe(rows):
    # 1. make an empty dict: key -> (how complete, row)
    # 2. for each row: key = normalize_domain(website, or email if no website); skip rows with no key
    # 3. count how many fields are filled in (not None, not "")
    # 4. if the key is new, or this row is MORE complete than the stored one, store this row
    #    (on a tie, keep the first one)
    # 5. return the stored rows
    raise NotImplementedError


# ----------------------------------------------------------------------------- 3. retry
class TemporaryError(Exception):
    """Stands in for a 429 / 5xx / network error."""


class PermanentError(Exception):
    """Stands in for a 400 / 401 / 404: never retry these."""


def call_with_retry(fn, max_tries=5, base_wait=0.01):
    # 1. loop over attempts 1..max_tries
    # 2. try: return fn()
    # 3. except TemporaryError: if this was the last attempt, stop looping;
    #    otherwise sleep base_wait * 2 ** (attempt - 1) and try again
    #    (PermanentError is NOT caught: it should go straight up to the caller)
    # 4. after the loop: raise RuntimeError("Gave up ...")
    raise NotImplementedError


# ----------------------------------------------------------------------------- 4. pagination
def get_all(fetch_page):
    # fetch_page(after) returns {"results": [...], "paging": {"next": {"after": "..."}}}
    # and has no "paging" key on the last page.
    # 1. start with an empty list and after = None
    # 2. loop forever:
    # 3.   data = fetch_page(after); add data's results to the list
    # 4.   read the next cursor safely (.get at each level)
    # 5.   if there's no cursor, return the list; otherwise set after = cursor
    raise NotImplementedError


# ----------------------------------------------------------------------------- 5. batching
def send_in_batches(records, send, size=100):
    # send(batch) returns {"created": int, "updated": int}
    # 1. totals = {"created": 0, "updated": 0}
    # 2. loop i from 0 to len(records), stepping by size
    # 3. batch = records[i : i + size]; result = send(batch); add result's counts to totals
    # 4. return totals
    raise NotImplementedError


# ----------------------------------------------------------------------------- 6. per-record errors
def process_all(records, process):
    # 1. ok = [], failed = []
    # 2. for each record:
    # 3.   try: ok.append(process(record))
    # 4.   except Exception as e: failed.append(record.get("domain")); log.warning which and why
    # 5. return ok, failed
    raise NotImplementedError


# ============================================================================= checks
def _checks(m):
    results = {}

    def run(name, fn):
        try:
            fn()
            results[name] = "pass"
        except NotImplementedError:
            results[name] = "not done"
        except AssertionError as e:
            results[name] = f"FAIL: {e}"
        except Exception as e:
            results[name] = f"ERROR: {type(e).__name__}: {e}"

    def c1():
        for raw, want in {"https://www.PeopleCo.de/about": "peopleco.de", "anna@PeopleCo.de": "peopleco.de",
                          "  peopleco.de ": "peopleco.de", "http://x.io/": "x.io", "": "", None: ""}.items():
            got = m.normalize_domain(raw)
            assert got == want, f"normalize_domain({raw!r}) = {got!r}, expected {want!r}"

    def c2():
        rows = [{"website": "peopleco.de", "name": "Peopleco", "employees": ""},
                {"email": "anna@peopleco.de", "name": "PeopleCo GmbH", "employees": "120"},
                {"website": "", "email": "", "name": "no key"},
                {"website": "opal.de", "name": "Opal", "employees": "25"},
                {"website": "https://opal.de", "name": "Opal 2", "employees": "25"}]
        out = m.dedupe(rows)
        assert len(out) == 2, f"expected 2 rows, got {len(out)}"
        names = sorted(r["name"] for r in out)
        assert names == ["Opal", "PeopleCo GmbH"], f"kept {names}, expected ['Opal', 'PeopleCo GmbH']"

    def c3():
        calls = {"n": 0}

        def flaky():
            calls["n"] += 1
            if calls["n"] < 3:
                raise m.TemporaryError("429")
            return "ok"
        assert m.call_with_retry(flaky) == "ok" and calls["n"] == 3, "should succeed on the 3rd try"
        perm = {"n": 0}

        def bad():
            perm["n"] += 1
            raise m.PermanentError("400")
        try:
            m.call_with_retry(bad)
            raise AssertionError("PermanentError should be raised")
        except m.PermanentError:
            assert perm["n"] == 1, "PermanentError must not be retried"
        never = {"n": 0}

        def down():
            never["n"] += 1
            raise m.TemporaryError("503")
        try:
            m.call_with_retry(down, max_tries=3)
            raise AssertionError("should raise RuntimeError after max_tries")
        except RuntimeError:
            assert never["n"] == 3, f"expected 3 tries, got {never['n']}"

    def c4():
        items = list(range(23))

        def fetch_page(after):
            start = int(after or 0)
            body = {"results": items[start:start + 5]}
            if start + 5 < len(items):
                body["paging"] = {"next": {"after": str(start + 5)}}
            return body
        assert m.get_all(fetch_page) == items, "should return all 23 items in order"

    def c5():
        sizes = []

        def send(batch):
            sizes.append(len(batch))
            return {"created": len(batch), "updated": 0}
        assert m.send_in_batches(list(range(230)), send, size=100) == {"created": 230, "updated": 0}
        assert sizes == [100, 100, 30], f"batch sizes {sizes}, expected [100, 100, 30]"

    def c6():
        def process(rec):
            if rec["domain"] == "bad.io":
                raise ValueError("bad data")
            return rec["domain"].upper()
        ok, failed = m.process_all([{"domain": "a.de"}, {"domain": "bad.io"}, {"domain": "b.de"}], process)
        assert ok == ["A.DE", "B.DE"] and failed == ["bad.io"], f"ok={ok} failed={failed}"

    for name, fn in [("1 normalise", c1), ("2 dedupe", c2), ("3 retry", c3),
                     ("4 pagination", c4), ("5 batching", c5), ("6 per-record errors", c6)]:
        run(name, fn)
    for name, status in results.items():
        print(f"{name:22} {status}")
    print(f"\n{sum(s == 'pass' for s in results.values())}/6 passing")
    return results


if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.WARNING, format="%(levelname)s %(message)s")
    _checks(sys.modules[__name__])
