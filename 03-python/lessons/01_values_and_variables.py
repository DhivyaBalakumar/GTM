"""
Lesson 1: values, variables and types
=====================================

Run me:  python 03-python/lessons/01_values_and_variables.py

A VARIABLE is a labelled box that holds a value. You create one with `=`.
Python reads this file top to bottom, one line at a time.
"""

print("=== 1. Variables ===")
company = "PeopleCo GmbH"      # text  -> str
employees = 120                # whole number -> int
score = 87.5                   # decimal -> float
is_customer = False            # True/False -> bool
owner = None                   # "nothing / missing" -> NoneType

print(company, employees, score, is_customer, owner)

# A variable can be reassigned. The old value is simply replaced.
employees = 125
print("employees is now", employees)

print("\n=== 2. Types ===")
# type() tells you what kind of value something is.
print(type(company), type(employees), type(score), type(is_customer), type(owner))

print("\n=== 3. Why types matter: data from files arrives as TEXT ===")
# A CSV gives you "120" (a string), not 120 (a number).
employees_from_csv = "120"
print("'120' + '5'   =", employees_from_csv + "5")       # joins text: '1205'
print("int('120') + 5 =", int(employees_from_csv) + 5)   # maths: 125

# Comparing text and numbers is a classic bug:
# "120" >= 20  -> TypeError: '>=' not supported between 'str' and 'int'
print("int('120') >= 20 is", int(employees_from_csv) >= 20)

print("\n=== 4. Converting between types ===")
print(int("45"), float("72.5"), str(45), bool(1), bool(0))
print(int(72.9))          # int() cuts off decimals: 72 (it does NOT round)
print(round(72.9))        # round() rounds: 73
print(round(72.456, 1))   # one decimal: 72.5

# Some conversions fail. "abc" is not a number:
#   int("abc")  -> ValueError: invalid literal for int() with base 10: 'abc'
# Lesson 9 shows how to handle that with try/except.

print("\n=== 5. Maths operators ===")
print("10 + 3 =", 10 + 3)
print("10 - 3 =", 10 - 3)
print("10 * 3 =", 10 * 3)
print("10 / 3 =", 10 / 3)     # always a float
print("10 // 3 =", 10 // 3)   # whole-number division
print("10 % 3 =", 10 % 3)     # remainder (useful for 'every 3rd item')
print("2 ** 3 =", 2 ** 3)     # power: used in exponential backoff (2, 4, 8, 16 seconds)

print("\n=== 6. Comparisons give True/False ===")
print("120 >= 20:", 120 >= 20)
print("120 == 120:", 120 == 120)   # == compares; = assigns
print("'DE' != 'NL':", "DE" != "NL")

print("\n=== 7. None means 'missing' ===")
industry = None
print("industry is None:", industry is None)   # use `is None`, not `== None`

print("\n=== 8. Truthiness: what counts as False ===")
# In an `if`, these all behave like False: None, 0, 0.0, "", [], {}, set()
# Everything else behaves like True.
for value in [None, 0, "", [], {}, "x", 5, [1]]:
    print(repr(value), "->", bool(value))

# This is why `if not website:` catches None AND "" in one check.
website = ""
if not website:
    print("website is missing (None or empty)")

print("\n=== 9. Naming rules ===")
# Use lower_case_with_underscores, descriptive names.
#   good: employee_count, fit_score, contact_email
#   bad:  x, n2, data1
# Constants (values that never change) are written in CAPITALS by convention:
TIER_A_THRESHOLD = 75
print("Tier A starts at", TIER_A_THRESHOLD)

# ---------------------------------------------------------------------------
# TRY IT
# 1. Change employees_from_csv to "abc" and run. Read the error's last line.
# 2. What is bool("False")? Predict, then check. (Hint: it's a non-empty string.)
# 3. Calculate the wait times 2**1, 2**2, 2**3, 2**4 for a retry loop.
# ---------------------------------------------------------------------------
