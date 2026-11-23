"""Solution to exercise 3."""
from itertools import cycle

TARGET_INDUSTRIES = {"software", "saas", "fintech", "healthtech", "health tech"}
TARGET_COUNTRIES = {"DE", "AT", "CH", "NL", "BE", "LU"}


def parse_employees(value):
    if value is None:
        return None
    if isinstance(value, int):
        return value
    text = str(value).strip()
    if "-" in text:
        low, _, high = text.partition("-")
        if low.strip().isdigit() and high.strip().isdigit():
            return (int(low) + int(high)) // 2
        return None
    return int(text) if text.isdigit() else None


def segment(employees):
    if employees is None:
        return "Unknown"
    if employees >= 500:
        return "Enterprise"
    if employees >= 20:
        return "Mid-market"
    return "Small"


def score_lead(lead):
    score, reasons = 0, []
    industry = (lead.get("industry") or "").strip().lower()
    if industry in TARGET_INDUSTRIES:
        score += 25
        reasons.append(f"target industry ({industry})")
    employees = parse_employees(lead.get("employees"))
    if employees is not None and 20 <= employees <= 500:
        score += 20
        reasons.append(f"{employees} employees")
    if lead.get("country") in TARGET_COUNTRIES:
        score += 15
        reasons.append(f"based in {lead['country']}")
    if lead.get("raised_recently") is True:
        score += 20
        reasons.append("raised funding recently")
    if lead.get("hiring_security") is True:
        score += 20
        reasons.append("hiring for security/compliance")
    tier = "A" if score >= 75 else "B" if score >= 50 else "C"
    return score, tier, reasons


def make_router(dach_reps, other_reps, fallback="head-of-sales"):
    dach, other = cycle(dach_reps), cycle(other_reps)

    def route(lead, existing_owner=None):
        if existing_owner:
            return existing_owner, "existing owner"
        if lead.get("tier") == "C":
            return "nurture-queue", "tier C"
        if lead.get("country") in {"DE", "AT", "CH"}:
            return next(dach), "DACH round-robin"
        if lead.get("country"):
            return next(other), "general round-robin"
        return fallback, "fallback"

    return route


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
    problems = _checks()
    print("\n".join(problems) if problems else "All checks passed")
