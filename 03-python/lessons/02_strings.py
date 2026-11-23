"""
Lesson 2: strings (cleaning text)
=================================

Run me:  python 03-python/lessons/02_strings.py

Half of GTM data work is cleaning text: domains, emails, company names, countries,
industries. Strings have built-in METHODS (tools) you call with a dot: text.lower()

Strings are IMMUTABLE: methods return a NEW string; the original is unchanged.
So you must save the result:  name = name.strip()
"""

print("=== 1. The most-used methods ===")
raw = "   PeopleCo GmbH   "
print(repr(raw.strip()))           # remove spaces at both ends
print(repr(raw.lower()))           # lowercase
print(repr(raw.upper()))           # uppercase
print(repr(raw.strip().title()))   # Title Case
print(raw.strip().replace("GmbH", "").strip())   # replace text, then tidy

print("\n=== 2. Chaining: each method works on the previous result ===")
website = "  HTTPS://www.PeopleCo.de/about  "
clean = website.strip().lower().replace("https://", "").replace("http://", "").replace("www.", "")
print(clean)                  # peopleco.de/about
print(clean.split("/")[0])    # peopleco.de   (split then take the first part)

print("\n=== 3. split and join ===")
email = "anna@peopleco.de"
parts = email.split("@")      # -> ['anna', 'peopleco.de']
print(parts, "-> domain:", parts[1])
print("first.last@x.de".split("@")[0].split("."))   # ['first', 'last']
tags = ["software", "dach", "series-a"]
print(", ".join(tags))        # join a list into one string

print("\n=== 4. Checking text ===")
print("@" in email)                       # contains?
print(email.endswith(".de"))              # ends with?
print("https://x.io".startswith("http"))  # starts with?
print("abc".isdigit(), "120".isdigit())   # only digits?
print("Head of IT".find("IT"))            # position of a substring (-1 if missing)

print("\n=== 5. f-strings: put values into text ===")
company, employees, score = "PeopleCo", 120, 87.456
print(f"{company} has {employees} employees and a score of {score:.1f}")
print(f"{'Name':<12}|{'Score':>6}")        # align left/right in 12/6 characters
print(f"{company:<12}|{score:>6.1f}")

print("\n=== 6. Indexing and slicing ===")
s = "peopleco.de"
print(s[0], s[-1], s[0:8], s[-3:])   # first char, last char, chars 0-7, last 3
# A slice [start:end] includes start, excludes end.

print("\n=== 7. A real cleaning function (you'll write this many times) ===")


def normalize_domain(value):
    """Turn a website or email into a bare domain like 'peopleco.de'."""
    if not value:                    # None or "" -> nothing to clean
        return ""
    v = str(value).strip().lower()
    if "@" in v:                     # an email: keep what's after @
        v = v.split("@")[-1]
    for prefix in ("https://", "http://", "www."):
        if v.startswith(prefix):
            v = v[len(prefix):]
    return v.split("/")[0]           # drop any path like /about


for value in ["https://www.PeopleCo.de/about", "peopleco.de", "anna@PeopleCo.de",
              "www.brightforge.io", "", None]:
    print(repr(value), "->", repr(normalize_domain(value)))

print("\n=== 8. Normalising company names for matching ===")
SUFFIXES = [" gmbh", " ag", " b.v.", " bv", " ltd", " inc", " sa"]


def company_key(name):
    """'PeopleCo GmbH' and 'peopleco' should give the same key."""
    if not name:
        return ""
    key = name.strip().lower()
    for suffix in SUFFIXES:
        if key.endswith(suffix):
            key = key[: -len(suffix)]
    return key.strip()


for name in ["PeopleCo GmbH", "Peopleco", "Nordbank Tech B.V.", "Nordbank Tech", "Alpenwerk AG"]:
    print(f"{name!r:24} -> {company_key(name)!r}")

print("\n=== 9. Special characters ===")
print("Müller".lower(), "Müller".casefold())   # casefold is stronger for matching
print("Line 1\nLine 2")    # \n = new line
print("Tab\there")         # \t = tab
print(r"C:\new\folder")    # r"" = raw string: backslashes are literal (Windows paths, regex)

# ---------------------------------------------------------------------------
# TRY IT
# 1. Make normalize_domain also strip a trailing dot: "peopleco.de." -> "peopleco.de"
# 2. Print f"{0.8734:.0%}". What does the % format do?
# 3. Why does "PeopleCo".lower() == "peopleco" matter when deduplicating?
# ---------------------------------------------------------------------------
