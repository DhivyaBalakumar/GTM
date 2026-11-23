"""
Lesson 7: functions
===================

Run me:  python 03-python/lessons/07_functions.py

A FUNCTION is a reusable machine: inputs (parameters) in, result (return value) out.
Good GTM code is many small, well-named functions: normalize_domain, score, route...
"""

print("=== 1. Defining and calling ===")


def greet(name):
    return f"Hello, {name}"


message = greet("Anna")    # call it; the returned value goes into `message`
print(message)

print("\n=== 2. return vs print ===")


def add_print(a, b):
    print(a + b)           # shows it, but gives nothing back (returns None)


def add_return(a, b):
    return a + b           # gives the value back so you can use it


x = add_print(2, 3)
y = add_return(2, 3)
print("add_print returned:", x, "| add_return returned:", y)
# Almost always: RETURN values, and print only at the edges of your program.

print("\n=== 3. Several parameters, defaults, keyword arguments ===")


def segment(employees, small_max=19, enterprise_min=500):
    if employees is None:
        return "Unknown"
    if employees >= enterprise_min:
        return "Enterprise"
    if employees > small_max:
        return "Mid-market"
    return "Small"


print(segment(120))                         # uses the defaults
print(segment(120, enterprise_min=100))     # override one by name (keyword argument)
print(segment(None))

print("\n=== 4. Returning several values (a tuple) ===")


def route(country, existing_owner=None):
    if existing_owner:
        return existing_owner, "existing owner"
    if country in {"DE", "AT", "CH"}:
        return "lena", "DACH team"
    return "maria", "general team"


owner, reason = route("AT")
print(owner, "|", reason)
print(route("NL", existing_owner="tom"))

print("\n=== 5. Docstrings and type hints (good habits) ===")


def fit_points(industry: str, employees: int | None) -> int:
    """Return 0-45 fit points for industry and company size."""
    points = 0
    if industry in {"Software", "Fintech", "Healthtech"}:
        points += 25
    if employees is not None and 20 <= employees <= 500:
        points += 20
    return points


print(fit_points("Software", 120), fit_points("Retail", 5))
print("docstring:", fit_points.__doc__)   # help(fit_points) shows it too
# Type hints (str, int | None, -> int) don't change behaviour; they document intent and help
# your editor catch mistakes.

print("\n=== 6. Pure functions: easy to test ===")
# A PURE function uses only its inputs and returns a result: no printing, no files, no API calls.
# normalize_domain(), fit_points() and segment() are pure, so you can test them with one line:
assert segment(20) == "Mid-market"
assert segment(19) == "Small"
assert fit_points("Software", 120) == 45
print("all asserts passed")
# Keep side effects (reading files, calling APIs, writing to the CRM) in a few separate functions.

print("\n=== 7. Scope: variables inside a function stay inside ===")
total = 100


def change_total():
    total = 5          # a NEW local variable; the outer `total` is untouched
    return total


print(change_total(), total)   # 5 100
# Don't rely on global variables inside functions; pass values in and return results.

print("\n=== 8. Functions calling functions: building a pipeline ===")


def clean(lead):
    lead = dict(lead)                                  # copy, don't change the caller's dict
    lead["country"] = (lead.get("country") or "").strip().upper()
    return lead


def score(lead):
    return fit_points(lead.get("industry"), lead.get("employees"))


def process(lead):
    cleaned = clean(lead)
    cleaned["score"] = score(cleaned)
    cleaned["owner"], cleaned["route_reason"] = route(cleaned["country"])
    return cleaned


print(process({"name": "PeopleCo", "industry": "Software", "employees": 120, "country": " de "}))

print("\n=== 9. Functions are values (used with sorted, map, apply) ===")


def by_score(lead):
    return lead["score"]


rows = [{"name": "A", "score": 40}, {"name": "B", "score": 90}]
print(sorted(rows, key=by_score, reverse=True))   # pass the function itself, no ()

print("\n=== 10. *args and **kwargs (awareness) ===")


def log(message, *args, **kwargs):
    print("LOG:", message, args, kwargs)


log("upsert", 10, 20, dry_run=True)
# *args collects extra positional values into a tuple; **kwargs collects named ones into a dict.

# ---------------------------------------------------------------------------
# TRY IT
# 1. Write tier(score) returning "A" (>=75), "B" (>=50) or "C", with three asserts.
# 2. Add a `country_points` function and use it inside score().
# 3. Remove the `return` from add_return. What does y become?
# ---------------------------------------------------------------------------
