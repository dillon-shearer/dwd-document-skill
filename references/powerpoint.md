# PowerPoint

Rules for writing a .pptx in the DWD brand. Read [brand.md](brand.md) first; this file maps those rules onto PowerPoint.

## Start from the template

Open `assets/dwd-template.pptx` (python-pptx: `Presentation("assets/dwd-template.pptx")`) and add slides from its layouts. The template holds the slide size, the master, the seven layouts, the theme colours and fonts, and the DWD Table style. `assets/dwd-sample.pptx` uses each layout and each helper. No direct font, size or colour changes on placeholder text: the master and layouts set them. The helpers in `scripts/dwd_pptx.py` are the allowed exceptions for tables, charts, images and callouts; do not add others.

Slide size: 16:9 widescreen, 13.333 x 7.5 in (33.867 x 19.05 cm), side margins 0.6 in. Do not change it. To change the template, edit `scripts/build_powerpoint.py` and run it. Do not edit the .pptx files by hand.

## Helpers

`scripts/dwd_pptx.py` needs only python-pptx and lxml and does nothing at import. Add the scripts folder to the path, then import it: `sys.path.insert(0, "scripts")`, `import dwd_pptx`.

- `layout_named(prs, name)`: the layout with that name.
- `add_hf(slide, types, values)`: copies the footer (`"ftr"`), slide number (`"sldNum"`) or date (`"dt"`) placeholders onto the slide; `values` maps `"ftr"` and `"dt"` to their text.
- `set_lines(frame, lines, numbered=False)`: fills a text frame from `(level, text)` pairs; level 0 or 1. With `numbered=True` each level 0 item is numbered "1." "2." in #7a2e2e; level 1 items keep the dash.
- `add_table(slide, placeholder, rows, numeric_cols=None)`: a DWD Table in the placeholder's place. `numeric_cols` lists the column indexes to right align; left out, a column is numeric when every body cell is a number.
- `add_chart(placeholder, chart_type, data, palette="categorical")`: a native chart, styled; returns the graphic frame.
- `add_image(slide, path, caption)`: on the Picture layout, the picture fitted into the box with the caption as alt text and as the caption line.
- `add_callout(slide, placeholder, text, align="top")`: the brand callout in the placeholder's place. With `align="middle"` it sits level with the middle of the box.
- `set_core(prs, title)`: sets the title, author and fixed dates in the file properties.

## Starter

```python
import sys; sys.path.insert(0, "scripts")
import dwd_pptx as d
from pptx import Presentation
prs = Presentation("assets/dwd-template.pptx")
foot = {"ftr": "Sales review", "dt": "November 2026"}
s = prs.slides.add_slide(d.layout_named(prs, "Title"))
s.shapes.title.text = "Sales review"
s.placeholders[1].text = "One line on what the deck is"
d.add_hf(s, {"dt"}, foot)
s = prs.slides.add_slide(d.layout_named(prs, "Section"))
s.shapes.title.text = "1. Summary"
d.add_hf(s, {"ftr", "sldNum"}, foot)
s = prs.slides.add_slide(d.layout_named(prs, "Title and Content"))
s.shapes.title.text = "What changed"
d.set_lines(s.placeholders[1].text_frame, [(0, "Reminders went out after 30 days")])
d.add_hf(s, {"ftr", "sldNum"}, foot)
s = prs.slides.add_slide(d.layout_named(prs, "Closing"))
s.shapes.title.text = "Thank you"
prs.save("dwd-sales-review.pptx")
```

## Layouts

Use only these layouts, by name (`layout_named`).

| Layout | Use | Placeholders |
| --- | --- | --- |
| Title | First slide | title, subtitle (idx 1), date (idx 10) via `add_hf(slide, {"dt"}, {"dt": "November 2026"})` |
| Section | Start of each section | title "N. Name", one line of text (idx 1) |
| Title and Content | Most slides | title, content (idx 1) |
| Two Content | Side by side, for example a table and its points | title, left (idx 1), right (idx 2) |
| Chart | One chart per slide | title, chart (idx 13), caption (idx 14) |
| Picture | One image per slide | title, picture (idx 13), caption (idx 14) |
| Closing | Last slide | title, text (idx 1) |

Title and Closing have the 0.08 in (5.76pt) #7a2e2e bar on the left edge and the "Data With Dillon" eyebrow, like the cover page in brand.md. They have no footer. Every other layout has the footer.

## Fonts

| Role | Font | Office-safe fallback |
| --- | --- | --- |
| Titles | DM Sans 700 (theme heading font) | Segoe UI |
| Body, tables, charts | Aptos (theme body font) | Calibri |
| Eyebrow, footer, captions | IBM Plex Mono | Consolas |

The theme names DM Sans and Aptos, so text set to the theme fonts picks them up. On a machine without them PowerPoint substitutes a font; the fallback column is what readers outside DWD will most likely see. DM Sans, Aptos and IBM Plex Mono are not installed in agent sandboxes, so any render you make yourself shows fallback fonts; do not change the fonts in the theme because of it. Never embed fonts.

## Text sizes

| Text | Size | Colour |
| --- | --- | --- |
| Cover and closing title | 54pt bold, letter spacing -0.02em | #111110 |
| Section title | 40pt bold | #7a2e2e |
| Slide title | 28pt bold | #7a2e2e |
| Subtitle, section text | 20pt | #44403b |
| Body level 1 | 20pt | #111110 |
| Body level 2 | 18pt | #111110 |
| Table text | 16pt (14pt at the least) | #111110 |
| Chart labels | 12pt | #44403b |
| Eyebrow, date | IBM Plex Mono 12pt, caps | #6f6b64 |
| Footer, caption | IBM Plex Mono 9pt and 10pt, caps | #6f6b64 |

These come from the master and layouts; do not set them by hand.

## Titles

One line: about 50 characters at 28pt across the 12.1 in title box. If a title runs over, shorten it; if it cannot be shortened, split the slide; if neither works, say so in your reply. Never shrink the inherited size.

## Colours

- Slide background: Paper #fafaf8.
- Titles: Accent #7a2e2e. Cover and closing titles: Ink #111110.
- Body text: Ink #111110. Secondary text: Ink 2 #44403b. Labels, footer, captions: Ink 3 #6f6b64.
- Rules and table lines: #e3e1db, 0.75pt.
- Accent fills (mark, cover bar, table header): #7a2e2e.
- Chart series, in this order (theme Accent 1 to 6): #7a2e2e, #4a4239, #b8893b, #4a6b3a, #5a7a8a, #5c3a1a. The sequential and diverging series are in brand.md.

Text on an accent fill uses the theme colour Background 1 (`schemeClr bg1`), never a typed #ffffff. PowerPoint has no Automatic font colour like Word's, so the theme colour is the contrast-aware choice: it follows the theme instead of being fixed. The mark and the DWD Table header row already do this.

## Footer

Content layouts show a footer row at 6.98 in from the top, below a 0.75pt #e3e1db rule at 6.85 in. Left to right: the mark ("DWD" on a #7a2e2e square, IBM Plex Mono bold, on the master; do not add it again), the deck name in the footer placeholder (idx 11), for example "Quarterly sales review", and the slide number at right (idx 12, a slide number field).

python-pptx does not copy the footer and slide number placeholders onto new slides. Call `add_hf(slide, {"ftr", "sldNum"}, values)` on each content slide. The date shows only on the Title slide.

## Bullets

- Level 1 is a #7a2e2e square bullet; level 2 is a #6f6b64 dash. 6pt after each item. Keep to these two levels (python-pptx levels 0 and 1).
- At most six bullets per slide and about ten words per bullet. No full stop at the end of a bullet.
- For steps or ranked items use `set_lines(frame, lines, numbered=True)`. At most six items. The numbers come in the accent colour #7a2e2e from the helper; never type the numbers into the text.
- Use the Section layout, not a bullet, for a one-line statement.

## Tables

Use `add_table`. It puts the table where the placeholder sat, sets DWD Table (`{7A2E2E00-D0D0-4D0D-8000-000000000001}`) with the header row on and banded rows off, pads cells 4.5pt top and bottom and 6pt left and right, sets 16pt text, and aligns each header cell with its column: right over a numeric column, left otherwise, so the first column and its header are always left. Row height is the placeholder height divided by the row count, at least 0.5 in and at most 0.75 in, so a short table fills the content box and a full one keeps 0.5 in rows; text stays 16pt and centred vertically in each cell. Pass `numeric_cols` when a text column could pass for numbers; numbers are digits with optional `%`, `$`, `+`, `-`, commas, decimals or "pts". Header row: #7a2e2e fill, bold text in theme colour Background 1. Body rows: 0.75pt #e3e1db rule below, no vertical rules, no fills. One header row, no merged cells, at most 7 rows and 5 columns; split a bigger table.

## Charts

Use the Chart layout and `add_chart` with one of COLUMN_CLUSTERED, BAR_CLUSTERED, LINE, PIE or DOUGHNUT (`XL_CHART_TYPE`); other types raise ValueError. `palette` is `"categorical"`, `"sequential"` (ordered data) or `"diverging"` (above and below a midpoint), from brand.md. Column and bar get a set gap width; lines are 2.25pt with no markers; pie and doughnut colour each slice. Category axis line 0.75pt #6f6b64, value axis gridlines 0.75pt #e3e1db, legend at the bottom, no chart title. Put the label in the caption placeholder: "Figure 1. Orders by quarter". One chart per slide. Never paste chart images.

## Images

- Use the Picture layout and `add_image`. It scales the picture to fit the box, keeps the aspect ratio and left aligns it; never crop or stretch.
- PNG or JPG at least 150 dpi at the placed size. No borders, shadows, reflections or rounded frames.
- Every picture and chart has alt text (the caption text is fine). `add_image` sets it; for a chart, `frame._element.nvGraphicFramePr.cNvPr.set("descr", caption)`.

## Callouts

`add_callout` replaces a content placeholder with the brand.md callout: a 3pt #7a2e2e bar at the left edge and the text 12pt (0.17 in) to its right at the body level 1 size. No fill, no box. By default it sits at the top of the box. On Two Content, when the other column holds a table or chart, pass `align="middle"` so the callout sits level with the middle of the box; its height stays the same. At most one per slide, for the one thing the reader must take away. A callout never sits alone on a slide; see Fill the slide.

## Fill the slide

- A callout never sits alone. Put it on Two Content next to the numbers or bullets it comes from, or next to the chart it summarises, or make the finding the one line of text on the Section slide.
- A Title and Content slide holds at least three bullets, a table, or a callout plus bullets.
- Table beside a callout: the table fills the box and the callout sits level with its middle (`add_callout(..., align="middle")`).
- `check_deck.py` fails a table on Title and Content or Two Content with fewer than 7 rows whose rows are shorter than the box height divided by the row count (at most 0.75 in), within 1pt.
- `check_deck.py` fails a Title and Content or Two Content slide whose content holds fewer than three non-empty paragraphs (a callout counts as one) and no table, chart or picture.

## From brand.md

Applies: palette, typography, chart palettes, voice, lists, callouts. Does not apply: page setup, header and footer, cover page geometry, body text density; the sections in this file replace them.

## Voice

Voice and prose: follow the Writing section in brand.md.

## Checklist before sending

- The file started from `assets/dwd-template.pptx` (DWD Table style present).
- Every slide uses one of the seven layouts above.
- First slide uses Title, last slide uses Closing.
- Every slide but Title and Closing has the deck name in the footer and a slide number.
- No placeholder run has a direct font, size or colour.
- Every table uses DWD Table, fits 7 rows and 5 columns, has no merged cells, and right aligns numbers and the header cells over them.
- Fill the slide: no callout alone; every Title and Content or Two Content slide holds three paragraphs, a table, a chart or a picture.
- Content placeholders keep to six bullets and two levels.
- Numbered lists use `set_lines(..., numbered=True)`: numbers in #7a2e2e, none typed into the text.
- Every title is at most 55 characters.
- Every Chart slide holds a native chart and a caption; every Picture slide has alt text and a caption.
- File name has no spaces, for example `dwd-quarterly-sales-review.pptx`.
- Human check: each section starts with a Section slide ("N. Name"), every chart has alt text, and nothing sits outside the side margins or below the footer rule.
- `python scripts/check_deck.py file.pptx` passes.
