# DWD Document Skill

A document branding skill for Data With Dillon (DWD). It gives any AI agent the rules, templates and checkers to produce on-brand Word, PowerPoint, Excel, Markdown and HTML deliverables. It follows the open Agent Skills format, with `SKILL.md` at the root. GitHub: https://github.com/dillon-shearer/dwd-document-skill

## What is inside

- `SKILL.md`: the entry point. It tells the agent which files to read for each format.
- `references/`: `brand.md` holds the shared brand rules (palette, typography, tables, writing). Each format has its own rules file.
- `assets/`: templates to start from and finished samples to compare against. See [assets/README.md](assets/README.md).
- `scripts/`: build scripts for the templates and samples, one checker per format, and helper modules (`dwd_pptx.py`, `dwd_excel.py`, `dwd_prose.py`). See [scripts/README.md](scripts/README.md).

| Format | Rules | Template or sample | Checker |
| --- | --- | --- | --- |
| Word | `references/word.md` | `assets/dwd-template.docx` | `scripts/check_docx.py` |
| PowerPoint | `references/powerpoint.md` | `assets/dwd-template.pptx` | `scripts/check_deck.py` |
| Excel | `references/excel.md` | `assets/dwd-template.xlsx` | `scripts/check_xlsx.py` |
| Markdown | `references/markdown.md` | `assets/dwd-sample.md` | `scripts/check_md.py` |
| HTML | `references/html.md` | `assets/dwd-report.html` | `scripts/check_html.py` |

## Using it with an agent

1. Clone the repo and tell the agent to read the folder, starting with `SKILL.md`.
2. Give the agent the raw URL of the skill: https://raw.githubusercontent.com/dillon-shearer/dwd-document-skill/main/SKILL.md. This is enough for Markdown. Word, PowerPoint and Excel also need their template under `assets/`, so give the raw base URL https://raw.githubusercontent.com/dillon-shearer/dwd-document-skill/main/ as well and tell the agent to fetch the rules and template it needs from there (for example `assets/dwd-template.docx`).
3. For Claude Code, copy the folder into `.claude/skills/` (for example `.claude/skills/dwd-document-skill/`) in your project or home directory.

## Checking a finished file

Run `python check.py` from the repo root. It exits 0 when every check passes or is skipped.

Each checker can also run on one file:

```
python scripts/check_docx.py path/to/file.docx
```

## Requirements

- Python 3.10 or later.
- python-docx, python-pptx, openpyxl and matplotlib. The scripts that need them install them.

## License

MIT. See [LICENSE](LICENSE).
