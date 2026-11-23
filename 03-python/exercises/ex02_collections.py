"""
Exercise 2: lists, dictionaries and sets
========================================

Fill in each function, then run:
    python 03-python/exercises/ex02_collections.py
"""


def count_by(rows, field):
    """Count rows per value of `field`. Skip rows where the value is missing or "".

    count_by([{"c": "DE"}, {"c": "NL"}, {"c": "DE"}, {"c": ""}], "c") -> {"DE": 2, "NL": 1}
    """
    raise NotImplementedError


def group_by(rows, field):
    """Group rows into lists by `field`.

    group_by([{"o": "lena", "n": 1}, {"o": "tom", "n": 2}, {"o": "lena", "n": 3}], "o")
      -> {"lena": [{"o": "lena", "n": 1}, {"o": "lena", "n": 3}], "tom": [{"o": "tom", "n": 2}]}
    """
    raise NotImplementedError


def batches(items, size):
    """Split a list into lists of at most `size` items, in order.

    batches([1, 2, 3, 4, 5], 2) -> [[1, 2], [3, 4], [5]];  batches([], 3) -> []
    """
    raise NotImplementedError


def new_vs_existing(new_domains, crm_domains):
    """Return (brand_new, already_in_crm) as SORTED lists, ignoring duplicates.

    new_vs_existing(["a.de", "b.de", "a.de"], ["b.de", "c.de"]) -> (["a.de"], ["b.de"])
    """
    raise NotImplementedError


def filled_count(row):
    """How many values in a dict are not None and not "" (after stripping strings)?

    filled_count({"a": "x", "b": "", "c": None, "d": " ", "e": 0}) -> 2   (0 counts as filled)
    """
    raise NotImplementedError


def dedupe_keep_most_complete(rows, key_field):
    """One row per value of `key_field`, keeping the row with the most filled fields.

    Rows with an empty key are dropped. On a tie, keep the FIRST one seen.
    Return rows in the order their key first appeared.
    """
    raise NotImplementedError


# --------------------------------------------------------------------------- checks
def _checks():
    failures = []

    def check(label, got, expected):
        if got != expected:
            failures.append(f"{label}: expected {expected!r}, got {got!r}")

    check("count_by", count_by([{"c": "DE"}, {"c": "NL"}, {"c": "DE"}, {"c": ""}, {}], "c"), {"DE": 2, "NL": 1})
    check("group_by", group_by([{"o": "lena", "n": 1}, {"o": "tom", "n": 2}, {"o": "lena", "n": 3}], "o"),
          {"lena": [{"o": "lena", "n": 1}, {"o": "lena", "n": 3}], "tom": [{"o": "tom", "n": 2}]})
    check("batches", batches([1, 2, 3, 4, 5], 2), [[1, 2], [3, 4], [5]])
    check("batches 23/10", [len(b) for b in batches(list(range(23)), 10)], [10, 10, 3])
    check("batches empty", batches([], 3), [])
    check("new_vs_existing", new_vs_existing(["a.de", "b.de", "a.de"], ["b.de", "c.de"]), (["a.de"], ["b.de"]))
    check("filled_count", filled_count({"a": "x", "b": "", "c": None, "d": " ", "e": 0}), 2)
    rows = [
        {"domain": "peopleco.de", "name": "Peopleco", "employees": ""},
        {"domain": "opal.de", "name": "Opal", "employees": "25"},
        {"domain": "peopleco.de", "name": "PeopleCo GmbH", "employees": "120"},
        {"domain": "", "name": "No domain", "employees": "5"},
        {"domain": "opal.de", "name": "Opal Analytics", "employees": "25"},
    ]
    result = dedupe_keep_most_complete(rows, "domain")
    check("dedupe count", len(result), 2)
    check("dedupe order", [r["domain"] for r in result], ["peopleco.de", "opal.de"])
    check("dedupe keeps complete", result[0]["name"] if result else None, "PeopleCo GmbH")
    check("dedupe tie keeps first", result[1]["name"] if len(result) > 1 else None, "Opal")
    return failures


if __name__ == "__main__":
    try:
        problems = _checks()
    except NotImplementedError:
        print("Some functions still raise NotImplementedError. Fill them in and run again.")
    else:
        print("\n".join(problems) if problems else "All checks passed")
