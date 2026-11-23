# 3. Claude Code

## What it is

An AI coding assistant that runs in your terminal (and IDEs). It reads your project, edits files, runs
commands and tests, and explains code. The job post treats hands-on Claude experience as a must-have,
so use it daily and be able to talk about *how* you use it.

## Install and start (Windows)

```powershell
irm https://claude.ai/install.ps1 | iex     # installs Claude Code
cd $HOME\GTM
claude                                        # start it inside your project folder
```

(Check the [Claude Code docs](https://docs.claude.com/en/docs/claude-code/overview) for the current
install instructions.)

## Good ways to use it while learning

| Ask | Why it helps |
| --- | --- |
| "Explain what `03-python/lessons/06_loops.py` does, line by line" | Understand code you didn't write |
| "I wrote ex02; review it and point out bugs but don't fix them" | Learn by fixing yourself |
| "Write 5 more test cases for normalize_domain, including weird inputs" | Better tests |
| "Why does this traceback happen?" (paste it) | Faster debugging, while you still decide the fix |
| "Make this function handle a 404 as 'no data'" | Small, reviewable changes |
| "Run the tests and tell me what fails" | It can run commands for you |

**The rule:** read and understand every line it writes. In the live round you'll change your own code
without it (or with it, if allowed, but you still have to explain everything).

## CLAUDE.md: project memory

A `CLAUDE.md` file in your project root tells Claude Code about the project every session: what it
does, how to run and test it, conventions ("use pandas; config lives in config.py; never commit
.env"). Write one for your take-home; it also documents the project for humans.

```markdown
# Account pipeline
- Run: python src/run_pipeline.py --dry-run
- Test: pytest
- Config and thresholds: src/config.py
- Never print or commit API keys; they live in .env
- Writes to HubSpot only via batch upsert on company_domain_key
```

## Skills and agents (awareness)

- **Skills:** packaged instructions for a repeatable task (e.g. "run our outbound campaign workflow").
  You already built Claude agent skills for an outbound workflow, which is directly relevant.
- **Agents / agentic workflows:** Claude calling tools in a loop (search, read a page, write to the
  CRM) to finish a multi-step task. Secfix's culture doc says "all of it will be connected with
  agentic workflows". Guardrails from the previous lesson apply.

## How to talk about it in interviews

Be specific and honest:

> "I use Claude Code daily. I start by having it read the repo and explain the structure, then I
> make small, reviewable changes: for example, adding retry logic, then asking it to write tests for
> the edge cases. I read every diff before accepting it. For the outbound workflow I packaged the
> steps (prospect pull, enrichment, ICP segmentation, drafting, logging) as agent skills so anyone on
> the team gets the same consistent output."

Only describe what you have actually done.
