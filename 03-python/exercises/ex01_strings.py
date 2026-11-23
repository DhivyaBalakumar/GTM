"""
Exercise 1: cleaning text
=========================

Fill in each function (replace `raise NotImplementedError`), then run:
    python 03-python/exercises/ex01_strings.py

The checks at the bottom tell you exactly what's wrong. Don't look at solutions/ until
you've tried for at least 15 minutes per function.
"""

PERSONAL_DOMAINS = {"gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "icloud.com", "web.de", "gmx.de"}


def normalize_domain(value):
    """Website or email -> bare lowercase domain.

    "https://www.PeopleCo.de/about" -> "peopleco.de"
    "anna@PeopleCo.de"              -> "peopleco.de"
    "  brightforge.io  "            -> "brightforge.io"
    "", None                        -> ""
    """
    raise NotImplementedError


def email_domain(email):
    """"anna@peopleco.de" -> "peopleco.de"; anything without exactly one @ -> ""."""
    raise NotImplementedError


def is_personal_email(email):
    """True if the email's domain is in PERSONAL_DOMAINS (case-insensitive)."""
    raise NotImplementedError


def company_key(name):
    """Name -> matching key: lowercase, trimmed, legal suffix removed, inner spaces collapsed.

    "PeopleCo GmbH" -> "peopleco"; "Nordbank Tech B.V." -> "nordbank tech";
    "  Alpenwerk   AG " -> "alpenwerk"; None -> ""
    Suffixes to remove: gmbh, ag, b.v., bv, ltd, inc, sa, se
    """
    raise NotImplementedError


def clean_country(value):
    """Country name or code -> 2-letter uppercase code.

    "DE", "de", "Germany", " germany " -> "DE"
    "Netherlands" -> "NL", "Austria" -> "AT", "Switzerland" -> "CH"
    Unknown or empty -> ""   (Hint: a dictionary of names -> codes.)
    """
    raise NotImplementedError


# --------------------------------------------------------------------------- checks
def _checks():
    failures = []

    def check(label, got, expected):
        if got != expected:
            failures.append(f"{label}: expected {expected!r}, got {got!r}")

    check("domain url", normalize_domain("https://www.PeopleCo.de/about"), "peopleco.de")
    check("domain email", normalize_domain("anna@PeopleCo.de"), "peopleco.de")
    check("domain spaces", normalize_domain("  brightforge.io  "), "brightforge.io")
    check("domain http", normalize_domain("http://nordbanktech.nl/"), "nordbanktech.nl")
    check("domain empty", normalize_domain(""), "")
    check("domain None", normalize_domain(None), "")
    check("email_domain", email_domain("anna@peopleco.de"), "peopleco.de")
    check("email_domain no @", email_domain("not-an-email"), "")
    check("email_domain two @", email_domain("a@b@c.de"), "")
    check("personal gmail", is_personal_email("Max.Fischer@GMAIL.com"), True)
    check("personal work", is_personal_email("anna@peopleco.de"), False)
    check("key gmbh", company_key("PeopleCo GmbH"), "peopleco")
    check("key bv", company_key("Nordbank Tech B.V."), "nordbank tech")
    check("key spaces", company_key("  Alpenwerk   AG "), "alpenwerk")
    check("key None", company_key(None), "")
    check("country code", clean_country("de"), "DE")
    check("country name", clean_country(" Germany "), "DE")
    check("country NL", clean_country("Netherlands"), "NL")
    check("country unknown", clean_country("Atlantis"), "")
    check("country empty", clean_country(""), "")
    return failures


if __name__ == "__main__":
    try:
        problems = _checks()
    except NotImplementedError:
        print("Some functions still raise NotImplementedError. Fill them in and run again.")
    else:
        print("\n".join(problems) if problems else "All checks passed")
