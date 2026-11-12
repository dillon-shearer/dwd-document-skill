# Brand

Shared brand rules for every DWD deliverable. Read this before any format file.

## Palette

Oxblood and paper, the site palette (picker option A). These values equal `styles/tokens.css` on the Data With Dillon site.

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

Two faces, the same as the site.

- Headings: Schibsted Grotesk 600, fallback 'Segoe UI', system-ui, sans-serif. Office files have no 600 weight, so they use Schibsted Grotesk bold.
- Body, labels, captions, header and footer text, table text and numbers: Inter 400 (500 for the wordmark and the mark), fallback 'Segoe UI', system-ui, sans-serif.
- No monospace face for labels, metadata or numbers. Use tabular figures for numbers where the format allows. Code samples alone may use the viewer's monospace (ui-monospace, Consolas, 'Courier New', monospace); it is never loaded as a brand font.

## Labels and wordmark

- Labels, eyebrows, captions, buttons, metadata, table headers, panel titles, header and footer text: sentence case, normal letter spacing. Never all caps, never small caps, never added letter spacing.
- The single exception is the wordmark "Data With Dillon": Inter 500, 12px (9pt), uppercase, letter spacing 0.1em, "Data With" in ink #111110 and "Dillon" in accent #7a2e2e. Use it only where a format file says, and do not reuse its style for anything else.
- No eyebrow that only repeats the title. No numbered index columns (01, 02) on lists.
- No role-first tagline (such as "Data analyst and engineer") on covers or headers, and no slogan lines.

## Headings

Mix of picker options C and E: accent-coloured headings, with a thin rule under H1 only.

- All heading levels: Schibsted Grotesk 600, sentence case, colour #7a2e2e, line height 1.15, letter spacing -0.01em.
- H1: 28px, with a 1px #6f6b64 rule below, 6px padding under the text and 8px margin under the rule.
- H2: 20px, no rule.
- H3: 15px, no rule.

## Body text

Office default density (picker option D): 11pt / 1.15 line height, colour #111110, paragraph spacing 0.6em. Inter, fallback 'Segoe UI', system-ui, sans-serif.

Bold marks a key term on first use only. That rule does not cover structural labels such as table label lines and callout labels, which are bold every time.

## Tables

Header fill, white text (picker option B).

- Header row: background #7a2e2e, text #ffffff, weight 600, sentence case, left aligned.
- Body rows: 1px #e3e1db bottom rule, no vertical rules.
- Cell padding 6px 8px; first column left aligned, number columns right aligned, tabular figures.

## Header and footer

The mark reads "DWD" everywhere.

Mark left, section right, the site layout (picker option A).

- Header: DWD mark at left (square, background #7a2e2e, white Inter 500 letters); section number and name at right, for example "2. Methods". 1px #e3e1db rule under the header.
- Footer: page number at right, nothing at left. 1px #e3e1db rule above the footer.
- Header and footer text: Inter, sentence case, normal letter spacing, colour #6f6b64.

## Cover page

Left statement with accent bar, the site layout (picker option A).

- Full-height 6px accent bar (#7a2e2e) on the left edge.
- Text block starts about one third down the page, left aligned: the wordmark "Data With Dillon" (see Labels and wordmark), then the title (Schibsted Grotesk 600, letter spacing -0.02em, line height 1.05, #111110, kept to a narrow block of about 9 to 13 characters per line; each format file gives its figure), then the subtitle (#44403b), a plain line on what the document is.
- Date at bottom left in Inter, sentence case, normal letter spacing, #6f6b64.

## Callouts

Left accent bar, the site style (picker option A): 3px solid #7a2e2e left border, 12px left padding, 2px top and bottom padding, text #111110 at line height 1.45. No fill, no box. Each format file sets the callout limit (one per section, per page or per slide).

## Lists

Accent square bullet, matching the site mark (picker option A): a 6px square in #7a2e2e, set 4px in from the left, text indented 22px, 6px between items.

## Charts

Site palette (picker option A). Use the series in this order.

- Categorical: #7a2e2e, #4a4239, #b8893b, #4a6b3a, #5a7a8a, #5c3a1a
- Sequential, light to dark: #f3e7e4, #dfbfb8, #c4928a, #a6635b, #7a2e2e, #5c2020
- Diverging, oxblood to green: #7a2e2e, #b07a6e, #e3d3cc, #d4ddcb, #86a274, #4a6b3a
- Axis line: 1px #6f6b64. Captions and axis labels: Inter, sentence case, normal letter spacing, #6f6b64.

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
