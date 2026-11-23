"""
Lesson 3: lists and tuples
==========================

Run me:  python 03-python/lessons/03_lists_and_tuples.py

A LIST is an ordered collection: [item, item, item]. Lists can change (add, remove).
You'll use lists for: rows of leads, domains, batches of records, API results.
"""

print("=== 1. Creating and reading ===")
domains = ["peopleco.de", "nordbanktech.nl", "brightforge.io"]
print(domains)
print("first:", domains[0], "| last:", domains[-1], "| count:", len(domains))
# Indexes start at 0. domains[3] would raise IndexError (only 0, 1, 2 exist).

print("\n=== 2. Changing a list ===")
domains.append("alpenwerk.ch")            # add one to the end
domains.extend(["corvex.de", "opal.de"])  # add several
domains.insert(0, "first.io")             # add at a position
print(domains)
domains.remove("first.io")                # remove by value
last = domains.pop()                      # remove and return the last item
print("popped:", last, "->", domains)

print("\n=== 3. Checking and finding ===")
print("peopleco.de" in domains)           # membership: True/False
print(domains.index("brightforge.io"))    # position of a value
print(["DE", "NL", "DE"].count("DE"))     # how many times

print("\n=== 4. Slicing: parts of a list ===")
nums = [10, 20, 30, 40, 50, 60, 70]
print(nums[0:3], nums[3:], nums[:2], nums[-2:], nums[::2])
# [start:end] includes start, excludes end. [::2] = every 2nd item.

print("\n=== 5. BATCHING: splitting a list into chunks (APIs accept max N per call) ===")
records = [f"company_{i}" for i in range(1, 24)]   # 23 records
BATCH_SIZE = 10
for start in range(0, len(records), BATCH_SIZE):   # 0, 10, 20
    batch = records[start:start + BATCH_SIZE]
    print(f"batch starting at {start}: {len(batch)} records -> {batch[0]} .. {batch[-1]}")
# 23 records -> batches of 10, 10, 3. This exact loop sends data to a CRM in batches.

print("\n=== 6. Sorting ===")
scores = [72, 95, 40, 88]
print(sorted(scores))                  # new sorted list, original unchanged
print(sorted(scores, reverse=True))    # biggest first
scores.sort()                          # sorts IN PLACE (changes scores itself)
print(scores, "| max:", max(scores), "| min:", min(scores), "| sum:", sum(scores))

print("\n=== 7. Lists of lists, and lists of dictionaries ===")
table = [["PeopleCo", 120], ["Nordbank", 80]]
print(table[1][0])   # row 1, column 0 -> 'Nordbank'
leads = [{"name": "PeopleCo", "employees": 120}, {"name": "Nordbank", "employees": 80}]
print(leads[0]["name"])   # this shape (list of dicts) is how API data looks

print("\n=== 8. Copying: a trap ===")
a = [1, 2, 3]
b = a            # NOT a copy: both names point to the same list
b.append(4)
print("a after changing b:", a)    # a changed too!
c = a.copy()     # a real copy
c.append(5)
print("a after changing c:", a)

print("\n=== 9. Tuples: fixed, unchangeable lists ===")
pair = ("PeopleCo", 95)           # use () instead of []
name, score = pair                # UNPACKING: split into variables
print(name, score)
# Tuples are good for pairs that belong together and shouldn't change, and as dictionary
# keys (lists can't be keys). Example: a webhook event key (event_id, subscription_id).
event_key = (101, 9001)
print("event key:", event_key)

print("\n=== 10. Unpacking in loops ===")
for name, score in [("PeopleCo", 95), ("Nordbank", 80)]:
    print(f"{name}: {score}")

# ---------------------------------------------------------------------------
# TRY IT
# 1. Change BATCH_SIZE to 7. How many batches, and of what sizes?
# 2. Get the top 3 scores from [55, 91, 72, 88, 40, 99] in one line.
# 3. What happens with domains[10]? Read the error name.
# ---------------------------------------------------------------------------
