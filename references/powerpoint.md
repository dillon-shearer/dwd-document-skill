# PowerPoint

Rules for writing a .pptx in the DWD brand. Read [brand.md](brand.md) first; this file maps those rules onto PowerPoint.

## Start from the template

Open `assets/dwd-template.pptx` (python-pptx: `Presentation("assets/dwd-template.pptx")`) and add slides from its layouts. The template holds the slide size, the master, the six layouts, the theme colours and fonts, and the DWD Table style. `assets/dwd-sample.pptx` uses each layout once. Never restyle text by hand when a layout or placeholder already sets it.

To change the template, edit `scripts/build_powerpoint.py` and run it. Do not edit the .pptx files by hand.

## Slide size

16:9 widescreen, 13.333 x 7.5 in (33.867 x 19.05 cm). Side margins 0.6 in. Do not change the size.

## Layouts

Use only these layouts, by name (python-pptx: the layout whose `.name` matches).

| Layout | Use | Placeholders |
| --- | --- | --- |
| Title | First slide | title, subtitle (idx 1), date (idx 10) |
| Section | Start of each section | title "N - Name", one line of text (idx 1) |
| Title and Content | Most slides | title, content (idx 1) |
| Two Content | Side by side, for example a table and its points | title, left (idx 1), right (idx 2) |
| Chart | One chart per slide | title, chart (idx 13), caption (idx 14) |
| Closing | Last slide | title, text (idx 1) |

Title and Closing have the 6px #7a2e2e bar on the left edge and the "Data With Dillon" eyebrow, like the cover page in brand.md. They have no footer. Every other layout has the footer.

## Fonts

| Role | Font | Office-safe fallback |
| --- | --- | --- |
| Titles | DM Sans 700 (theme heading font) | Segoe UI |
| Body, tables, charts | Aptos (theme body font) | Calibri |
| Eyebrow, footer, captions | IBM Plex Mono | Consolas |

The theme names DM Sans and Aptos, so text set to the theme fonts picks them up. When the deck goes to readers outside DWD and must look the same everywhere, set `HEAD_FONT`, `BODY_FONT` and `MONO_FONT` in the script to the fallbacks and rebuild under a new file name. Never embed fonts.

## Text sizes

| Text | Size | Colour |
| --- | --- | --- |
| Cover and closing title | 54pt bold, letter spacing -0.02em | #111110 |
| Section title | 40pt bold | #7a2e2e |
| Slide title | 28pt bold | #7a2e2e |
| Subtitle, section text | 20pt | #44403b |
| Body level 1 | 20pt | #111110 |
| Body level 2 | 18pt | #111110 |
| Body level 3 | 16pt | #111110 |
| Table text | 16pt (14pt at the least) | #111110 |
| Chart labels | 12pt | #44403b |
| Eyebrow, date | IBM Plex Mono 12pt, caps | #6f6b64 |
| Footer, caption | IBM Plex Mono 9pt and 10pt, caps | #6f6b64 |

These come from the master and layouts; do not set them by hand. Keep titles to one line.

## Colours

- Slide background: Paper #fafaf8.
- Titles: Accent #7a2e2e. Cover and closing titles: Ink #111110.
- Body text: Ink #111110. Secondary text: Ink 2 #44403b. Labels, footer, captions: Ink 3 #6f6b64.
- Rules and table lines: #e3e1db.
- Accent fills (mark, cover bar, table header): #7a2e2e.
- Chart series, in this order (they are theme Accent 1 to 6):
  1. #7a2e2e
  2. #4a4239
  3. #b8893b
  4. #4a6b3a
  5. #5a7a8a
  6. #5c3a1a

For ordered data use the sequential series and for above/below data the diverging series, both in brand.md.

Text on an accent fill uses the theme colour Background 1 (`schemeClr bg1`), never a typed #ffffff. PowerPoint has no Automatic font colour like Word's, so the theme colour is the contrast-aware choice: it follows the theme instead of being fixed. The mark and the DWD Table header row already do this.

## Footer

Content layouts show, left to right, above a 1px #e3e1db rule:

- The mark: "DWD" on a #7a2e2e square, IBM Plex Mono bold. It is on the master; do not add it again.
- The deck name, in the footer placeholder (idx 11), for example "Quarterly sales review".
- The slide number at right (placeholder idx 12, a slide number field).

python-pptx does not copy the footer and slide number placeholders onto new slides. Copy them from the layout onto each slide, as `add_hf` in the script does, and put the deck name in the footer. The date shows only on the Title slide.

## Bullets

- Level 1 is a #7a2e2e square bullet; levels 2 and 3 are #6f6b64 dashes. 6pt after each item.
- Keep to two levels; use level 3 only when it cannot be avoided.
- At most six bullets per slide and about ten words per bullet. No full stop at the end of a bullet.
- Use the Section layout, not a bullet, for a one-line statement.

## Tables

1. Put the table where a content placeholder sits (same left, top and width) and remove the empty placeholder.
2. Set the table style to DWD Table (`{7A2E2E00-D0D0-4D0D-8000-000000000001}`), header row on, banded rows off.
3. Header row: #7a2e2e fill, bold text in theme colour Background 1, from the style. Body rows: 1px #e3e1db rule below, no vertical rules, no fills.
4. Cell padding 6px top and bottom, 8px left and right. Text 16pt.
5. Left align the first column and every header cell. Right align number columns in the body rows.
6. One header row. Do not merge cells. At most 7 rows and 5 columns; split a bigger table.

## Charts

1. Use the Chart layout and insert a native chart into placeholder idx 13 (python-pptx `insert_chart`). Do not paste chart images.
2. Fill series in the order above. Turn off series outlines.
3. Category axis line 1px #6f6b64. Value axis: no line, gridlines 1px #e3e1db.
4. Legend at the bottom; no chart title. Put the label in the caption placeholder: "Figure 1. Orders by quarter".
5. One chart per slide.

## Images

- PNG or JPG at least 150 dpi at their placed size; keep the aspect ratio, never stretch.
- Place inside the content area: 0.6 in side margins, below the title, above the footer rule.
- No borders, shadows, reflections or rounded frames.
- Put a caption (IBM Plex Mono, caps, #6f6b64) under any image that shows data.

## Voice

Pick the voice for each deck as brand.md's Voice section says. Ask when the occasion is unclear.

## Checklist before sending

- Started from `assets/dwd-template.pptx`; only the six layouts above are used.
- First slide uses Title, last slide uses Closing, and each section starts with Section ("N - Name").
- Every content slide shows the mark, the deck name and the slide number.
- No direct font, size or colour changes; text on accent fills uses theme colour Background 1.
- Bullets keep to two levels and six items.
- Every table uses DWD Table with numbers right aligned.
- Every chart is native, uses the series order above and has a caption.
- Nothing sits outside the side margins or below the footer rule.
- File name has no spaces, for example `dwd-quarterly-sales-review.pptx`.
