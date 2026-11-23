"""
Lesson 5: conditions (if / elif / else)
=======================================

Run me:  python 03-python/lessons/05_conditions.py

Business rules (scoring, routing, filtering) are just conditions written in code.
Indentation (4 spaces) shows which lines belong to which branch.
"""

print("=== 1. if / elif / else ===")
employees = 120
if employees >= 500:
    segment = "Enterprise"
elif employees >= 20:          # checked only if the first was False
    segment = "Mid-market"
else:                          # everything else
    segment = "Small"
print(employees, "->", segment)

print("\n=== 2. Combining conditions: and, or, not ===")
country, industry = "DE", "Software"
if country in {"DE", "AT", "CH"} and industry == "Software":
    print("DACH software company")
if country == "FR" or country == "ES":
    print("Southern Europe")
if not industry:
    print("industry missing")
else:
    print("industry present")

print("\n=== 3. Ranges read naturally ===")
print("20 <= 120 <= 500:", 20 <= employees <= 500)

print("\n=== 4. Checking membership with `in` ===")
PERSONAL_DOMAINS = {"gmail.com", "yahoo.com", "outlook.com", "hotmail.com"}
email = "max.fischer@gmail.com"
domain = email.split("@")[-1]
if domain in PERSONAL_DOMAINS:
    print(email, "-> personal email, not a company lead")

print("\n=== 5. Order matters: the FIRST matching branch wins ===")
score = 80
# Wrong order: 80 >= 50 matches first, so it never reaches the A check.
if score >= 50:
    wrong = "B"
elif score >= 75:
    wrong = "A"
else:
    wrong = "C"
# Right order: most specific first.
if score >= 75:
    right = "A"
elif score >= 50:
    right = "B"
else:
    right = "C"
print("wrong order gives", wrong, "| right order gives", right)

print("\n=== 6. Boundaries: > vs >= (a classic bug) ===")
for n in [19, 20, 21]:
    buggy = "Mid-market" if n > 20 else "Small"
    fixed = "Mid-market" if n >= 20 else "Small"
    print(f"{n}: buggy={buggy:10} fixed={fixed}")
# The rule said "20-500 employees", so 20 must be Mid-market. Always test the boundary.

print("\n=== 7. One-line if (conditional expression) ===")
tier = "A" if score >= 75 else "B" if score >= 50 else "C"
print("tier:", tier)

print("\n=== 8. Handling missing values before comparing ===")
for raw in [120, None, 0]:
    # `raw >= 20` would crash on None. Check first:
    if raw is None:
        print(raw, "-> unknown size (needs enrichment)")
    elif raw >= 20:
        print(raw, "-> in range")
    else:
        print(raw, "-> too small")

print("\n=== 9. A real scoring rule set, with reasons ===")
lead = {"industry": "Software", "employees": 120, "country": "DE",
        "raised_recently": True, "hiring_security": False}
points, reasons = 0, []
if lead["industry"] in {"Software", "Fintech", "Healthtech"}:
    points += 25
    reasons.append("target industry")
if lead["employees"] and 20 <= lead["employees"] <= 500:
    points += 20
    reasons.append(f"{lead['employees']} employees")
if lead["country"] in {"DE", "AT", "CH", "NL", "BE", "LU"}:
    points += 15
    reasons.append(f"in {lead['country']}")
if lead["raised_recently"]:
    points += 20
    reasons.append("raised funding recently")
if lead["hiring_security"]:
    points += 20
    reasons.append("hiring for security")
print(points, reasons)

print("\n=== 10. match/case (Python 3.10+): clean multi-way choices ===")
stage = "demo_booked"
match stage:
    case "demo_booked":
        action = "alert the AE"
    case "closed_won":
        action = "notify customer success"
    case _:                       # _ means "anything else"
        action = "log only"
print(stage, "->", action)

# ---------------------------------------------------------------------------
# TRY IT
# 1. Add a rule: -30 points if industry == "Retail". Re-run with Retail.
# 2. Write the condition: country is DE and (employees >= 50 or raised_recently).
# 3. What does `if lead["employees"] and ...` protect against?
# ---------------------------------------------------------------------------
