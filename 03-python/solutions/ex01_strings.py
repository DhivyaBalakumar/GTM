"""Solution to exercise 1. Compare with yours: different code can be equally correct."""

PERSONAL_DOMAINS = {"gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "icloud.com", "web.de", "gmx.de"}

COUNTRY_CODES = {
    "de": "DE", "germany": "DE", "deutschland": "DE",
    "at": "AT", "austria": "AT",
    "ch": "CH", "switzerland": "CH",
    "nl": "NL", "netherlands": "NL", "the netherlands": "NL",
    "be": "BE", "belgium": "BE",
    "lu": "LU", "luxembourg": "LU",
    "fr": "FR", "france": "FR",
    "es": "ES", "spain": "ES",
    "uk": "GB", "gb": "GB", "united kingdom": "GB",
    "us": "US", "usa": "US", "united states": "US",
    "no": "NO", "norway": "NO",
}

SUFFIXES = ("gmbh", "ag", "b.v.", "bv", "ltd", "inc", "sa", "se")


def normalize_domain(value):
    if not value:
        return ""
    v = str(value).strip().lower()
    if "@" in v:
        v = v.split("@")[-1]
    for prefix in ("https://", "http://", "www."):
        if v.startswith(prefix):
            v = v[len(prefix):]
    return v.split("/")[0].strip()


def email_domain(email):
    if not email or email.count("@") != 1:
        return ""
    return email.split("@")[1].strip().lower()


def is_personal_email(email):
    return email_domain(email) in PERSONAL_DOMAINS


def company_key(name):
    if not name:
        return ""
    words = name.strip().lower().split()      # split() with no argument also collapses spaces
    if words and words[-1] in SUFFIXES:
        words = words[:-1]
    return " ".join(words)


def clean_country(value):
    if not value:
        return ""
    return COUNTRY_CODES.get(value.strip().lower(), "")


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
    problems = _checks()
    print("\n".join(problems) if problems else "All checks passed")
