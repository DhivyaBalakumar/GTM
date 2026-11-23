# 1. How programs and the internet work (the mental model)

## A program is a list of instructions

A Python file (`something.py`) is plain text. When you run `python something.py`, the **Python
interpreter** reads it **top to bottom, one line at a time**, and does what each line says. If a line
fails, it stops and prints an error (a **traceback**) telling you which line and why.

```
Your code (text)  →  Python interpreter  →  actions: calculations, files, network calls, output
```

## Where things live while a program runs

| Thing | Analogy | Lasts |
| --- | --- | --- |
| **Memory (RAM)** – variables | A whiteboard | Until the program ends |
| **Disk** – files (CSV, JSON, .py) | A filing cabinet | Until deleted |
| **Database** – tables | A filing cabinet with an index and rules | Until deleted |
| **Another computer** – an API | A shop you phone | Their system, not yours |

This is why pipelines **save to files or databases**: variables vanish when the script ends.

## The terminal

The terminal (PowerShell on Windows) is a text window where you type commands. You always run commands
**in a folder** (the "current directory"). Most `FileNotFoundError`s happen because you ran Python from
the wrong folder.

## How the internet carries a request

When your code calls an API:

1. Your code builds an **HTTP request**: a method (GET/POST), a URL, headers (like your API key),
   and maybe a body (JSON).
2. **DNS** turns the name `api.hubapi.com` into an IP address (like a phone book).
3. The request travels over **HTTPS** (encrypted) to that server.
4. The server checks your key, does the work, and sends back an **HTTP response**: a **status code**
   (200 OK, 404 not found, 429 slow down…) and a body, usually **JSON**.
5. Your code reads the status and the JSON and decides what to do.

```
your script ──HTTP request──▶ api.hubapi.com
            ◀──HTTP response── (status 200 + JSON)
```

## Client and server

- **Client:** the one asking (your script, your browser).
- **Server:** the one answering (HubSpot's API, or your own Flask app when it receives a webhook).

With webhooks, roles flip: HubSpot becomes the client and **your** code is the server.

## JSON: the language of APIs

```json
{
  "name": "PeopleCo GmbH",
  "domain": "peopleco.de",
  "employees": 120,
  "tags": ["software", "dach"],
  "owner": null
}
```

In Python this becomes a **dictionary** with a **list** inside; `null` becomes `None`, `true` becomes
`True`.

## Libraries and packages

Other people's code you can use. Python's **standard library** is built in (`json`, `csv`,
`datetime`, `logging`). Others you install with `pip`: `pandas` (tables), `requests` (HTTP), `flask`
(web server), `anthropic` (Claude), `pytest` (tests).

## Check yourself

1. Why does a pipeline write results to a file or database instead of keeping them in variables?
2. What two things does every HTTP response contain?
3. In a webhook, which side is the server?

Next: [02-setup-windows.md](02-setup-windows.md)
