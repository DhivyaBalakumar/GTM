"""
Lesson 9: errors and debugging
==============================

Run me:  python 03-python/lessons/09_errors_and_debugging.py

Real data is messy and real APIs fail. Good GTM code:
  * handles EXPECTED problems (a bad value in one row) and keeps going
  * fails LOUDLY on serious problems (bad API key) with a clear message
  * never hides errors silently
"""
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger("lesson9")

print("=== 1. try / except: handle an error instead of crashing ===")
for raw in ["120", "51-200", "abc", None]:
    try:
        n = int(raw)
        print(repr(raw), "->", n)
    except ValueError:
        print(repr(raw), "-> ValueError: not a whole number")
    except TypeError:
        print(repr(raw), "-> TypeError: None can't be converted")

print("\n=== 2. Catch SPECIFIC errors, not everything ===")
# `except Exception:` catches almost everything, including bugs you WANT to see.
# Use specific types where you can; use broad catches only at the top of a loop, and LOG them.

print("\n=== 3. else and finally ===")
try:
    value = int("45")
except ValueError:
    print("bad")
else:
    print("no error, value =", value)      # runs only if nothing failed
finally:
    print("finally always runs (close files, release things)")

print("\n=== 4. One bad record must not stop the run ===")
rows = [{"domain": "peopleco.de", "employees": "120"},
        {"domain": "bad.io", "employees": "abc"},
        {"domain": "opal.de", "employees": "25"}]
ok, failed = [], []
for row in rows:
    try:
        row["employees"] = int(row["employees"])
        ok.append(row)
    except ValueError as e:
        failed.append(row["domain"])
        log.warning("Skipping %s: %s", row["domain"], e)    # log the reason
print("ok:", [r["domain"] for r in ok], "| failed:", failed)

print("\n=== 5. raise: signal a problem yourself ===")


def require_key(key):
    if not key:
        raise ValueError("HUBSPOT_TOKEN is missing. Add it to your .env file.")
    return key


try:
    require_key("")
except ValueError as e:
    print("caught:", e)

print("\n=== 6. Common errors and their usual cause ===")
examples = {
    "KeyError": lambda: {"a": 1}["b"],           # key not in dict -> use .get()
    "IndexError": lambda: [1, 2][5],             # position past the end
    "TypeError": lambda: "120" + 5,              # mixing types
    "ValueError": lambda: int("abc"),            # right type, bad value
    "AttributeError": lambda: None.lower(),      # calling a method on None
    "ZeroDivisionError": lambda: 1 / 0,          # dividing by zero (e.g. a rate with 0 leads)
}
for name, fn in examples.items():
    try:
        fn()
    except Exception as e:
        print(f"{name:18} -> {type(e).__name__}: {e}")
# NameError: you used a variable that doesn't exist (often a typo).
# FileNotFoundError: wrong path, or running from the wrong folder.
# ModuleNotFoundError: package not installed, or the venv isn't active.

print("\n=== 7. Reading a traceback ===")
print("""
Traceback (most recent call last):
  File "run.py", line 12, in <module>
    total = count_leads(rows)
  File "run.py", line 5, in count_leads
    return rows["count"]
TypeError: list indices must be integers or slices, not str

How to read it:
  1. Read the LAST line first: the error type and message.
  2. Look just above it: the file and line where it happened (line 5).
  3. Ask: what did Python expect, and what did it get? (expected a number index, got "count";
     rows is a list, not a dict)
""")

print("=== 8. The debugging routine (say it out loud in live coding) ===")
print("""
  1. Reproduce: run it and see the error.
  2. Read the error: last line, then the line number.
  3. Guess the cause.
  4. Check the guess: print(type(x), x) or use the debugger.
  5. Fix, re-run, and test the edge case that caused it.
""")

print("=== 9. assert: check your assumptions ===")
scores = [95, 80, 35]
assert all(0 <= s <= 100 for s in scores), "scores must be 0-100"
print("assert passed")

# ---------------------------------------------------------------------------
# TRY IT
# 1. Write safe_int(value, default=None) that returns default instead of raising.
# 2. Make the loop in section 4 also handle a missing "employees" key (KeyError).
# 3. Break something on purpose in lesson 7 and practise reading the traceback.
# ---------------------------------------------------------------------------
