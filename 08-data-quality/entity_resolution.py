"""
Data quality in code: keys, fuzzy matching, survivorship and an enrichment waterfall
===================================================================================

Run me:  python 08-data-quality/entity_resolution.py
Standard library only (difflib), so nothing to install.
"""
from difflib import SequenceMatcher

LEGAL_SUFFIXES = {"gmbh", "ag", "bv", "b.v.", "ltd", "inc", "sa", "se", "technologies", "tech", "group"}

records = [
    {"source": "crm", "name": "Nordbank Tech B.V.", "domain": "nordbanktech.nl", "country": "NL",
     "employees": None, "owner": "tom", "updated_at": "2026-11-18"},
    {"source": "apollo", "name": "Nordbank Technologies", "domain": "", "country": "NL",
     "employees": 85, "owner": None, "updated_at": "2026-11-21"},
    {"source": "webinar", "name": "NORDBANK TECH", "domain": "nordbanktech.nl", "country": "NL",
     "employees": 80, "owner": None, "updated_at": "2026-11-20"},
    {"source": "apollo", "name": "Nordic Bank Solutions", "domain": "nordicbank.no", "country": "NO",
     "employees": 300, "owner": None, "updated_at": "2026-11-19"},
    {"source": "crm", "name": "PeopleCo GmbH", "domain": "peopleco.de", "country": "DE",
     "employees": 120, "owner": "lena", "updated_at": "2026-11-20"},
    {"source": "clay", "name": "Nordbanc Tech", "domain": "", "country": "NL",
     "employees": 15, "owner": None, "updated_at": "2026-11-22"},       # a typo, or a different company?
]


def name_key(name):
    words = [w for w in name.lower().replace(",", " ").split() if w not in LEGAL_SUFFIXES]
    return " ".join(words)


def similarity(a, b):
    return SequenceMatcher(None, name_key(a), name_key(b)).ratio()     # 0.0 .. 1.0


print("=== 1. Name keys (normalised for matching) ===")
for r in records:
    print(f"{r['name']!r:28} -> {name_key(r['name'])!r}")

print("\n=== 2. Fuzzy similarity between names ===")
pairs = [("Nordbank Tech B.V.", "Nordbank Technologies"), ("Nordbank Tech B.V.", "NORDBANK TECH"),
         ("Nordbank Tech B.V.", "Nordic Bank Solutions"), ("PeopleCo GmbH", "Nordbank Tech B.V.")]
for a, b in pairs:
    print(f"{a!r:22} vs {b!r:26} -> {similarity(a, b):.2f}")

print("\n=== 3. Matching rule: domain first; else fuzzy name + same country ===")
AUTO_MERGE, REVIEW = 0.90, 0.75


def match_decision(a, b):
    if a["domain"] and a["domain"] == b["domain"]:
        return "same company (domain match)"
    score = similarity(a["name"], b["name"])
    if a["country"] != b["country"]:
        return f"different (countries differ, name sim {score:.2f})"
    if score >= AUTO_MERGE:
        return f"same company (name sim {score:.2f})"
    if score >= REVIEW:
        return f"HUMAN REVIEW (name sim {score:.2f})"
    return f"different (name sim {score:.2f})"


base = records[0]
for other in records[1:]:
    print(f"{base['name']} vs {other['name']}: {match_decision(base, other)}")
# A wrong merge mixes two customers' data, which is worse than a duplicate. Borderline -> a person checks.

print("\n=== 4. Survivorship: build the golden record field by field ===")
group = records[:3]                                   # the three Nordbank records
SOURCE_TRUST = {"crm": 3, "apollo": 2, "webinar": 1}  # higher wins


def pick(field, rule):
    candidates = [r for r in group if r.get(field) not in (None, "")]
    if not candidates:
        return None
    if rule == "most_trusted":
        return max(candidates, key=lambda r: SOURCE_TRUST[r["source"]])[field]
    if rule == "most_recent":
        return max(candidates, key=lambda r: r["updated_at"])[field]
    raise ValueError(rule)


golden = {
    "name": pick("name", "most_trusted"),           # CRM name (a human may have corrected it)
    "domain": pick("domain", "most_trusted"),
    "owner": pick("owner", "most_trusted"),         # never lose the existing owner
    "employees": pick("employees", "most_recent"),  # freshest number
    "country": pick("country", "most_trusted"),
}
print(golden)

print("\n=== 5. Enrichment waterfall: try providers in order, field by field ===")


def provider_a(domain):
    return {"employees": None, "industry": "Fintech"}           # has industry, not size


def provider_b(domain):
    return {"employees": 82, "industry": "Financial Services"}  # has both


def provider_c(domain):
    raise TimeoutError("provider C is down")


def waterfall(domain, fields, providers):
    found, sources = {}, {}
    for provider in providers:
        missing = [f for f in fields if f not in found]
        if not missing:
            break
        try:
            data = provider(domain) or {}
        except Exception as e:                      # one provider failing must not stop the rest
            print(f"  {provider.__name__} failed: {e}")
            continue
        for f in missing:
            if data.get(f) not in (None, ""):
                found[f], sources[f] = data[f], provider.__name__
    return found, sources


values, sources = waterfall("nordbanktech.nl", ["industry", "employees", "funding"],
                            [provider_a, provider_c, provider_b])
print("values:", values)
print("sources:", sources)      # record WHERE each value came from
print("still missing:", [f for f in ["industry", "employees", "funding"] if f not in values])

print("\n=== 6. Fill gaps only: merge enrichment into the CRM record ===")
crm_record = {"name": "Nordbank Tech B.V.", "industry": "Fintech", "employees": None, "owner": "tom"}
merged = {**crm_record, **{k: v for k, v in values.items() if crm_record.get(k) in (None, "")}}
print(merged)   # industry kept from CRM; employees filled from the provider; owner untouched

# ---------------------------------------------------------------------------
# TRY IT
# 1. Lower REVIEW to 0.5. What new matches appear, and are they right?
# 2. Change SOURCE_TRUST so apollo beats crm. What happens to `name`? Why is that risky?
# 3. Add a provider that returns "funding": "Series A" and put it last.
# ---------------------------------------------------------------------------
