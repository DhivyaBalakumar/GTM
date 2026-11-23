"""Solution to exercise 2."""


def count_by(rows, field):
    counts = {}
    for row in rows:
        value = row.get(field)
        if not value:
            continue
        counts[value] = counts.get(value, 0) + 1
    return counts


def group_by(rows, field):
    groups = {}
    for row in rows:
        groups.setdefault(row.get(field), []).append(row)
    return groups


def batches(items, size):
    return [items[i:i + size] for i in range(0, len(items), size)]


def new_vs_existing(new_domains, crm_domains):
    new, crm = set(new_domains), set(crm_domains)
    return sorted(new - crm), sorted(new & crm)


def filled_count(row):
    count = 0
    for value in row.values():
        if value is None:
            continue
        if isinstance(value, str) and not value.strip():
            continue
        count += 1
    return count


def dedupe_keep_most_complete(rows, key_field):
    best = {}                       # key -> (filled, row); dicts keep insertion order
    for row in rows:
        key = row.get(key_field)
        if not key:
            continue
        filled = filled_count(row)
        if key not in best or filled > best[key][0]:   # ">" so ties keep the first
            best[key] = (filled, row)
    return [row for _, row in best.values()]


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
    problems = _checks()
    print("\n".join(problems) if problems else "All checks passed")
