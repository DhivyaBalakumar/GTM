# Module 9: Claude and AI in GTM

"Hands-on with Claude (Code or API)" is the job post's **only explicit must-have**. Two parts:

- **Claude Code:** an AI coding assistant in your terminal that reads your project, edits files and runs
  commands. You use it to *build faster*.
- **The Claude API:** calling Claude from your own Python, so your *pipeline* can use AI on each record
  (research, classification, drafting).

| # | File | Covers |
| --- | --- | --- |
| 1 | [01-llms-and-when-to-use-ai.md](01-llms-and-when-to-use-ai.md) | How LLMs work (just enough), tokens, cost, AI vs rules, GTM use cases |
| 2 | [02-prompts-structured-output-guardrails.md](02-prompts-structured-output-guardrails.md) | The API call, prompt design, JSON output, validation, fallbacks, guardrails for agents that write to the CRM, evaluation |
| 3 | [03-claude-code.md](03-claude-code.md) | Installing and using Claude Code well, CLAUDE.md, skills, how to talk about it in interviews |
| 4 | [claude_scoring.py](claude_scoring.py) | Runnable: classify and score companies with Claude, validated JSON, fallbacks, logging. Works offline with a built-in fake model so you can see validation in action |

```powershell
python 09-claude-and-ai/claude_scoring.py            # offline demo (fake model, shows validation)
# with ANTHROPIC_API_KEY in .env:
python 09-claude-and-ai/claude_scoring.py --live
```
