# HTML

Rules for writing a self-contained .html report in the DWD brand. Read [brand.md](brand.md) first; this file maps those rules onto HTML and CSS. The operator turns the HTML into PDF, so do not produce a PDF.

## Start from the template

Copy `assets/dwd-report.html` and replace the body content; the body is a sample of every block below. Keep the original stylesheet whole. Append document-specific CSS at the end of the same `<style>` block. No second `<style>` block, and no `style` attribute anywhere except `style="width: N%"` on a `.bar`.

## File rules

- One .html file. No framework, no build step, no `<script>`.
- The only allowed external resource request is the Google Fonts stylesheet for DM Sans and IBM Plex Mono (with its two `preconnect` links). No other `<link>`, no remote images. Ordinary citation hyperlinks (`<a href="https://...">`) are allowed.
- Images are inline: SVG markup or a `data:` URI.
- UTF-8 text with LF line endings is allowed. Write entities only where HTML needs them: `&amp;`, `&lt;`, `&gt;`, and quotes inside attributes.
- `<html lang="en">`, `<meta charset="utf-8">`, a viewport meta, `<meta name="color-scheme" content="light">`, and a `<title>` of the form "Document title - DWD".

## Tokens

Brand colours and font families are defined once as custom properties on `:root`; rules use `var(...)` for those. Dimensions and other values are plain. Exceptions: literal values inside `@page` (where `var()` does not work), and inline SVG may use presentation attributes with literal brand hex (`fill="#7a2e2e"`).

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
| `--series-1` to `--series-6` | #7a2e2e, #4a4239, #b8893b, #4a6b3a, #5a7a8a, #5c3a1a | Categorical |
| `--seq-1` to `--seq-6` | #f3e7e4, #dfbfb8, #c4928a, #a6635b, #7a2e2e, #5c2020 | Sequential, light to dark |
| `--div-1` to `--div-6` | #7a2e2e, #b07a6e, #e3d3cc, #d4ddcb, #86a274, #4a6b3a | Diverging, oxblood to green |

Fonts:

- `--font-heading`: "DM Sans", "Segoe UI", system-ui, sans-serif.
- `--font-body`: Aptos, Calibri, Carlito, "Segoe UI", sans-serif. Aptos is not on Google Fonts; it is used when installed.
- `--font-mono`: "IBM Plex Mono", ui-monospace, Consolas, "Courier New", monospace.
- DM Sans, Aptos and IBM Plex Mono are not installed in agent sandboxes and Google Fonts may be blocked there, so an agent's own render uses the fallbacks and the operator's PDF will differ from it. Do not change the stacks because of that.

## Light only

The report is light. Set `color-scheme: light` on `:root` and add the color-scheme meta. Do not add `prefers-color-scheme` styles. If a dark style is ever added, the table header and the mark keep a solid #7a2e2e fill with #ffffff text; never lighten them.

## Page and print

- Screen: body on `--paper`, content in a `.page` column on `--surface`, about 50rem wide.
- PDF route: Chrome or Edge, File > Print > Save as PDF, background graphics on, browser headers and footers off. "Print preview" in these rules means that renderer. wkhtmltopdf and similar tools do not draw margin-box page numbers.
- `@page { size: letter portrait; margin: 2.54cm; }`, matching brand page setup and the Word template.
- Page numbers come from `@page` only: `@bottom-right { content: counter(page); }` in IBM Plex Mono 8pt #6f6b64, none on the first page (`@page :first`). There is no screen footer.
- `print-color-adjust: exact` on body so fills print.
- In `@media print`: hide `nav` and `.no-print`, drop the `.page` padding and width, make the cover fill page 1 with `break-after: page`.
- Every h1 section starts a new page with its header block at the top: `.doc-header { break-before: page; break-after: avoid; }`.
- Headings and captions `break-after: avoid`; blockquote, callout, figure and `pre` `break-inside: avoid`.
- Tables: `thead` repeats (`display: table-header-group`) and a `tr` never splits. Long tables may break between rows. Add class `short` to a table of up to about 12 rows to keep it whole (`table.short { break-inside: avoid; }`).
- A figure taller than the printable area is split into two figures, each with its own caption.
- `.page-break` forces a break.

## Header block

- `<header class="doc-header">` right before each `h1`, with the mark at left and the section at right ("2. Findings", same number as the h1), 1px `--rule` line below.
- The mark is `<span class="mark">DWD</span>`: always "DWD", never "DW". Solid `--accent` fill, `--on-accent` text, IBM Plex Mono 500.
- Header text: IBM Plex Mono 8pt, uppercase, letter spacing 0.08em, `--ink-3`.

## Cover

`<section class="cover">`: 6px `--accent` left border, eyebrow "Data With Dillon", title (DM Sans 700, 44pt, line height 1.05, letter spacing -0.02em, `--ink`, `max-width: 9ch`), subtitle (`--ink-2`), date at the bottom (`3 November 2026`, per brand.md). On screen the text starts about a fifth down; in print about a third.

## Headings

- `h1` once per section, numbered in order from 1 ("2. Findings"): 28px, 1px `--ink-3` rule below, 6px padding, 8px margin under the rule.
- `h2` 20px, `h3` 15px, no rule. All DM Sans 700, `--accent`, line height 1.15, letter spacing -0.01em.
- No `h4` or deeper. Do not skip a level. Sentence case.
- HTML numbers `h1` sections, while Markdown numbers `##` under one document H1; converting between them shifts every level by one on purpose.

## Body text

Aptos 11pt, line height 1.15, `--ink`, paragraphs `margin: 0 0 0.6em`. Links in `--accent`, `--accent-hover` on hover, a 2px `--accent` outline on `a:focus-visible`.

## Code

- Inline `code`: `--font-mono` 10pt on `--accent-soft`.
- `pre` block: `--font-mono` 9.5pt, `--accent-soft` fill, 8px 12px padding, no border, `break-inside: avoid`. Long lines scroll horizontally on screen and wrap in print.
- No syntax colouring.

## Lists

- `ul`: no default bullets. Each `li::before` is a 6px `--accent` square, 4px from the left; text indented 22px; 6px between items.
- `ol`: numbers in `--accent`, bold (`li::marker`).
- Nest at most one level.

## Tables

- A caption line right before the table: `<div class="caption" id="t1">Table 1. Revenue by quarter</div>`, numbered in order. `<caption>` is not used; tie the line to the table with `aria-labelledby="t1"` on the `table`.
- Always `<thead>` with `<th scope="col">` cells: solid `--accent` fill, `--on-accent` text, weight 600, left aligned.
- Body rows: 1px `--rule` bottom line, no vertical lines. Cell padding 6px 8px.
- First column names the row and is left aligned. Number columns get `class="num"` (right aligned) on both `th` and `td`; the table uses `font-variant-numeric: tabular-nums`.
- No empty cells: `-` means missing, `n/a` means not applicable. Units go in the header.

## Callouts and quotes

- Callout: `<div class="callout"><strong>Key point:</strong> ...</div>`. 3px `--accent` left border, 12px left padding, 2px top and bottom, line height 1.45, no fill. Labels: Note, Key point, Warning. One callout per h1 section at most.
- Quote: `<blockquote>` with the quote in `<p>` and the source in a `<footer>` (IBM Plex Mono caps, `--ink-3`). Italic `--ink-2`, indented both sides. No left bar, so it never looks like a callout.

## Figures and charts

- Every chart or image is a `<figure>` with a `<figcaption class="caption">` above it: "Figure 1. ...", numbered in order, IBM Plex Mono caps, `--ink-3`.
- Simple bar charts are pure CSS (see `.bar-chart` in the template): one `.bar` per row, width as a percent of the axis maximum, series classes `s1` to `s6` in brand order. The value label is a `.bar-value` span after the `.bar` inside `.bar-track`: outside the bar, just past its end, in `--ink-2`. Never white text inside the bar.
- Contrast: text on a fill needs 4.5:1. With white text only `--accent`, `--series-2`, `--series-4` and `--series-6` clear it with margin; `--series-5` is 4.6:1, too close, and `--series-3` fails at 3.1:1.
- Give a CSS chart `role="img"` and an `aria-label`. Inline SVG needs `role="img"`, a `<title>` and a `<desc>` that lists the data.
- Every chart needs a text or table equivalent nearby.
- Axis line 1px `--ink-3`. No gridlines, no 3D, no gradients, no legend when bars are labelled.
- Use the categorical series in order; `--seq-*` for ordered values, `--div-*` for values either side of a midpoint.
- More complex charts: inline SVG using the same colours and fonts.

## Voice

Voice and prose: follow the Writing section in brand.md.

## Checklist before sending

Each line is one `scripts/check_html.py` check unless marked human-only.

1. UTF-8, LF line endings, one final newline.
2. `lang="en"`, charset, viewport and color-scheme metas, title ends in " - DWD".
3. No `<script>`; the only links are Google Fonts and its two preconnects; no remote images.
4. One `<style>` block that starts with the template stylesheet unchanged.
5. No `style` attribute except width on `.bar`.
6. No brand hex outside `:root`, `@page` and inline SVG.
7. Every mark reads "DWD".
8. No `h4` to `h6`; h1 numbered from 1, each right after its header block with the same number; no skipped levels.
9. No screen footer block.
10. Every table has a "Table N." caption line before it, `aria-labelledby`, a `thead` and `scope="col"`; every figure has a "Figure N." caption.
11. No empty cells; number cells and their header carry `num`.
12. Callouts use Note, Key point or Warning, at most one per h1 section.
13. Charts and SVG have `role="img"`; SVG has `<title>` and `<desc>`.
14. Quotes have a `p` and a `footer`.
15. No bare `&`, no `<` in text.
16. print-render: PASS or SKIP; a SKIP means print by hand and check the page count. On PASS the page count looks right.
17. Human-only: print preview shows the cover alone on page 1, each section on a new page, page numbers from page 2, and no table split mid-row.
18. Human-only: one voice throughout, dates as `3 November 2026`, every chart has a text or table equivalent.
19. `python scripts/check_html.py file.html` passes.
