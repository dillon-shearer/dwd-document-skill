# Scripts

Build scripts for the templates in `assets/` live here. They target Python 3.10 and use the standard library, plus python-docx, python-pptx or openpyxl where needed.

## build_word.py

Builds `assets/dwd-template.docx` and `assets/dwd-sample.docx` from the rules in `references/word.md`. Run it from anywhere, with no arguments:

    python scripts/build_word.py

It needs python-docx. If it is missing the script installs it with `pip install python-docx`; you can also install it yourself first. Reruns overwrite both files, and the same input gives the same bytes.

## build_powerpoint.py

Builds `assets/dwd-template.pptx` and `assets/dwd-sample.pptx` from the rules in `references/powerpoint.md`. Run it from anywhere, with no arguments:

    python scripts/build_powerpoint.py

It needs python-pptx and XlsxWriter (python-pptx uses XlsxWriter to store chart data). If either is missing the script installs both with `pip install python-pptx XlsxWriter`; you can also install them yourself first. Reruns overwrite both files, and the same input gives the same bytes.

## build_excel.py

Builds `assets/dwd-template.xlsx` and `assets/dwd-sample.xlsx` from the rules in `references/excel.md`. Run it from anywhere, with no arguments:

    python scripts/build_excel.py

It needs openpyxl. If it is missing the script installs it with `pip install openpyxl`; you can also install it yourself first. Reruns overwrite both files, and the same input gives the same bytes.
