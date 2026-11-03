---
name: dwd-document-skill
description: Brand rules, templates and checkers for Data With Dillon (DWD) deliverables: reports, Word (.docx), PowerPoint decks (.pptx), Excel workbooks (.xlsx), Markdown (.md) and single-file HTML, for use with any DWD document, deck, sheet or page.
---

# DWD Document Skill

Brand rules and templates for Data With Dillon (DWD) deliverables. It covers
the shared brand (palette, type, layout, voice) and the rules for each output
format.

## What it covers

- `references/brand.md`: the brand rules every format shares.
- `references/word.md`: rules for Word documents (.docx).
- `references/powerpoint.md`: rules for PowerPoint decks (.pptx).
- `references/markdown.md`: rules for Markdown files (.md).
- `references/excel.md`: rules for Excel workbooks (.xlsx).
- `references/html.md`: rules for single-file HTML reports (.html).
- `assets/`: ready-made templates, where one exists.
- `scripts/`: the scripts that build the templates, check finished files, and
  the PowerPoint and Excel helpers (`dwd_pptx.py`, `dwd_excel.py`).

For a format with no file under `references/` yet, apply `brand.md` and say so in
the output.

## How to use it

1. Read [references/brand.md](references/brand.md) in full, first.
2. Then read the one file under `references/` that matches the output format:
   [word.md](references/word.md) for Word,
   [powerpoint.md](references/powerpoint.md) for PowerPoint,
   [markdown.md](references/markdown.md) for Markdown,
   [excel.md](references/excel.md) for Excel,
   [html.md](references/html.md) for HTML.
3. If a matching template exists under `assets/`, start from it instead of a
   blank file.
4. Where a format file and `brand.md` disagree, the format file wins for that
   format.

Writing rules (voice, punctuation, banned words) live in `brand.md` and apply to
every format.
