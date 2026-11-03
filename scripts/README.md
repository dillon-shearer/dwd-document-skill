# Scripts

Build scripts for the templates in `assets/` live here. They target Python 3.10 and use the standard library, plus python-docx or python-pptx where needed.

## build_word.py

Builds `assets/dwd-template.docx` and `assets/dwd-sample.docx` from the rules in `references/word.md`. Run it from anywhere, with no arguments:

    python scripts/build_word.py

It needs python-docx. If it is missing the script installs it with `pip install python-docx`; you can also install it yourself first. Reruns overwrite both files, and the same input gives the same bytes.
