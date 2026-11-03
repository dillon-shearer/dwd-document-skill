# Excel

Rules for writing a .xlsx in the DWD brand. Read [brand.md](brand.md) first; this file maps those rules onto Excel.

## Start from the template

Open `assets/dwd-template.xlsx` (openpyxl: `load_workbook("assets/dwd-template.xlsx")`). It holds the named styles, the theme colours and fonts, one formatted sheet with the title block, a header row, print setup and the freeze pane. `assets/dwd-sample.xlsx` shows a filled sheet with a table and a chart. Apply the named styles; never format a cell by hand when a style exists.

To change the template, edit `scripts/build_excel.py` and run it. Do not edit the .xlsx files by hand.

## Fonts

| Role | Font | Office-safe fallback |
| --- | --- | --- |
| Title | DM Sans 700 | Segoe UI |
| Body, table cells | Aptos 11pt | Calibri |
| Eyebrow, date, captions, print header and footer | IBM Plex Mono | Consolas |

Excel has no per-cell fallback list. When the file goes to readers outside DWD and must look the same everywhere, change `HEAD_FONT`, `BODY_FONT` and `MONO_FONT` in the script to the fallback fonts and rebuild under a new file name. Never embed fonts.

## Named styles

Use only these cell styles. They show under Home > Cell Styles; openpyxl takes the same names (`cell.style = "DWD Text"`).

| Use | Style | Look |
| --- | --- | --- |
| Eyebrow (A1) | DWD Eyebrow | IBM Plex Mono 9pt, #6f6b64 |
| Sheet title (A2) | DWD Title | DM Sans 700, 20pt, #7a2e2e |
| Subtitle (A3) | DWD Subtitle | Aptos 12pt, #44403b |
| Date (A4) | DWD Date | IBM Plex Mono 9pt, #6f6b64, `d mmmm yyyy` |
| Table header row | DWD Header | Aptos 11pt bold, #7a2e2e fill, font colour Automatic |
| Text cells | DWD Text | Aptos 11pt, #111110, left, #e3e1db hairline below |
| Whole numbers | DWD Integer | as DWD Text, right, `#,##0` |
| Decimals | DWD Decimal | as DWD Text, right, `#,##0.0` |
| Percentages | DWD Percent | as DWD Text, right, `0.0%` |
| Dates in a table | DWD Date Cell | as DWD Text, right, `yyyy-mm-dd` |
| Total row | DWD Total | Aptos 11pt bold, right, `#,##0`, 1px #6f6b64 rule above |
| Table or chart label | DWD Caption | IBM Plex Mono 8pt, #6f6b64 |

Normal is Aptos 11pt #111110. Need another number format (currency, two decimals)? Copy the nearest style in the script under a new `DWD` name and rebuild; do not set formats cell by cell.

## Title block

Rows 1 to 4 of every sheet, in column A, no merged cells:

1. A1, DWD Eyebrow: "DWD - DATA WITH DILLON". The mark reads "DWD".
2. A2, DWD Title: the sheet title, short, sentence case.
3. A3, DWD Subtitle: one line on what the sheet holds.
4. A4, DWD Date: the date as a real date value, not text.

Row 5 stays empty. The table header row is row 6.

## Table header row

DWD Header: #7a2e2e fill, bold, left aligned, wrap on. The font colour is Automatic (`<color auto="1"/>`), never fixed white. Excel shows white text on the oxblood fill and keeps it readable when dark mode recolours the fill.

LibreOffice and Google Sheets do not do this contrast pick and may show dark text on the fill. That is expected; do not "fix" it to white. Only if the file must look right outside Excel, switch to fixed white and accept poor dark-mode contrast.

## Body rows

Hairline rule, no banding: each body cell has a 1px #e3e1db bottom border and no vertical rules. Do not fill body rows. Gridlines are off on every sheet. First column left aligned (DWD Text); number columns right aligned with a number style. One header row, no merged cells, no blank rows or columns inside a table. Put a DWD Caption cell in column A on the row under the table: "Table 1. Orders by region and quarter".

## Number and date formats

- Whole numbers: `#,##0`. Decimals: `#,##0.0`. Percentages: `0.0%`. Store values as numbers, never as text.
- Negatives with a minus sign, not brackets or red.
- Dates in tables: `yyyy-mm-dd`. Title block date: `d mmmm yyyy`.
- Keep one format per column.

## Column widths and freeze panes

- First column 24, number columns 14 (Excel character units). Widen to fit the longest entry plus 2, at most 40; wrap header text instead of going wider.
- Do not hide columns or rows.
- Freeze panes at A7 so the title block and header row stay in view (`ws.freeze_panes = "A7"`). For a table wider than the screen, freeze at B7 so the first column stays too.

## Print setup

Portrait, US Letter, 1 inch margins, fit to one page wide. Row 6 repeats on each printed page. Print header: "DWD" left, sheet name right; footer: page number right; all IBM Plex Mono 8pt #6f6b64. The template sets all of this.

## Charts

Use native Excel charts, not pictures. The theme accents are the brand series, so a new chart picks them up in order; set the series colours by hand when you build a chart in code:

1. #7a2e2e
2. #4a4239
3. #b8893b
4. #4a6b3a
5. #5a7a8a
6. #5c3a1a

For ordered data use the sequential series and for above/below data the diverging series, both in brand.md. Category axis line 1px #6f6b64, gridlines #e3e1db, no chart border, legend at the bottom, axis text 9pt #6f6b64. No chart title inside the chart: put a DWD Caption cell under it ("Figure 1. Orders by region and quarter"). Place charts below the table, starting in column A.

## Sheets

One table per sheet. Name sheets in one or two plain words ("Orders", "Notes"), no default "Sheet1" in a sent file. Each sheet gets the title block.

## Checklist before sending

- Started from `assets/dwd-template.xlsx`; cells use the DWD styles, no direct font, size or colour changes.
- Every sheet has the title block in A1:A4 and a real date in A4.
- Header row in DWD Header with font colour Automatic; body rows with the hairline rule, no fills.
- Numbers stored as numbers, right aligned, one format per column.
- Freeze pane under the header row; gridlines off; no merged or hidden cells.
- Every table and chart has a DWD Caption; chart colours follow the order above.
- Sheets named; no empty default sheets.
- File name has no spaces, for example `dwd-orders-by-region.xlsx`.
