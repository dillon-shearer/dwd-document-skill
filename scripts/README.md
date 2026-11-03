# Scripts

Build scripts for the templates in `assets/` live here. They target Python 3.10 and use the standard library, plus python-docx, python-pptx or openpyxl where needed.

## build_word.py

Builds `assets/dwd-template.docx` and `assets/dwd-sample.docx` from the rules in `references/word.md`. Run it from anywhere, with no arguments:

    python scripts/build_word.py

It needs python-docx. If it is missing the script installs it with `pip install python-docx`; you can also install it yourself first. Reruns overwrite both files, and the same input gives the same contents.

It also draws the sample's chart PNG with matplotlib. If matplotlib is missing the script installs it with `pip install matplotlib`. The PNG carries no software tag or timestamp, so reruns give the same image.

## check_docx.py

Checks a finished .docx against `references/word.md`. Run it with the file as the only argument:

    python scripts/check_docx.py path/to/file.docx

It prints one PASS or FAIL line per check and exits 1 on any FAIL. It checks that the file started from the template (every DWD style is defined), that no body run has a direct font, size or colour, that each Heading 1 reads "N - Name", that heading levels never skip, that every table uses DWD Table, has a Caption after it and marks row 1 as a header row, that number cells in body rows are right aligned, that the file name has no spaces, and that the cover date and header section text are not the template's "Month Year" and "1 - Section". It needs python-docx and installs it with pip if missing. `check.py` at the repo root runs it on `assets/dwd-sample.docx`.

## build_powerpoint.py

Builds `assets/dwd-template.pptx` and `assets/dwd-sample.pptx` from the rules in `references/powerpoint.md`. Run it from anywhere, with no arguments:

    python scripts/build_powerpoint.py

It needs python-pptx and XlsxWriter (python-pptx uses XlsxWriter to store chart data). If either is missing the script installs both with `pip install python-pptx XlsxWriter`; you can also install them yourself first. Reruns overwrite both files, and the same input gives the same contents.

## build_excel.py

Builds `assets/dwd-template.xlsx` and `assets/dwd-sample.xlsx` from the rules in `references/excel.md`. Run it from anywhere, with no arguments:

    python scripts/build_excel.py

It needs openpyxl. If it is missing the script installs it with `pip install openpyxl`; you can also install it yourself first. Reruns overwrite both files, and the same input gives the same contents.
