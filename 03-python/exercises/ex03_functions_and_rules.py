"""
Exercise 3: functions and business rules
========================================

Fill in each function, then run:
    python 03-python/exercises/ex03_functions_and_rules.py
"""
from itertools import cycle

TARGET_INDUSTRIES = {"software", "saas", "fintech", "healthtech", "health tech"}
TARGET_COUNTRIES = {"DE", "AT", "CH", "NL", "BE", "LU"}


def parse_employees(value):
    """Employee text -> int or None.

    "120" -> 120;  " 45 " -> 45;  "51-200" -> 125 (midpoint, rounded down);
    "abc", "", None -> None;  80 (already an int) -> 80
    """
    raise NotImplementedError


def segment(employees):
    """None -> "Unknown"; < 20 -> "Small"; 20-499 -> "Mid-market"; >= 500 -> "Enterprise"."""
    raise NotImplementedError


def score_lead(lead):
    """Return (score, tier, reasons).

    +25 if lead["industry"] (case-insensitive) is in TARGET_INDUSTRIES
    +20 if employees (use parse_employees) is between 20 and 500 inclusive
    +15 if lead["country"] is in TARGET_COUNTRIES
    +20 if lead.get("raised_recently") is True
    +20 if lead.get("hiring_security") is True
    tier: "A" if score >= 75, "B" if >= 50, else "C"
    reasons: a list with one short string per rule that added points (any wording)
    Missing keys must not crash.
    """
    raise NotImplementedError


def make_router(dach_reps, other_reps, fallback="head-of-sales"):
    """Return a function route(lead, existing_owner=None) -> (owner, reason).

    Rules in order:
      1. existing_owner given -> (existing_owner, "existing owner")
      2. lead tier "C" -> ("nurture-queue", "tier C")
      3. country in DE/AT/CH -> next DACH rep in round-robin, "DACH round-robin"
      4. any other non-empty country -> next other rep, "general round-robin"
      5. otherwise -> (fallback, "fallback")
    Hint: create cycle() objects inside make_router, and define route inside it.
    """
    raise NotImplementedError


# --------------------------------------------------------------------------- checks
def _checks():
    failures = []

    def check(label, got, expected):
        if got != expected:
            failures.append(f"{label}: expected {expected!r}, got {got!r}")

    for raw, want in [("120", 120), (" 45 ", 45), ("51-200", 125), ("abc", None), ("", None), (None, None), (80, 80)]:
        check(f"parse_employees({raw!r})", parse_employees(raw), want)
    for n, want in [(None, "Unknown"), (5, "Small"), (19, "Small"), (20, "Mid-market"), (499, "Mid-market"), (500, "Enterprise")]:
        check(f"segment({n})", segment(n), want)

    hot = {"industry": "Software", "employees": "120", "country": "DE", "raised_recently": True, "hiring_security": True}
    s, t, r = score_lead(hot)
    check("score hot", (s, t), (100, "A"))
    check("reasons count", len(r), 5)
    check("score boundary 20", score_lead({"industry": "SaaS", "employees": "20", "country": "NL"})[:2], (60, "B"))
    check("score boundary 19", score_lead({"industry": "SaaS", "employees": "19", "country": "NL"})[:2], (40, "C"))
    check("score empty", score_lead({})[:2], (0, "C"))

    route = make_router(["lena", "jonas"], ["maria", "tom"])
    check("existing owner", route({"country": "DE", "tier": "A"}, existing_owner="tom"), ("tom", "existing owner"))
    check("tier C", route({"country": "DE", "tier": "C"}), ("nurture-queue", "tier C"))
    check("dach 1", route({"country": "AT", "tier": "A"})[0], "lena")
    check("dach 2", route({"country": "CH", "tier": "B"})[0], "jonas")
    check("dach 3", route({"country": "DE", "tier": "A"})[0], "lena")
    check("other", route({"country": "FR", "tier": "A"}), ("maria", "general round-robin"))
    check("fallback", route({"country": "", "tier": "A"}), ("head-of-sales", "fallback"))
    return failures


if __name__ == "__main__":
    try:
        problems = _checks()
    except NotImplementedError:
        print("Some functions still raise NotImplementedError. Fill them in and run again.")
    else:
        print("\n".join(problems) if problems else "All checks passed")
