# Module 3: Python

Python is the main tool of the job. The target: **read and write 50–150 line scripts that call APIs,
clean data and write to a CRM**, and explain every line. About 70% of your technical prep.

## How this module works

Each lesson is a **runnable Python file** full of comments. Do this for each one:

1. **Read** the file top to bottom (the comments are the lesson).
2. **Run** it: `python 03-python/lessons/01_values_and_variables.py`, and match each printed line to
   the code that produced it.
3. **Change** things: break a line on purpose, see the error, fix it.
4. **Do the exercise** in `exercises/` *without* looking at `solutions/`. Run the exercise file; it
   checks your answers and tells you what's wrong.
5. **Explain** it out loud in two minutes.

## Lessons

| # | File | You'll learn | Priority |
| --- | --- | --- | --- |
| 1 | [01_values_and_variables.py](lessons/01_values_and_variables.py) | Variables, types, conversion, None, truthiness | Must |
| 2 | [02_strings.py](lessons/02_strings.py) | Cleaning text: strip, lower, replace, split, f-strings, slicing | Must |
| 3 | [03_lists_and_tuples.py](lessons/03_lists_and_tuples.py) | Lists, slicing, batching, tuples, unpacking | Must |
| 4 | [04_dicts_and_sets.py](lessons/04_dicts_and_sets.py) | Dictionaries, `.get()`, nested JSON-like data, sets for "seen" checks | Must |
| 5 | [05_conditions.py](lessons/05_conditions.py) | if/elif/else, comparisons, and/or/not, scoring rules | Must |
| 6 | [06_loops.py](lessons/06_loops.py) | for, range, enumerate, zip, while, break, continue, counting | Must |
| 7 | [07_functions.py](lessons/07_functions.py) | def, return, defaults, keyword args, pure functions, docstrings, type hints | Must |
| 8 | [08_comprehensions_and_sorting.py](lessons/08_comprehensions_and_sorting.py) | List/dict comprehensions, sorted with key, lambda | Must |
| 9 | [09_errors_and_debugging.py](lessons/09_errors_and_debugging.py) | try/except/else/finally, raise, common errors, reading tracebacks | Must |
| 10 | [10_files_csv_json.py](lessons/10_files_csv_json.py) | Reading/writing files, csv.DictReader/Writer, json, paths | Must |
| 11 | [11_standard_library.py](lessons/11_standard_library.py) | datetime, time, logging, os/env, Counter, defaultdict, cycle, re, urlparse | Must/Good |
| 12 | [12_modules_and_scripts.py](lessons/12_modules_and_scripts.py) | Imports, `if __name__ == "__main__"`, argparse, splitting code into files | Must |

## Exercises

| File | Practises |
| --- | --- |
| [ex01_strings.py](exercises/ex01_strings.py) | Normalising domains and company names |
| [ex02_collections.py](exercises/ex02_collections.py) | Counting, grouping, deduping with lists, dicts, sets |
| [ex03_functions_and_rules.py](exercises/ex03_functions_and_rules.py) | Segmenting, scoring with reasons, routing |
| [ex04_errors_and_files.py](exercises/ex04_errors_and_files.py) | Safe parsing, reading the CSV, writing results |

Run an exercise: `python 03-python/exercises/ex01_strings.py`. When everything passes it prints
`All checks passed`. Solutions are in [solutions/](solutions/), to compare after you've tried.

## What you can skip for now

Classes beyond reading level, decorators, generators, async, metaclasses. If they come up in someone
else's code, you can read them; you won't need to write them for this role.
