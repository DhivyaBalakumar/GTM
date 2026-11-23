# 2. Setup on Windows: terminal, Python, VS Code, venv, Git, this repo

Do this once. It takes about 30 minutes.

## 1. Check what you have

Open **PowerShell** (Start → type "PowerShell") and run:

```powershell
python --version     # need 3.10 or newer (you have 3.12.5)
git --version        # you have 2.56
```

If `python` isn't found: install from python.org and **tick "Add python.exe to PATH"**.

## 2. Terminal basics

| Command | What it does |
| --- | --- |
| `pwd` | Show the current folder |
| `cd folder` / `cd ..` | Go into a folder / up one level |
| `dir` (or `ls`) | List files |
| `mkdir name` | Make a folder |
| `python file.py` | Run a Python file |
| `code .` | Open the current folder in VS Code |
| `Ctrl + C` | Stop a running program |
| ↑ arrow | Repeat the previous command |
| `Tab` | Autocomplete a file or folder name |

## 3. Get this repo onto your laptop

```powershell
cd $HOME
git clone https://github.com/DhivyaBalakumar/GTM.git
cd GTM
code .
```

## 4. Create a virtual environment (venv)

A venv is a private box of packages for one project, so projects don't clash.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

You'll see `(.venv)` at the start of the line. **Activate it every time** you open a new terminal for
this repo.

If PowerShell blocks the activate script, run this once:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

## 5. Install the packages

```powershell
pip install -r requirements.txt
```

`requirements.txt` lists everything this repo uses: pandas, requests, flask, pytest, python-dotenv,
anthropic.

## 6. VS Code

- Install the **Python** extension (by Microsoft).
- `Ctrl + Shift + P` → "Python: Select Interpreter" → choose the one in `.venv`.
- Open the terminal inside VS Code with `` Ctrl + ` ``.
- Run a file: open it and press the ▶ button, or type `python path\to\file.py` in the terminal.

## 7. Check everything works

```powershell
python 03-python/lessons/01_values_and_variables.py
pytest
```

## 8. Secrets: the .env file

API keys never go in code. Copy the example file and fill in keys only when a lesson needs them:

```powershell
copy .env.example .env
```

`.env` is listed in `.gitignore`, so Git never uploads it.

## 9. Git habits for your own practice

```powershell
git status                       # what changed
git add .                        # stage everything
git commit -m "Finish lesson 3"  # save a snapshot
git push                         # upload to GitHub
```

Next: [../03-python/README.md](../03-python/README.md)
