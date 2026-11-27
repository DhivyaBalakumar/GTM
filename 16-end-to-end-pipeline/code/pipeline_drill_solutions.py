"""
Reference answers for pipeline_drill.py. Try the drill first; compare after.
Run me:  python 16-end-to-end-pipeline/code/pipeline_drill_solutions.py
"""
import re

COUNTRY_ALIASES = {"germany": "DE", "deutschland": "DE", "austria": "AT", "netherlands": "NL",
                   "switzerland": "CH", "united kingdom": "UK", "uk": "UK"}
PERSONAL = {"gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "gmx.de"}
ROLE = {"info", "sales", "hello", "contact", "admin", "support"}


# 1 --------------------------------------------------------------------------------------------
def normalise_country(value):
    if value is None or not str(value).strip():
        return None
    v = str(value).strip()
    if v.lower() in COUNTRY_ALIASES:
        return COUNTRY_ALIASES[v.lower()]
    if len(v) == 2 and v.isalpha():
        return v.upper()
    return None


# 2 --------------------------------------------------------------------------------------------
def parse_employees(value):
    if value is None:
        return None
    s = str(value).replace(",", "").strip()
    if s.isdigit():
        return int(s)
    m = re.fullmatch(r"(\d+)\s*-\s*(\d+)", s)
    if m:
        return (int(m.group(1)) + int(m.group(2))) // 2
    m = re.fullmatch(r"(\d+)\+", s)
    if m:
        return int(m.group(1))
    return None


# 3 --------------------------------------------------------------------------------------------
def classify_seniority(title):
    t = (title or "").lower()
    if not t.strip():
        return None
    if any(w in t for w in ("intern", "student", "trainee")):
        return "junior"
    if re.search(r"\b(ceo|cto|coo|cfo|ciso|chief|founder)\b", t):
        return "c_level"
    if re.search(r"\b(vp|vice president|head of|director)\b", t):
        return "vp_head"
    if "manager" in t or "lead" in t:
        return "manager"
    return "ic"


# 4 --------------------------------------------------------------------------------------------
def email_kind(email):
    if not email or "@" not in email:
        return None
    local, domain = email.strip().lower().rsplit("@", 1)
    if domain in PERSONAL:
        return "personal"
    if local in ROLE:
        return "role"
    return "work"


# 5 --------------------------------------------------------------------------------------------
def survivorship(records, fields, priority):
    rank = {s: i for i, s in enumerate(priority)}
    ordered = sorted(records, key=lambda r: rank.get(r["source"], 99))
    golden, lineage = {}, {}
    for f in fields:
        golden[f] = None
        for r in ordered:
            if r.get(f) not in (None, ""):
                golden[f], lineage[f] = r[f], r["source"]
                break
    golden["lineage"] = lineage
    return golden


# 6 --------------------------------------------------------------------------------------------
def group_by_key(rows, key_fn):
    groups = {}
    for r in rows:
        k = key_fn(r)
        if not k:
            continue
        groups.setdefault(k, []).append(r)
    return groups


# 7 --------------------------------------------------------------------------------------------
def enrich_waterfall(domain, missing, providers, cache, budget):
    """providers: list of (name, cost, lookup_fn). Returns (filled_dict, credits_spent)."""
    filled, spent, missing = {}, 0, list(missing)
    for name, cost, lookup in providers:
        if not missing:
            break
        key = (name, domain)
        if key in cache:
            hit = cache[key]
        else:
            if spent + cost > budget:
                break
            hit = lookup(domain)
            cache[key] = hit
            if hit:
                spent += cost
        for f in list(missing):
            if hit and hit.get(f) not in (None, ""):
                filled[f] = hit[f]
                missing.remove(f)
    return filled, spent


# 8 --------------------------------------------------------------------------------------------
def first_match(rules, record, default=None):
    for test, result in rules:
        if test(record):
            return result
    return default


# 9 --------------------------------------------------------------------------------------------
def score_with_reasons(record, rules, tiers):
    """rules: list of (points, reason, test). tiers: [(floor, name)] high to low."""
    score, reasons = 0, []
    for points, reason, test in rules:
        if test(record):
            score += points
            reasons.append(reason)
    score = max(0, min(100, score))
    tier = next(name for floor, name in tiers if score >= floor)
    return score, tier, reasons


# 10 -------------------------------------------------------------------------------------------
def route(leads, existing_owner, reps):
    """leads: list of {"email","domain"}. existing_owner: {domain: rep}. reps: list.
    Returns {email: owner}; one owner per domain; round robin for new domains."""
    out, chosen, i = {}, dict(existing_owner), 0
    for lead in leads:
        d = lead["domain"]
        if d not in chosen:
            chosen[d] = reps[i % len(reps)]
            i += 1
        out[lead["email"]] = chosen[d]
    return out


# 11 -------------------------------------------------------------------------------------------
def build_payload(props, existing, human_owned, fill_if_empty):
    out = {}
    for k, v in props.items():
        if v is None or (isinstance(v, str) and not v.strip()):
            continue
        if k in human_owned and existing.get(k):
            continue
        if k in fill_if_empty and existing.get(k):
            continue
        out[k] = v
    return out


# 12 -------------------------------------------------------------------------------------------
def should_alert(key, now, last_sent, cooldown_days):
    """last_sent: {key: day number}. Updates last_sent when it returns True."""
    if key in last_sent and now - last_sent[key] < cooldown_days:
        return False
    last_sent[key] = now
    return True


# 13 -------------------------------------------------------------------------------------------
def summarise(rows, group_field, value_field):
    out = {}
    for r in rows:
        g = out.setdefault(r[group_field], {"count": 0, "total": 0})
        g["count"] += 1
        g["total"] += r[value_field]
    for g in out.values():
        g["avg"] = round(g.pop("total") / g["count"], 1)
    return out


# 14 -------------------------------------------------------------------------------------------
def process_all(records, process, max_fail_rate=0.10):
    ok, failed = [], []
    for rec in records:
        try:
            ok.append(process(rec))
        except ValueError as e:
            failed.append({"record": rec, "error": str(e)})
    rate = len(failed) / len(records) if records else 0
    return ok, failed, rate > max_fail_rate


if __name__ == "__main__":
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import pipeline_drill_checks
    pipeline_drill_checks.report(sys.modules[__name__])
