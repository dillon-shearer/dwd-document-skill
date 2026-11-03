# Brand

Shared brand rules for every DWD deliverable. Read this before any format file.

## Palette

Oxblood and paper, the site palette (picker option A).

- Paper: #fafaf8
- Surface: #ffffff
- Ink: #111110
- Ink 2 (secondary text): #44403b
- Ink 3 (captions, labels): #6f6b64
- Rule: #e3e1db
- Accent: #7a2e2e
- Accent hover: #5c2020
- Accent soft (tints): #f3e7e4

## Typography

- Headings: DM Sans 700, fallback 'Segoe UI', system-ui, sans-serif (picker option D).
- Body: Aptos 400 at 11pt, fallback Calibri, Carlito, 'Segoe UI', sans-serif (picker option E, office-safe).
- Labels, eyebrows, page furniture: IBM Plex Mono 400 or 500, fallback ui-monospace, Consolas, 'Courier New', monospace.

## Headings

Mix of picker options C and E: accent-coloured headings, with a thin rule under H1 only.

- All heading levels: DM Sans 700, colour #7a2e2e, line height 1.15, letter spacing -0.01em.
- H1: 28px, with a 1px #6f6b64 rule below, 6px padding under the text and 8px margin under the rule.
- H2: 20px, no rule.
- H3: 15px, no rule.

## Body text

Office default density (picker option D): 11pt / 1.15 line height, colour #111110, paragraph spacing 0.6em. Aptos, fallback Calibri, Carlito, 'Segoe UI', sans-serif.

Bold marks a key term on first use only. That rule does not cover structural labels such as table label lines and callout labels, which are bold every time.

## Tables

Header fill, white text (picker option B).

- Header row: background #7a2e2e, text #ffffff, weight 600, left aligned.
- Body rows: 1px #e3e1db bottom rule, no vertical rules.
- Cell padding 6px 8px; first column left aligned, number columns right aligned, tabular figures.

## Header and footer

The mark reads "DWD" everywhere.

Mark left, section right, the site layout (picker option A).

- Header: DWD mark at left (square, background #7a2e2e, white IBM Plex Mono 500 letters); section number and name at right, for example "2 - Methods". 1px #e3e1db rule under the header.
- Footer: page number at right, nothing at left. 1px #e3e1db rule above the footer.
- Header and footer text: IBM Plex Mono, uppercase, letter spacing 0.08em, colour #6f6b64.

## Cover page

Left statement with accent bar, the site layout (picker option A).

- Full-height 6px accent bar (#7a2e2e) on the left edge.
- Text block starts about one third down the page, left aligned: eyebrow "Data With Dillon" (IBM Plex Mono, uppercase, letter spacing 0.08em, #6f6b64), then the title (DM Sans 700, letter spacing -0.02em, line height 1.05, #111110, kept to a narrow block of about 9 to 13 characters per line; each format file gives its figure), then the subtitle (#44403b).
- Date at bottom left in IBM Plex Mono, uppercase, letter spacing 0.08em, #6f6b64.

## Callouts

Left accent bar, the site style (picker option A): 3px solid #7a2e2e left border, 12px left padding, 2px top and bottom padding, text #111110 at line height 1.45. No fill, no box. Each format file sets the callout limit (one per section, per page or per slide).

## Lists

Accent square bullet, matching the site mark (picker option A): a 6px square in #7a2e2e, set 4px in from the left, text indented 22px, 6px between items.

## Charts

Site palette (picker option A). Use the series in this order.

- Categorical: #7a2e2e, #4a4239, #b8893b, #4a6b3a, #5a7a8a, #5c3a1a
- Sequential, light to dark: #f3e7e4, #dfbfb8, #c4928a, #a6635b, #7a2e2e, #5c2020
- Diverging, oxblood to green: #7a2e2e, #b07a6e, #e3d3cc, #d4ddcb, #86a274, #4a6b3a
- Axis line: 1px #6f6b64. Captions: IBM Plex Mono, uppercase, letter spacing 0.08em, #6f6b64.

## Page setup

Normal margins (picker option A): portrait, single column, 2.54 cm on all four sides.

## Dates

Full dates are day, month, year with no ordinal and no leading zero: `3 November 2026`. Where only the month is shown (the Word cover date), write `November 2026`.

## Writing

The default voice is neutral third person. The request overrides it: when it asks for a voice, or the occasion clearly calls for one of the options below, use that. Ask only when an operator is available to answer.

- Plain, first person: "I looked at twelve months of sales and found that repeat customers drive most of the growth."
- Neutral, third person: "Twelve months of sales data show that repeat customers drive most of the growth."
- Formal corporate: "Data With Dillon has completed a comprehensive review of twelve months of sales data, which indicates that repeat customers are the principal driver of growth."

Voice is per document, not per brand. Plain first person for a personal note or a blog style post; neutral third person for a report, an analysis or anything with no named author; formal corporate for a client-facing or contractual document. One voice per document; never mix. A document type that needs a fourth voice gets a new option here, not a flag.

Punctuation: no em dash and no en dash; use a comma, a colon, a full stop or parentheses. Hyphens only inside compound words. Straight quotes in plain text files; typographic quotes only where the format file says so.

Plain prose: short sentences, one idea each; active voice; concrete nouns and numbers over adjectives; say the finding first, then the evidence.

Banned patterns, with the fix:

- Filler openers ("In today's fast-paced world", "It is important to note"): start with the finding.
- Summary closers ("In conclusion", "Overall,"): stop when the point is made.
- Stock words (delve, robust, leverage, seamless, crucial, landscape, journey, unlock, harness, tapestry, navigate): use the plain word.
- Lists padded to three items: list only the items there are.
- A bold label on every bullet: write the bullet as a sentence.
- Rhetorical questions: state the answer.
- "Not only X but also Y": write "X and Y".
- Exclamation marks: use a full stop.
- Stacked hedges ("may potentially"): one hedge at most, or a number.

The checkers fail on dashes, the stock words and the quoted phrases above.

Content honesty: do not invent numbers, names, sources or quotes. Mark missing data with the format's missing marker. A quote needs a real source, or it is not used.

Length: the document is as long as the content, never padded to a page count.
