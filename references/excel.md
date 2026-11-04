# Excel

Rules for writing a .xlsx in the DWD brand. Read [brand.md](brand.md) first; this file maps those rules onto Excel.

## Start from the template

Open `assets/dwd-template.xlsx` (openpyxl: `load_workbook("assets/dwd-template.xlsx")`). It holds the named styles, the theme colours and fonts, and one formatted sheet named "Sheet1" with the title block, a table title row, a header row, print setup and the freeze pane. Rename that sheet before you fill it. `assets/dwd-sample.xlsx` shows every helper below in use: a table with a total and a chart, a notes sheet, a trend sheet with a line chart and a raw data sheet. Apply the named styles; never format a cell by hand when a style exists.

To change the template, edit `scripts/build_excel.py` and run it. Do not edit the .xlsx files by hand.

## Helpers

`scripts/dwd_excel.py` needs only openpyxl and does nothing at import. Add the scripts folder to the path, then import it: `sys.path.insert(0, "scripts")`, `import dwd_excel`. It also holds the brand constants (fonts, `INK`, `ACCENT`, `CHART`, `SEQUENTIAL`, `DIVERGING`, `FMT_INT`, `TITLE_ROW`, `HEADER_ROW` and the rest).

- `setup_sheet(ws, name, title, subtitle, when, landscape=False)`: renames a sheet and sets the title block, row heights, freeze pane, gridlines off, print setup, print titles and header and footer.
- `new_sheet(wb, name, title, subtitle, when, landscape=False)`: a new sheet with all of `setup_sheet` applied; returns it. `landscape` flips the orientation only.
- `set_widths(ws, widths)`: column widths from column A, in Excel character units. Set them before `add_table`.
- `add_table(ws, heads, rows, styles, first_row=HEADER_ROW, total=None, caption=None, autofilter=False, title=None)`: `title` in DWD Table Title in column A on the row above the header row, header row, body rows with one style name per column in `styles`, an optional total row, the caption on the next row, and an AutoFilter on header and body when `autofilter` is true. `total` is the label, or a list with the label first and one entry per column: `None` for the default (SUM for integer and decimal columns, empty otherwise), `""` for empty, or a formula. Any body or total cell can be a `(formula, value)` pair: the formula goes in the cell and `value`, computed in Python, is kept for `save` to write as the cached result. A default SUM total gets its value from the body rows. In formulas `{row}`, `{first}` and `{last}` become the current, first body and last body row. Clears leftover template header cells to the right of `heads`, and the template's table title when `title` is not given. Raises the header row to 30 when a header is longer than its column or holds a newline. Returns `(first_body_row, last_body_row, next_free_row)`.
- `add_chart(ws, kind, first, last, ncols, anchor, palette="categorical", label_col=1)`: a native chart over body rows `first` to `last`, labels in `label_col`, series in the next `ncols - 1` columns. `kind` is "column", "bar" or "line"; the legend sits at the top and does not overlay the plot area. Returns the chart.
- `chart_text(size, color, bold=False)`: the rich text block the charts use for axis and legend text.
- `finish(wb)`: sets `fullCalcOnLoad` and drops any empty sheet still named "Sheet" or "Sheet1".
- `save(wb, path)`: calls `finish`, saves with openpyxl, then writes each pair's value into its formula cell as the cached value. Use it instead of `wb.save`.

## Starter

```python
import sys; sys.path.insert(0, "scripts")
import dwd_excel as d
from datetime import date
from openpyxl import load_workbook
wb = load_workbook("assets/dwd-template.xlsx")
ws = wb.active
d.setup_sheet(ws, "Orders", "Orders by region", "Order count per region, 2026", date(2026, 11, 3))
d.set_widths(ws, [24, 14, 14])
first, last, nxt = d.add_table(ws, ["Region", "Q1", "Q2"], [["North", 1240, 1315], ["South", 980, 1022]],
    ["DWD Text", "DWD Integer", "DWD Integer"], total="Total", caption="Table 1. Orders by region",
    title="Orders by region")
d.add_chart(ws, "column", first, last, 3, f"A{nxt + 1}")
ws.cell(row=nxt + 19, column=1, value="Figure 1. Orders by region").style = "DWD Caption"
d.save(wb, "dwd-orders-by-region.xlsx")
```

## Fonts

| Role | Font | Office-safe fallback |
| --- | --- | --- |
| Title | DM Sans 700 | Segoe UI |
| Body, table cells | Aptos 11pt | Calibri |
| Eyebrow, date, captions, print header and footer | IBM Plex Mono | Consolas |

Excel has no per-cell fallback list; on a machine without a brand font it substitutes one. DM Sans, Aptos and IBM Plex Mono are not installed in agent sandboxes, so any render you make yourself shows fallback fonts; do not change the fonts in the template because of it. Never embed fonts.

This file overrides generic xlsx guidance on fonts (Arial or Times): DWD workbooks use the template fonts.

## Named styles

Use only these cell styles. They show under Home > Cell Styles; openpyxl takes the same names (`cell.style = "DWD Text"`).

| Use | Style | Look |
| --- | --- | --- |
| Eyebrow (A1) | DWD Eyebrow | IBM Plex Mono 9pt, #6f6b64 |
| Sheet title (A2) | DWD Title | DM Sans 700, 20pt, #7a2e2e |
| Subtitle (A3) | DWD Subtitle | Aptos 12pt, #44403b |
| Date (A4) | DWD Date | IBM Plex Mono 9pt, #6f6b64, `d mmmm yyyy` |
| Table header row | DWD Header | Aptos 11pt bold, #7a2e2e fill, font colour Automatic |
| Text cells | DWD Text | Aptos 11pt, #111110, left, thin #e3e1db rule below |
| Long text cells | DWD Text Wrap | as DWD Text, wrap on, top aligned |
| Whole numbers | DWD Integer | as DWD Text, right, `#,##0` |
| Decimals | DWD Decimal | as DWD Text, right, `#,##0.0` |
| Percentages | DWD Percent | as DWD Text, right, `0.0%` |
| Dates in a table | DWD Date Cell | as DWD Text, right, `yyyy-mm-dd` |
| Total row label | DWD Total Label | Aptos 11pt bold, left, thin #6f6b64 rule above |
| Whole number total | DWD Total Integer | as DWD Total Label, right, `#,##0` |
| Decimal total | DWD Total Decimal | as DWD Total Label, right, `#,##0.0` |
| Percent total | DWD Total Percent | as DWD Total Label, right, `0.0%` |
| Table title (row above the header) | DWD Table Title | Aptos 11pt bold, #7a2e2e, left, no border |
| Table or chart label | DWD Caption | IBM Plex Mono 8pt, #6f6b64 |

Normal is Aptos 11pt #111110. A text column whose entries would need a width over 40 uses DWD Text Wrap at width 40. Need another number format (currency, two decimals)? Copy the nearest style in the script under a new `DWD` name and rebuild; do not set formats cell by cell.

## Title block

Rows 1 to 4 of every sheet, in column A, no merged cells:

1. A1, DWD Eyebrow: "DWD - DATA WITH DILLON". The mark reads "DWD".
2. A2, DWD Title: the sheet title, short, sentence case.
3. A3, DWD Subtitle: one line on what the sheet holds, with the data source and units when the caption does not give them.
4. A4, DWD Date: the date as a real date value, not text.

Row 5 stays empty. Row 6 is the table title, in DWD Table Title in A6 (`add_table(..., title=...)`): a short name for the table, sentence case, no "Table N." number. The table header row is row 7. The title row sits outside the frozen and printed rows, so the freeze pane and print titles name the header row alone.

## Table header row

Row 7. DWD Header: #7a2e2e fill, bold, left aligned, wrap on. The font colour is Automatic (`<color auto="1"/>`), never fixed white. Excel shows white text on the oxblood fill and keeps it readable when dark mode recolours the fill. The template row is 22 high; `add_table` makes it 30 when a header wraps.

LibreOffice and Google Sheets do not do this contrast pick and may show dark text on the fill. That is expected; do not "fix" it to white. Only if the file must look right outside Excel, switch to fixed white and accept poor dark-mode contrast.

## Body rows and totals

No banding: each body cell has a thin #e3e1db bottom border (Excel border style `thin`, openpyxl `Side(style="thin")`) and no vertical rules. Do not fill body rows. Gridlines are off on every sheet. First column left aligned (DWD Text); number columns right aligned with a number style. One header row, no merged cells, no blank rows or columns inside a table. Every table has a DWD Table Title cell in column A directly above its header row, and keeps a DWD Caption cell in column A on the row under the table, or under the total row: "Table 1. Orders by region and quarter".

A total row puts its label in DWD Total Label and each total in the Total style matching the column (DWD Total Integer, DWD Total Decimal or DWD Total Percent), with a thin #6f6b64 rule above. A percent column total is a ratio formula (total numerator over total denominator) in DWD Total Percent, never a SUM of percentages and never plain DWD Percent. A date column total stays empty.

## Number and date formats

- Whole numbers: `#,##0`. Decimals: `#,##0.0`. Percentages: `0.0%`. Store values as numbers, never as text.
- Percentages are stored as fractions: 0.173 shows as 17.3%.
- Negatives with a minus sign, not brackets or red.
- Dates in tables: `yyyy-mm-dd`. Title block date: `d mmmm yyyy`.
- Keep one format per column. Say the units in A3 or the caption ("$ millions").

## Formulas and data

- Calculated cells stay formulas, and every formula is written with its computed value: pass a `(formula, value)` pair to `add_table` and save with `save`. Excel opens any file from email or a download in Protected View, which does not recalculate, so a formula with no cached value shows blank there, and so does any chart that reads it. `fullCalcOnLoad` stays set, so Excel recomputes once editing is enabled. Example: `("=E{row}/SUM(B{row}:E{row})", q4 / year)`.
- A blank cell means missing; 0 means zero. Never swap them.
- Note the data source and units in A3 or the caption.
- Do not re-save the file through LibreOffice to recalculate it. It drops the Automatic header colour, reorders the named styles so openpyxl cannot resolve them, and rewrites the theme. If cached values are needed, compute them in Python and write both.

## Column widths and freeze panes

- First column 24, number columns 14 (Excel character units). Widen to fit the longest entry plus 2, at most 40; wrap header text and long text instead of going wider.
- Do not hide columns or rows.
- Freeze panes at A8 so the title block, table title and header row stay in view (`ws.freeze_panes = "A8"`). For a table wider than the screen, freeze at B8 so the first column stays too.

## Print setup

Portrait, US Letter, 1 inch margins, fit to one page wide. Row 7, the header row, repeats on each printed page. Print header: "DWD" left, sheet name right; footer: page number right; all IBM Plex Mono 8pt #6f6b64. The template and `new_sheet` set all of this.

## Sheets

Name sheets in one or two plain words ("Orders", "Notes"), no default "Sheet1" in a sent file. Each sheet gets the title block. For a second sheet use `new_sheet`; never `copy_worksheet`, which drops the sheet view, the header and footer and the print titles.

## Notes sheet

Prose that is not tabular data (sources, definitions, callouts, lists, quotes, a summary) goes on a sheet named Notes, as one two-column table and nothing else:

- Heads `["Label", "Note"]`, styles `["DWD Text", "DWD Text Wrap"]`, widths `[24, 60]` (the one place a text column is wider than 40), title "Notes", caption "Table N. Notes".
- One item per row, with its label in column A:
  - `Note`, `Key point` or `Warning` for a callout. At most one `Key point` per sheet.
  - `Step 1`, `Step 2`, ... for a numbered list, in order from 1.
  - A short topic word or two for a bullet item ("Source", "Returns").
  - `Quote` for a quote: the quote text in straight quotes, then the source, in the Note cell.
  - `Summary` for a summary paragraph.
- No merged cells, no blank rows, no text outside the table.

```python
ws = d.new_sheet(wb, "Notes", "Notes on the data", "Sources, definitions and known gaps", date(2026, 11, 3))
d.set_widths(ws, [24, 60])
d.add_table(ws, ["Label", "Note"], [["Key point", "Online grew fastest."], ["Source", "Order system export."],
    ["Step 1", "Export the order lines."], ["Quote", '"Returns are booked on arrival." Finance team']],
    ["DWD Text", "DWD Text Wrap"], caption="Table 2. Notes", title="Notes")
d.save(wb, "dwd-orders-by-region.xlsx")
```

## Wide sheets

The default is one table per sheet, portrait, one page wide. These exceptions are allowed; state each in the subtitle or caption:

1. More than about eight columns: landscape via `new_sheet(..., landscape=True)`, freeze at B8.
2. A raw data sheet: no chart, DWD styles on every column, AutoFilter on the header row (`autofilter=True`), no native Excel Table, the row count in the subtitle.
3. More than one table on a sheet: each has its own title row directly above its header row (pass `first_row` as the header row; the title goes on the row above) and its own caption, two empty rows between one table's caption and the next table's title, numbered Table 1, Table 2.
4. A dashboard sheet: tables and charts side by side in column blocks, only when each block keeps its caption and the sheet still prints one page wide in landscape.

Never hide, merge or shrink text to fit.

## Charts

Use native Excel charts, not pictures. `add_chart` makes three kinds: column, bar and line. Line charts get 2.25pt lines and no markers. The theme accents are the categorical series, so a new chart picks them up in order: #7a2e2e, #4a4239, #b8893b, #4a6b3a, #5a7a8a, #5c3a1a.

Three palettes, from brand.md: categorical (above) by default; sequential for ordered bands such as years or size bands (with fewer than six series it uses the darkest ones, light to dark); diverging for signed values around a zero baseline (the category axis crosses at 0, labels stay at the bottom). Never colour unrelated categories with the sequential series. Category axis line 9525 EMU (0.75pt) #6f6b64, gridlines 9525 EMU #e3e1db, no chart border, legend at the top (`legendPos t`) with overlay off (`overlay 0`) so it never sits on the plot area or the category axis labels, axis text 9pt #6f6b64. No chart title inside the chart: put a DWD Caption cell under it ("Figure 1. Orders by region and quarter"). Place charts below the table, starting in column A.

## Voice

Voice and prose: follow the Writing section in brand.md.

## Checklist before sending

Each line is one `check_xlsx.py` check unless marked human.

- Started from the template: all seventeen DWD named styles and the DWD theme colours are present.
- Every sheet has the title block in A1:A4, a real date in A4 and an empty row 5.
- Every cell from row 6 down uses a DWD style, with no direct font, fill or number format.
- Row 7 is in DWD Header with font colour Automatic.
- Each body column uses one style; number and date cells hold numbers or dates, not text.
- No total row sums a percent column; a percent total is in DWD Total Percent.
- No merged cells, no hidden rows or columns.
- Every sheet: freeze pane at A8 or B8, gridlines off, print titles row 7, one page wide, "DWD" in the print header.
- Every table has a DWD Table Title in column A directly above its header row.
- Every table has a "Table N." caption; every chart has a "Figure N." caption below it.
- Chart series use brand colours; no chart titles.
- A Notes sheet holds one table; column A labels are Note, Key point, Warning, Summary, Quote, Step N or a one or two word topic; Step rows run in order from 1; at most one Key point.
- `fullCalcOnLoad` is set when the workbook holds formulas.
- Every formula cell carries a cached value, so Protected View shows numbers and charts.
- No sheet named Sheet or Sheet1; file name has no spaces, for example `dwd-orders-by-region.xlsx`.
- Human: the palette fits the data (sequential for ordered, diverging for signed), blanks mean missing, sources and units are stated.
- `python scripts/check_xlsx.py file.xlsx` passes.
