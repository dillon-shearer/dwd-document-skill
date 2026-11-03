# HTML

Rules for writing a self-contained .html report in the DWD brand. Read [brand.md](brand.md) first; this file maps those rules onto HTML and CSS. The operator turns the HTML into PDF, so do not produce a PDF.

## Start from the template

Copy `assets/dwd-report.html`. Its `<style>` block holds the full brand CSS; keep it whole and replace the body content. The body is a sample of every block below.

## File rules

- One .html file. All CSS inline in one `<style>` block in the head. No framework, no build step, no script.
- The only allowed external link is the Google Fonts stylesheet for DM Sans and IBM Plex Mono (with its two `preconnect` links). No other `<link rel="stylesheet">`, no `<script src>`.
- Every font stack ends in system fallbacks, so the file renders offline.
- Images are inline: SVG markup or a `data:` URI. No remote images.
- ASCII text. Write an entity (`&amp;`, `&lt;`) where HTML needs one; do not type non-ASCII characters.
- `<html lang="en">`, `<meta charset="utf-8">`, a viewport meta and a `<title>`.

## Tokens

Define brand values once as CSS custom properties on `:root`, named after the brand tokens, and use only `var(...)` in rules.

| Property | Value | Brand token |
| --- | --- | --- |
| `--paper` | #fafaf8 | Paper |
| `--surface` | #ffffff | Surface |
| `--ink` | #111110 | Ink |
| `--ink-2` | #44403b | Ink 2 |
| `--ink-3` | #6f6b64 | Ink 3 |
| `--rule` | #e3e1db | Rule |
| `--accent` | #7a2e2e | Accent |
| `--accent-hover` | #5c2020 | Accent hover |
| `--accent-soft` | #f3e7e4 | Accent soft |
| `--on-accent` | #ffffff | text on accent fills |
| `--series-1` to `--series-6` | categorical series | Charts |

Fonts:

- `--font-heading`: "DM Sans", "Segoe UI", system-ui, sans-serif.
- `--font-body`: Aptos, Calibri, Carlito, "Segoe UI", sans-serif. Aptos is not on Google Fonts; it is used when installed.
- `--font-mono`: "IBM Plex Mono", ui-monospace, Consolas, "Courier New", monospace.

## Light only

The report is light. Set `color-scheme: light` on `:root` and `<meta name="color-scheme" content="light">`. Do not add `prefers-color-scheme` styles. If a dark style is ever added, the table header and the mark keep a solid #7a2e2e fill with #ffffff text; never lighten them.

## Page and print

- Screen: body on `--paper`, content in a `.page` column on `--surface`, about 50rem wide.
- Print: `@page { size: letter portrait; margin: 2.54cm; }`, matching brand page setup and the Word template.
- Page number at bottom right with `@page { @bottom-right { content: counter(page); } }` in IBM Plex Mono 8pt #6f6b64; none on the first page (`@page :first`). Write literal values inside `@page`; `var()` does not work there.
- `print-color-adjust: exact` on body so fills print.
- In `@media print`: hide `nav` and `.no-print`, drop the `.page` padding and width, hide the screen footer, make the cover fill page 1 with `break-after: page`.
- Page breaks: headings and captions `break-after: avoid`; tables, rows, figures `break-inside: avoid`; `thead` repeats (`display: table-header-group`); `.page-break` for a forced break.

## Header and footer blocks

- Header: `<header class="doc-header">` with the mark at left and the section at right ("2 - Findings"), 1px `--rule` line below.
- The mark is `<span class="mark">DWD</span>`: always "DWD", never "DW". Solid `--accent` fill, `--on-accent` text, IBM Plex Mono 500.
- Footer: `<footer class="doc-footer">` with the page number at right, nothing at left, 1px `--rule` line above. Shown on screen only; print uses `@page`.
- Header and footer text: IBM Plex Mono 8pt, uppercase, letter spacing 0.08em, `--ink-3`.

## Cover

`<section class="cover">`: 6px `--accent` left border, eyebrow "Data With Dillon", title (DM Sans 700, 44pt, line height 1.05, letter spacing -0.02em, `--ink`, `max-width: 9ch`), subtitle (`--ink-2`), date at the bottom. On screen the text starts about a fifth down; in print about a third.

## Headings

- `h1` once per section, numbered ("2. Findings"): 28px, 1px `--ink-3` rule below, 6px padding, 8px margin under the rule.
- `h2` 20px, `h3` 15px, no rule. All DM Sans 700, `--accent`, line height 1.15, letter spacing -0.01em.
- No `h4` or deeper. Do not skip a level. Sentence case.

## Body text

Aptos 11pt, line height 1.15, `--ink`, paragraphs `margin: 0 0 0.6em`. Links in `--accent`, `--accent-hover` on hover.

## Lists

- `ul`: no default bullets. Each `li::before` is a 6px `--accent` square, 4px from the left; text indented 22px; 6px between items.
- `ol`: numbers in `--accent`, bold (`li::marker`).
- Nest at most one level.

## Tables

- A caption line above: `<div class="caption">Table 1. Revenue by quarter</div>`.
- Always `<thead>` with `<th>` cells: solid `--accent` fill, `--on-accent` text, weight 600, left aligned.
- Body rows: 1px `--rule` bottom line, no vertical lines. Cell padding 6px 8px.
- First column names the row and is left aligned. Number columns get `class="num"` (right aligned) on both `th` and `td`; the table uses `font-variant-numeric: tabular-nums`.
- No empty cells: write `-` or `n/a`. Units go in the header.

## Callouts and quotes

- Callout: `<div class="callout"><strong>Key point:</strong> ...</div>`. 3px `--accent` left border, 12px left padding, 2px top and bottom, line height 1.45, no fill. Labels: Note, Key point, Warning. One per section at most.
- Quote: `<blockquote>` with the quote in `<p>` and the source in a `<footer>` (IBM Plex Mono caps, `--ink-3`). Italic `--ink-2`, indented both sides. No left bar, so it never looks like a callout.

## Figures and charts

- Every chart or image is a `<figure>` with a `<figcaption class="caption">` above it: "Figure 1. ...", IBM Plex Mono caps, `--ink-3`.
- Simple bar charts are pure CSS (see `.bar-chart` in the template): one `.bar` per row, width as a percent of the axis maximum, series classes `s1` to `s6` in brand order. Give the chart `role="img"` and an `aria-label`.
- Axis line 1px `--ink-3`. No gridlines, no 3D, no gradients, no legend when bars are labelled.
- Use the categorical series in order (#7a2e2e, #4a4239, #b8893b, #4a6b3a, #5a7a8a, #5c3a1a). Sequential and diverging scales come from brand.md.
- More complex charts: inline SVG using the same colours and fonts.

## Voice

[brand.md](brand.md) does not fix a voice. Pick one per document from the request and keep it throughout; ask when the occasion is unclear.

## Checklist before sending

1. One .html file; no `<script>`, no stylesheet link except Google Fonts.
2. `:root` tokens match brand.md; rules use `var(...)`, not raw hex (except inside `@page`).
3. Mark reads "DWD"; table header is solid #7a2e2e with #ffffff text.
4. Cover, header block, numbered `h1` sections, no `h4`.
5. Number columns right aligned, no empty cells, captions on every table and figure.
6. Opens offline in a browser and still reads well with fallback fonts.
7. Print preview: US Letter, 2.54 cm margins, cover alone on page 1, page numbers from page 2, no table split mid-row.
8. ASCII only, LF line endings.
