# Word

Rules for writing a .docx in the DWD brand. Read [brand.md](brand.md) first; this file maps those rules onto Word.

## Start from the template

Open `assets/dwd-template.docx` (python-docx: `Document("assets/dwd-template.docx")`), delete its one empty body paragraph, then add content. The template already holds every style, the header, the footer, the page setup, the theme colours and the font fallbacks. `assets/dwd-sample.docx` shows every recipe below. Never restyle text by hand when a style exists: apply the style.

To change the template, edit `scripts/build_word.py` and run it. Do not edit the .docx files by hand.

## Starter

```python
from docx import Document
doc = Document("assets/dwd-template.docx")
empty = doc.paragraphs[0]._p
empty.getparent().remove(empty)
doc.add_paragraph("Data With Dillon", style="Cover Eyebrow")
doc.add_paragraph("Sales review", style="Title")
doc.add_paragraph("One line on what the document is", style="Subtitle")
doc.sections[0].first_page_footer.paragraphs[0].text = "November 2026"
h1 = doc.add_paragraph("1. Summary", style="Heading 1")
h1.paragraph_format.page_break_before = True
doc.sections[0].header.paragraphs[0]._p.xpath(".//w:fldSimple//w:t")[0].text = "1. Summary"
doc.save("dwd-sales-review.docx")
```

## Styles

Use only these styles. Names are as Word shows them; python-docx takes the same names.

| Use | Style | Look |
| --- | --- | --- |
| Cover title | Title | DM Sans 700, 44pt, #111110, right indent keeps it to 13 characters per line |
| Cover subtitle | Subtitle | Aptos 14pt, #44403b |
| Cover eyebrow | Cover Eyebrow | IBM Plex Mono 9pt, caps, #6f6b64 |
| Cover date | Cover Date | IBM Plex Mono 9pt, caps, #6f6b64 (first-page footer) |
| Section | Heading 1 | DM Sans 700, 21pt, #7a2e2e, 1px #6f6b64 rule below |
| Subsection | Heading 2 | DM Sans 700, 15pt, #7a2e2e |
| Minor heading | Heading 3 | DM Sans 700, 11.5pt, #7a2e2e |
| Body | Normal | Aptos 11pt, #111110, line 1.15, 6.6pt after |
| Bullets | List Bullet | #7a2e2e square bullet (see Lists) |
| Steps | List Number | #7a2e2e bold numbers |
| Quotation | Quote | Aptos 12pt italic, #44403b, indented both sides |
| Key point | Callout | 3px #7a2e2e left bar, no fill |
| Table or chart label | Caption | IBM Plex Mono 8pt, caps, #6f6b64 |
| Tables | DWD Table (table style) | see Tables |

Heading sizes are brand.md's 28px, 20px and 15px in points. Do not use Heading 4 or lower; split the section instead.

## Fonts

| Role | Font | Office-safe fallback |
| --- | --- | --- |
| Headings, title | DM Sans | Segoe UI |
| Body | Aptos | Calibri |
| Labels, header, footer, captions | IBM Plex Mono | Consolas |

The template's font table names each fallback (`altName`), so Word swaps it in when the brand font is missing. DM Sans, Aptos and IBM Plex Mono are not installed in agent sandboxes, so any render you make yourself shows fallback fonts; do not change the fonts in the styles because of it. When the file goes to readers outside DWD and must look the same everywhere, set the fallback fonts in the styles instead (change `HEAD_FONT`, `BODY_FONT` and `MONO_FONT` in the script and rebuild under a new file name). Never embed fonts.

## Page setup

US Letter, portrait, single column, 2.54 cm (1 inch) margins on all four sides. Header and footer sit 1.27 cm from the page edge. Do not add section breaks that change any of this.

## Header and footer

Page 1 is the cover and uses its own header and footer ("different first page" is on).

- Header, page 2 onward: the mark at left, which reads "DWD" (character style DW Mark: bold, #7a2e2e fill, font colour Automatic), a tab, then a `STYLEREF "Heading 1"` field that shows the current section. Rule below in #e3e1db. LibreOffice, Google Docs and docx-to-PDF converters can show Automatic text on the oxblood fill dark where Word shows it white; this is expected, so do not set a fixed colour.
- Footer, page 2 onward: a `PAGE` field at right, nothing at left. Rule above in #e3e1db.
- Cover header: empty. Cover footer: the date, style Cover Date, for example "November 2026".
- Header and footer text is IBM Plex Mono 8pt, caps, letter spacing 0.08em, #6f6b64. This comes from the Header and Footer styles; do not format it by hand.

Write each Heading 1 as number, full stop, space, name ("2. Methods") so the header reads like brand.md's example.

## Cover page recipe

1. Cover Eyebrow: "Data With Dillon". Its space before puts the block about one third down the page.
2. Title: the document title. Its right indent holds 13 characters per line, so a word of 13 letters fits on one line and a longer word breaks mid-word. Titles over about 26 characters wrap to three lines, so shorten them. When the brief fixes the title and a word is longer than 13 letters, hyphenate it at a syllable (end the first part with a hyphen, then a line break run: `run.add_break()`), or, when a long word sits badly next to its neighbours, put it on its own line with a line break run before it. `check_docx.py` fails `title-width` on any Title word over 13 characters.
3. Subtitle: one line on what the document is.
4. Put the date in the first-page footer, `doc.sections[0].first_page_footer.paragraphs[0]` (style Cover Date). The template holds the placeholder "Month Year" there, which prints as "MONTH YEAR" if you do not replace it.
5. Start the first Heading 1 on page 2 with `paragraph_format.page_break_before = True`. Do not add an empty paragraph or a page break run.

The 6px #7a2e2e bar on the left edge is a first-page-only left page border in the template. Keep it; do not draw a shape. LibreOffice may repeat it on later odd pages; Word does not. Leave it as is.

## Table recipe

1. Add the table and set `table.style = "DWD Table"`. Row 1 is the header row: #7a2e2e fill, bold text in font colour Automatic, repeats on each page. Also set `w:tblHeader` on row 1 yourself (`build_word.py` `add_table` shows how); do not rely on the style alone.
2. Body rows get a 1px #e3e1db rule below; there are no vertical rules. Cell padding is built in.
3. Left align the first column and every header cell. Right align number columns in the body rows.
4. Put a Caption paragraph under the table: "Table 1. Orders by quarter".
5. Keep one header row. Do not merge cells or add fills to body rows.

On a #7a2e2e fill, set the font colour to Automatic (`w:color w:val="auto"`), never fixed white. Word then shows white text on the oxblood fill, and dark text when Word dark mode lightens the fill, so the text stays readable in both. LibreOffice, Google Docs and docx-to-PDF converters show dark text on the oxblood fill; Word shows white. This is expected. Do not "fix" it by setting a fixed colour.

## Callout recipe

One short paragraph in style Callout for the one thing a reader must take away from a section. No fill, no box, no icon, no bold text inside. At most one callout per Heading 1 section.

## Lists

List Bullet gives the #7a2e2e square bullet with the text indented 22px and 6px between items. List Number gives #7a2e2e numbers with the same spacing. Use List Number only for steps or ranked items. The bullet num id is 90 and the number num id is 91 (each points at the abstractNum of the same id). Keep lists one level deep. To restart numbering, add a new `w:num` and put its numId on each paragraph of the new list:

```python
num = doc.part.numbering_part.element.add_num(91)
num.add_lvlOverride(ilvl=0).add_startOverride(1)
p = doc.add_paragraph("First step", style="List Number")
p._p.get_or_add_pPr().get_or_add_numPr().get_or_add_numId().val = num.numId
```

## Charts

The template's theme colours are the brand series, so a chart made in Word picks them up in order. When you colour a chart yourself, use the categorical series in this order:

1. #7a2e2e
2. #4a4239
3. #b8893b
4. #4a6b3a
5. #5a7a8a
6. #5c3a1a

For ordered data use the sequential series and for above/below data the diverging series, both in brand.md. Axis lines 1px #6f6b64. Label every chart with a Caption paragraph ("Figure 1. Repeat share by month"). Insert charts as PNG at the text width (6.5 in).

With matplotlib: figure 6.5 by 3.25 in, 200 dpi, transparent background, labels 8pt in #6f6b64, axis lines 1px (0.75pt) #6f6b64, no top or right spines, series colours in the order above. Insert with `doc.add_picture(path, width=Inches(6.5))`, then add a Caption paragraph. Leaving the picture paragraph in Normal is fine. `chart_png` in `build_word.py` is a worked example.

## Voice

Voice and prose: follow the Writing section in brand.md.

## Checklist before sending

- Started from `assets/dwd-template.docx`; no direct font, size or colour changes.
- Cover has eyebrow, title, subtitle and date; the first Heading 1 starts page 2.
- Headings go H1, H2, H3 in order with no skipped level; each H1 reads "N. Name".
- Every table uses DWD Table and has a caption; numbers are right aligned.
- At most one callout per Heading 1 section.
- Chart colours follow the order above.
- Header field set: write the first Heading 1 text into the STYLEREF field's cached run (as `set_header_footer` in `build_word.py` does). The template's updateFields setting makes Word and LibreOffice refresh STYLEREF and PAGE on open. If you skip this, any viewer that trusts the cached text shows "1. Section".
- Cover date replaced; "Month Year" is gone.
- `python scripts/check_docx.py your-file.docx` prints PASS on every line.
- File name has no spaces, for example `dwd-quarterly-sales-review.docx`.
