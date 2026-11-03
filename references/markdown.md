# Markdown

Dialect: GitHub Flavored Markdown. Tables and column alignment are GFM extensions. Target viewers are GitHub, VS Code preview and Obsidian. Fonts, colours and bullet shapes are the viewer's; here the brand is structure and voice.

Rules for writing a .md file (README, report, notes) in the DWD brand. Read [brand.md](brand.md) first. `assets/dwd-sample.md` follows every rule below.

## Title line and eyebrow

- Line 1 is the eyebrow: `DWD / DATA WITH DILLON` in inline code, uppercase. The mark is always "DWD", never "DW".
- Line 3 is the title as the only H1: `# Title`.
- Line 5 is one italic line with the subtitle and date: `*Subtitle - 3 November 2026*`. Dates follow brand.md.
- Lines 2 and 4 are blank. No front matter above line 1.
- Then the intro paragraph.

## Headings

- One H1 per file (the title). Sections are H2, subsections H3. Never use H4 or deeper; split the section instead.
- Do not skip a level (no H3 straight under H1).
- Number H2 sections in reports: `## 2. Methods`. The dot form is the heading; `2 - Methods` is the same section as page furniture in the Word header and the PowerPoint footer. Do not number H3. READMEs and notes are not numbered. Number every H2 or none.
- Sentence case. No trailing punctuation. No bold or links inside a heading.
- One blank line before and after every heading.

## Body text

- Short paragraphs, one idea each. One blank line between paragraphs.
- Bold for a key term on first use only; table labels and callout labels are bold every time. Italic for titles of works and the subtitle line. No underline, no HTML.

## Lists

- Bullets use `-` only (renders as the brand's single bullet; never `*` or `+`).
- Steps that must happen in order use `1.`, `2.`, `3.` so the raw file reads in order too.
- No blank lines between items. Nest at most one level. A nested item indents to the parent's content column: two spaces under `-`, three under `1.`.
- Items are fragments or full sentences, not a mix, within one list.

## Tables

- Always a header row, then the `| --- |` separator row.
- Text columns left aligned (`---`), number columns right aligned (`---:`). Never centre.
- No empty cells: `-` means missing, `n/a` means not applicable.
- First column names the row. Keep units in the header, not in each cell.
- One line of bold text above the table as its label, for example `**Table 1. Revenue by quarter**`.

## Callouts

The brand callout is a left accent bar with no fill, so use a plain blockquote that starts with a bold label. Do not use GitHub `> [!NOTE]` alerts; they add colour and icons the brand does not have.

```text
> **Note:** Figures exclude refunds issued after 30 June.
```

Labels: `Note`, `Key point`, `Warning`. One callout per H2 section at most; the intro before the first H2 counts as a section.

## Quotes

A quote is a blockquote with no bold label. After the quote, an empty `>` line, then the source in italics.

```text
> Most growth came from people who had bought before.
>
> *Sales review, Q2*
```

## Code blocks

- Fenced with three backticks and always a language tag (`python`, `sql`, `bash`, `text`).
- Never indent code to make a block. Inline code for file names, paths, commands and field names.
- Keep blocks short; link to the full script instead of pasting it.

## Links

- Inline links with descriptive text: `[the sales script](scripts/sales.py)`, never "click here" or a bare URL in prose.
- Relative paths for files in the same repo. Full `https://` URLs for outside pages.
- A document that lives in no repo uses full URLs or no link.
- A `#fragment` link uses GitHub's heading slug: lowercase, spaces to hyphens, punctuation dropped (`## 3. Method` is `#3-method`).

## Front matter

None for reports, READMEs and notes. Use YAML front matter only when a tool needs it (for example `SKILL.md`).

## Voice

Voice and prose: follow the Writing section in brand.md.

## Line length and file

- Prose: one paragraph per line, no hard wrap (diffs stay clean on GitHub).
- Code blocks and tables: keep lines under 100 characters where possible.
- Deliverables are UTF-8 with LF line endings and one final newline.
- This skill repo stays ASCII, because `check.py` enforces it.

## Checklist before sending

1. UTF-8, LF endings, exactly one final newline.
2. Line 1 eyebrow, line 3 the only H1, line 5 the italic subtitle and date; lines 2 and 4 blank.
3. No front matter.
4. H2 and H3 only, no skipped levels.
5. H2 numbered `N.` in order from 1, or none numbered.
6. Headings have no trailing punctuation, bold or links.
7. Bullets use `-`, never `*` or `+`.
8. Every table has a bold `**Table N.**` label, a `---` or `---:` separator and no empty cells.
9. Every code fence has a language tag.
10. Callouts use `Note`, `Key point` or `Warning`, no `[!NOTE]` alerts, at most one per section.
11. No HTML.
12. Relative links resolve and `#fragment` links match a heading.
13. Human only: one voice throughout, short paragraphs, descriptive link text, right-aligned number columns.
14. `python scripts/check_md.py file.md` passes.
