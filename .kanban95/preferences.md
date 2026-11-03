# Board preferences

## What this project is

A public, agent-readable document branding skill for Data With Dillon (DWD). Any AI agent pointed at the repo (GitHub: dillon-shearer/dwd-document-skill) reads it and produces Word, PowerPoint and other professional documents in the same DWD style.

Layout follows the open Agent Skills format:

- `SKILL.md` at the repo root, with `name` and `description` frontmatter.
- Rule files under `references/`.
- Templates under `assets/`.

Everything is plain markdown plus a few binary templates, so any agent can read it from the raw GitHub URL.

## How the board works

- GitHub repo with push.
- Base branch is `master` locally; it pushes to `main` on GitHub.
- The board pushes after every merge, so `master` must always pass `python check.py`.

## Build and test

- There is no Node project here. Ignore any `npm run build` or `npm run test:changed` instruction in the agent brief; those npm commands do not apply.
- The test command is `python check.py` from the repo root (ticket #2 creates it).
- Python 3.10 is at `C:\Users\dills\AppData\Local\Programs\Python\Python310\python.exe` and on PATH as `python`.

## Operator style

- Brief replies, plain language.
- ASCII only.
- No code comments.
- Surgical changes; preserve all existing behaviour.
- Own every issue you find, even if your ticket did not cause it.
- Files use LF line endings. On Windows write files with explicit `newline="\n"` or as bytes.

## Desktop

Agents never open a window on the desktop. For HTML checks use:

`"C:\Program Files\Google\Chrome\Application\chrome.exe" --headless=new --dump-dom <file>`
