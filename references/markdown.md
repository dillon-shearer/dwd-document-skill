# Markdown

Rules for writing a .md file (README, report, notes) in the DWD brand. Read [brand.md](brand.md) first. Markdown has no colours or fonts, so here the brand is structure and voice. `assets/dwd-sample.md` follows every rule below.

## Title line and eyebrow

- Line 1 is the eyebrow: `DWD / DATA WITH DILLON` in inline code, uppercase. The mark is always "DWD", never "DW".
- Line 3 is the title as the only H1: `# Title`.
- Line 5 is one italic line with the subtitle and date: `*Subtitle - 3 November 2026*`.
- Then the intro paragraph.

## Headings

- One H1 per file (the title). Sections are H2, subsections H3. Never use H4 or deeper; split the section instead.
- Do not skip a level (no H3 straight under H1).
- Number H2 sections in reports, matching the Word header ("2 - Methods"): `## 2. Methods`. Do not number H3. READMEs and notes are not numbered.
- Sentence case. No trailing punctuation. No bold or links inside a heading.
- One blank line before and after every heading.

## Body text

- Short paragraphs, one idea each. One blank line between paragraphs.
- Bold for a key term on first use only. Italic for titles of works and the subtitle line. No underline, no HTML.

## Lists

- Bullets use `-` only (renders as the brand's single bullet; never `*` or `+`).
- Steps that must happen in order use `1.`, `2.`, `3.` so the raw file reads in order too.
- No blank lines between items. Nest at most one level, indented two spaces.
- Items are fragments or full sentences, not a mix, within one list.

## Tables

- Always a header row, then the `| --- |` separator row.
- Text columns left aligned (`---`), number columns right aligned (`---:`). Never centre.
- No empty cells: write `-` or `n/a`.
- First column names the row. Keep units in the header, not in each cell.
- One line of bold text above the table as its label, for example `**Table 1. Revenue by quarter**`.

## Callouts

The brand callout is a left accent bar with no fill, so use a plain blockquote that starts with a bold label. Do not use GitHub `> [!NOTE]` alerts; they add colour and icons the brand does not have.

```text
> **Note:** Figures exclude refunds issued after 30 June.
```

Labels: `Note`, `Key point`, `Warning`. One callout per section at most.

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

## Front matter

None for reports, READMEs and notes. Use YAML front matter only when a tool needs it (for example `SKILL.md`).

## Voice

[brand.md](brand.md) does not fix a voice. Pick one per document from the request and keep it throughout; ask when the occasion is unclear.

- Plain, first person: "I looked at twelve months of sales and found that repeat customers drive most of the growth."
- Neutral, third person: "Twelve months of sales data show that repeat customers drive most of the growth."
- Formal corporate: "Data With Dillon has completed a comprehensive review of twelve months of sales data, which indicates that repeat customers are the principal driver of growth."

In every voice: lead with the finding, short sentences, plain words, no filler.

## Line length and file

- Prose: one paragraph per line, no hard wrap (diffs stay clean on GitHub).
- Code blocks and tables: keep lines under 100 characters where possible.
- ASCII only, LF line endings, one newline at the end of the file.

## Checklist before sending

1. Eyebrow reads `DWD / DATA WITH DILLON`, then one H1.
2. H2 and H3 only, no skipped levels, H2 numbered in reports.
3. Bullets use `-`, steps use `1.`.
4. Every table has a header row, a label line, right-aligned numbers and no empty cells.
5. Callouts are blockquotes with a bold label; no `[!NOTE]` alerts.
6. Every code block has a language tag.
7. Links have descriptive text and relative paths resolve.
8. One voice throughout, chosen for this document.
9. ASCII only, LF endings.
