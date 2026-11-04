# Scripts

Build scripts for the templates in `assets/`, output checkers and the PowerPoint and Excel helper modules live here. They target Python 3.10 and use the standard library, plus python-docx, python-pptx or openpyxl where needed.

## build_word.py

Builds `assets/dwd-template.docx` and `assets/dwd-sample.docx` from the rules in `references/word.md`. Run it from anywhere, with no arguments:

    python scripts/build_word.py

It needs python-docx. If it is missing the script installs it with `pip install python-docx`; you can also install it yourself first. Reruns overwrite both files, and the same input gives the same contents.

It also draws the sample's chart PNG with matplotlib. If matplotlib is missing the script installs it with `pip install matplotlib`. The PNG carries no software tag or timestamp, so reruns give the same image.

## dwd_prose.py

The banned list from the Writing section of `references/brand.md`: em dash, en dash, the stock words and the quoted phrases. `find_banned(text)` returns a list of `(word, snippet)` pairs, and URLs in the text are skipped. Each checker imports it and adds a `prose` check that prints one FAIL line per hit, with the paragraph, slide, line, or sheet and cell. Code, URLs and table cells with no words (data) are skipped. It uses the standard library only and does nothing at import:

    import sys; sys.path.insert(0, "scripts")
    import dwd_prose

## check_docx.py

Checks a finished .docx against `references/word.md`. Run it with the file as the only argument:

    python scripts/check_docx.py path/to/file.docx

It prints one PASS or FAIL line per check and exits 1 on any FAIL. It checks that the file started from the template (every DWD style is defined), that no body run has a direct font, size or colour, that no word in a Title paragraph is longer than the 13 characters the Title box holds on one line (`TITLE_CHARS`, kept beside `TITLE_RIGHT_IND`, which `build_word.py` imports for the Title style), that each Heading 1 reads "N. Name", that heading levels never skip, that only the first Heading 1 has page break before and no paragraph holds a page break run, that every table uses DWD Table, has a Caption after it and marks row 1 as a header row, that number cells in body rows and the header cells over them are right aligned, that the file name has no spaces, and that the cover date and header section text are not the template's "Month Year" and "1. Section". It needs python-docx and installs it with pip if missing. `check.py` at the repo root runs it on `assets/dwd-sample.docx`.

## build_powerpoint.py

Builds `assets/dwd-template.pptx` and `assets/dwd-sample.pptx` from the rules in `references/powerpoint.md`. Run it from anywhere, with no arguments:

    python scripts/build_powerpoint.py

It needs python-pptx and XlsxWriter (python-pptx uses XlsxWriter to store chart data), and matplotlib for the sample's picture. If any is missing the script installs it with pip; you can also install them yourself first. It imports its helpers from `dwd_pptx.py`. Reruns overwrite both files and give the same contents, not the same bytes: on one machine the bytes match run to run, but other library versions can write different bytes.

## dwd_pptx.py

The helpers agents use to build a deck from the template: `layout_named`, `add_hf`, `set_lines` (with `numbered=True` for a numbered list), `add_table`, `add_chart`, `add_image`, `add_callout` and `set_core`. `references/powerpoint.md` documents each one. It needs only python-pptx and lxml, installs nothing and does nothing at import:

    import sys; sys.path.insert(0, "scripts")
    import dwd_pptx

## check_deck.py

Checks a finished .pptx against `references/powerpoint.md`. Run it with the file as the only argument:

    python scripts/check_deck.py path/to/file.pptx

It prints one PASS or FAIL line per check and exits 1 on any FAIL. It checks that the file started from the template (the DWD Table style is defined), that every slide uses a DWD layout, that the deck opens with Title and ends with Closing, that content slides carry the footer and slide number, that no placeholder run has a direct font, size or colour, that tables use DWD Table, fit 7 by 5, have no merged cells and right align numbers and the header cells over number columns, that bullets keep to six items and two levels, that numbered paragraphs (`a:buAutoNum`) have a #7a2e2e `a:buClr` and no level 0 text starts with a typed "1." or "1)" number (Section slide titles, which read "N. Name", excepted), that titles are at most 55 characters, that Chart and Picture slides have their chart or alt-texted picture and a caption, that every Title and Content or Two Content slide holds three non-empty paragraphs (a callout counts) or a table, chart or picture, and that the file name has no spaces. It needs python-pptx and installs it with pip if missing. `check.py` at the repo root runs it on `assets/dwd-sample.pptx`.

## build_excel.py

Builds `assets/dwd-template.xlsx` and `assets/dwd-sample.xlsx` from the rules in `references/excel.md`. Run it from anywhere, with no arguments:

    python scripts/build_excel.py

It needs openpyxl. If it is missing the script installs it with `pip install openpyxl`; you can also install it yourself first. It imports its styles and helpers from `dwd_excel.py`. Reruns overwrite both files and give the same contents, not the same bytes: on one machine the bytes match run to run, but other library versions can write different bytes.

## dwd_excel.py

The helpers agents use to build a workbook from the template: `setup_sheet`, `new_sheet`, `set_widths`, `add_table`, `add_chart`, `chart_text`, `finish` and `save` (writes each formula's cached value so Protected View shows numbers), plus the brand constants and the `styles` list. `references/excel.md` documents each one. It needs only openpyxl, installs nothing and does nothing at import:

    import sys; sys.path.insert(0, "scripts")
    import dwd_excel

## check_xlsx.py

Checks a finished .xlsx against `references/excel.md`. Run it with the file as the only argument:

    python scripts/check_xlsx.py path/to/file.xlsx

It prints one PASS or FAIL line per check, naming the sheet and cell or chart on FAIL, and exits 1 on any FAIL. It checks that the file started from the template (all seventeen DWD named styles and the DWD theme colours), that every sheet has the title block in A1:A4 with a real date in A4 and an empty row 5, that every cell from row 6 down uses a DWD style with no direct font, fill or number format, that row 7 is in DWD Header with font colour Automatic, that each body column keeps one style and number cells hold numbers, that no total row sums a percent column or leaves a percent total in DWD Percent instead of DWD Total Percent, that there are no merged cells or hidden rows and columns, the freeze pane, gridlines, print titles, fit to one page wide and the DWD print header, that every table has a DWD Table Title in column A directly above its header row, that every table and chart has a "Table N." or "Figure N." caption, that chart series use brand colours and have no titles, that a sheet named Notes holds one table whose column A labels are Note, Key point, Warning, Summary, Quote, Step N in order from 1 or a one or two word topic, with at most one Key point, that `fullCalcOnLoad` is set when there are formulas, that every formula cell has a cached value (it loads the file again with `data_only=True`), and that no sheet is named Sheet or Sheet1 and the file name has no spaces. It needs openpyxl and installs it with pip if missing. `check.py` at the repo root runs it on `assets/dwd-sample.xlsx`.

## check_md.py

Checks a finished .md file against `references/markdown.md`. Run it with the file as the only argument:

    python scripts/check_md.py path/to/file.md

It prints one PASS or FAIL line per check, with the line number on FAIL, and exits 1 on any FAIL. It checks that the file is UTF-8 with LF endings and one final newline, that lines 1 to 5 are the eyebrow, a blank line, the only H1, a blank line and the italic subtitle with a `3 November 2026` style date, that there is no front matter, that headings stop at H3 and never skip a level, that H2 headings are all numbered in order from 1 or none are, that headings have no trailing punctuation, bold or links, that bullets use `-`, that every table has a `**Table N. ...**` label, a `---` or `---:` separator and no empty cells, that every image has alt text, a `**Figure N. ...**` label line above it numbered in order from 1 and a relative path to a file that exists, that every code fence has a language tag, that callouts use `Note`, `Key point` or `Warning` with at most one per H2 section and no `[!NOTE]` alerts, that there is no HTML, and that relative links resolve and `#fragment` links match a heading. Fenced code and inline code are skipped for the marker, HTML, link and figure checks. It uses the standard library only and does nothing at import. `check.py` at the repo root runs it on `assets/dwd-sample.md`.

## check_html.py

Checks a finished .html file against `references/html.md`. Run it with the file as the only argument:

    python scripts/check_html.py path/to/file.html

It prints one PASS or FAIL line per check, with the line number on FAIL, and exits 1 on any FAIL. It checks that the file is UTF-8 with LF endings and one final newline; the `lang`, charset, viewport and color-scheme metas and a title ending in " - DWD"; that there is no script, no link except the Google Fonts stylesheet and its two preconnects, and no remote image; that there is one `<style>` block and it starts with the stylesheet of `assets/dwd-report.html` unchanged; that the only `style` attribute is a width on `.bar`; that no brand hex appears outside `:root`, `@page` and inline SVG; that every mark reads "DWD"; that headings stop at h3 and never skip, and h1 sections are numbered from 1, each right after a `header.doc-header` with the same number; that there is no `.doc-footer`; that tables have a "Table N." caption line, `aria-labelledby`, a `thead` and `scope="col"`, and figures a "Figure N." caption; that no cell is empty and number cells and their header carry `num`; that callouts use Note, Key point or Warning, at most one per h1 section; that charts and SVG have `role="img"` and SVG a `<title>` and `<desc>`; that quotes have a `p` and a `footer`; and that there is no bare `&` or `<` in text. It uses the standard library only and does nothing at import. The only repo file it reads is `assets/dwd-report.html`, for the reference stylesheet.

The last line, `print-render`, is optional and kept apart from the structural checks. When Chrome, Edge or Chromium is on PATH or in the usual Windows install folders, the script prints the file to a temporary PDF with `--headless=new --print-to-pdf --no-pdf-header-footer` in a throwaway profile and reports the page count. It prints SKIP when no browser is found, when the browser cannot start, or when it does not finish in 60 seconds (`PRINT_TIMEOUT`); then print to PDF by hand. It prints FAIL only when the browser exits and writes no PDF. `check.py` at the repo root runs the script on `assets/dwd-report.html`.
