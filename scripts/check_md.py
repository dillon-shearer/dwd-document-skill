import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dwd_prose

EYEBROW = "`DWD / DATA WITH DILLON`"
MONTHS = "January|February|March|April|May|June|July|August|September|October|November|December"
SUBTITLE_RE = re.compile(r"^\*(?!\*)\S.* - ([1-9]|[12][0-9]|3[01]) (" + MONTHS + r") \d{4}\*$")
FENCE_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
HEADING_RE = re.compile(r"^ {0,3}(#{1,6})(?:[ \t]+(.*?))?(?:[ \t]+#+)?[ \t]*$")
INLINE_CODE_RE = re.compile(r"(`+)(?!`).*?(?<!`)\1(?!`)")
LINK_RE = re.compile(r"!?\[[^\]]*\]\(\s*<?([^)\s>]*)>?(?:\s+\"[^\"]*\")?\s*\)")
HTML_RE = re.compile(r"<!--|</?[A-Za-z][A-Za-z0-9-]*(?:\s[^<>]*)?/?>")
TABLE_LABEL_RE = re.compile(r"^\*\*Table \d+\. \S.*\*\*$")
FIGURE_LABEL_RE = re.compile(r"^\*\*Figure (\d+)\. \S.*\*\*$")
SEP_CELL_RE = re.compile(r"^-{3,}:?$")
CALLOUT_RE = re.compile(r"^ {0,3}>\s*\*\*([^*]+?)\*\*")
ALERT_RE = re.compile(r"^ {0,3}>\s*\[![A-Za-z]+\]")
LABELS = {"Note", "Key point", "Warning"}
LINK_TARGET_RE = re.compile(r"\]\([^)]*\)")
SEP_ROW_RE = re.compile(r"^\s*\|?[\s|:-]+$")


def strip_code(line):
    return INLINE_CODE_RE.sub("", line)


def fence_mask(lines):
    mask = []
    fences = []
    open_char = None
    open_len = 0
    for num, line in enumerate(lines, 1):
        m = FENCE_RE.match(line)
        if open_char is None:
            if m and not (m.group(1)[0] == "`" and "`" in m.group(2)):
                open_char = m.group(1)[0]
                open_len = len(m.group(1))
                fences.append((num, m.group(2).strip()))
                mask.append(True)
            else:
                mask.append(False)
        else:
            mask.append(True)
            if m and m.group(1)[0] == open_char and len(m.group(1)) >= open_len and not m.group(2).strip():
                open_char = None
    return mask, fences


def slug(text):
    text = strip_code_marks(text).strip().lower()
    text = re.sub(r"[^\w\- ]", "", text)
    return text.replace(" ", "-")


def strip_code_marks(text):
    return text.replace("`", "")


def split_row(line):
    row = line.strip()
    if row.startswith("|"):
        row = row[1:]
    if row.endswith("|") and not row.endswith("\\|"):
        row = row[:-1]
    return [c.strip() for c in re.split(r"(?<!\\)\|", row)]


class Doc:
    def __init__(self, path):
        self.path = Path(path)
        self.data = self.path.read_bytes()
        try:
            self.text = self.data.decode("utf-8")
            self.utf8 = True
        except UnicodeDecodeError:
            self.text = self.data.decode("utf-8", errors="replace")
            self.utf8 = False
        body = self.text.replace("\r", "")
        self.lines = body.split("\n")
        if self.lines and self.lines[-1] == "":
            self.lines.pop()
        self.mask, self.fences = fence_mask(self.lines)
        self.headings = []
        for num, line in enumerate(self.lines, 1):
            if self.mask[num - 1]:
                continue
            m = HEADING_RE.match(line)
            if m:
                self.headings.append((num, len(m.group(1)), (m.group(2) or "").strip()))

    def outside(self):
        for num, line in enumerate(self.lines, 1):
            if not self.mask[num - 1]:
                yield num, line


def check_encoding(doc):
    bad = []
    if not doc.utf8:
        bad.append("file does not decode as UTF-8")
    if b"\r" in doc.data:
        line = doc.data[: doc.data.index(b"\r")].count(b"\n") + 1
        bad.append(f"line {line}: CR byte, use LF endings")
    if not doc.data.endswith(b"\n"):
        bad.append(f"line {len(doc.lines)}: no final newline")
    elif doc.data.endswith(b"\n\n") or doc.data.endswith(b"\r\n\r\n"):
        bad.append(f"line {len(doc.lines)}: more than one final newline")
    return bad, "UTF-8, LF endings, one final newline"


def check_title_block(doc):
    bad = []
    lines = doc.lines + [""] * max(0, 5 - len(doc.lines))
    if lines[0] != EYEBROW:
        bad.append(f"line 1: expected {EYEBROW}")
    if lines[1] != "":
        bad.append("line 2: expected a blank line")
    if not lines[2].startswith("# "):
        bad.append("line 3: expected the H1 title")
    if lines[3] != "":
        bad.append("line 4: expected a blank line")
    if not SUBTITLE_RE.match(lines[4]):
        bad.append("line 5: expected *Subtitle - D Month YYYY*")
    for num, level, _ in doc.headings:
        if level == 1 and num != 3:
            bad.append(f"line {num}: extra H1, the only H1 is the title on line 3")
    return bad, "eyebrow, H1, subtitle and date on lines 1 to 5"


def check_front_matter(doc):
    h1 = next((n for n, lvl, _ in doc.headings if lvl == 1), len(doc.lines) + 1)
    bad = [f"line {n}: front matter delimiter before the H1" for n, l in doc.outside() if n < h1 and l.strip() == "---"]
    return bad, "no front matter"


def check_heading_depth(doc):
    bad = [f"line {n}: H{lvl} is deeper than H3" for n, lvl, _ in doc.headings if lvl > 3]
    return bad, "no heading deeper than H3"


def check_heading_order(doc):
    bad = []
    prev = 0
    for num, level, _ in doc.headings:
        if level > prev + 1:
            bad.append(f"line {num}: H{level} after H{prev}" if prev else f"line {num}: H{level} before the H1")
        prev = level
    return bad, "no skipped heading level"


def check_h2_numbering(doc):
    h2 = [(n, t) for n, lvl, t in doc.headings if lvl == 2]
    nums = [(n, re.match(r"^(\d+)\. \S", t)) for n, t in h2]
    numbered = [x for x in nums if x[1]]
    if not numbered:
        return [], "H2 headings are not numbered"
    bad = [f"line {n}: H2 not numbered while others are" for n, m in nums if not m]
    expected = 1
    for n, m in numbered:
        if int(m.group(1)) != expected:
            bad.append(f"line {n}: H2 number {m.group(1)}, expected {expected}")
        expected = int(m.group(1)) + 1
    return bad, "H2 headings numbered in order from 1"


def check_heading_text(doc):
    bad = []
    for num, _, text in doc.headings:
        plain = strip_code(text)
        if re.search(r"[.,;:!?]$", text):
            bad.append(f"line {num}: trailing punctuation")
        if "**" in plain or "__" in plain:
            bad.append(f"line {num}: bold in heading")
        if LINK_RE.search(plain):
            bad.append(f"line {num}: link in heading")
    return bad, "headings have no trailing punctuation, bold or links"


def check_list_markers(doc):
    bad = [f"line {n}: list marker {l.lstrip()[0]}, use -" for n, l in doc.outside() if re.match(r"^\s*[*+]\s", l)]
    return bad, "bullets use - only"


def check_tables(doc):
    bad = []
    lines = doc.lines
    i = 0
    count = 0
    while i < len(lines):
        if doc.mask[i] or not lines[i].lstrip().startswith("|"):
            i += 1
            continue
        start = i
        while i < len(lines) and not doc.mask[i] and lines[i].lstrip().startswith("|"):
            i += 1
        rows = lines[start:i]
        count += 1
        above = [lines[j].strip() for j in (start - 1, start - 2) if j >= 0]
        if not (above and (TABLE_LABEL_RE.match(above[0]) or (above[0] == "" and len(above) > 1 and TABLE_LABEL_RE.match(above[1])))):
            bad.append(f"line {start + 1}: no **Table N. ...** label above the table")
        if len(rows) < 2:
            bad.append(f"line {start + 1}: table has no separator row")
            continue
        for cell in split_row(rows[1]):
            if not SEP_CELL_RE.match(cell):
                bad.append(f"line {start + 2}: separator cell {cell or '(empty)'}, use --- or ---:")
        for k, row in enumerate(rows):
            if k == 1:
                continue
            if any(c == "" for c in split_row(row)):
                bad.append(f"line {start + k + 1}: empty cell, write - or n/a")
    return bad, f"{count} table(s) have a label, a --- or ---: separator and no empty cells"


def check_fence_language(doc):
    bad = [f"line {n}: code fence has no language tag" for n, info in doc.fences if not info]
    return bad, "every code fence has a language tag"


def check_callouts(doc):
    bad = []
    section = 0
    per_section = {}
    h2_lines = {n for n, lvl, _ in doc.headings if lvl == 2}
    prev_quote = False
    for num, line in enumerate(doc.lines, 1):
        if num in h2_lines:
            section += 1
        if doc.mask[num - 1]:
            prev_quote = False
            continue
        is_quote = re.match(r"^ {0,3}>", line) is not None
        if is_quote and ALERT_RE.match(line):
            bad.append(f"line {num}: [!ALERT] callout, use a bold label")
        if is_quote and not prev_quote:
            m = CALLOUT_RE.match(line)
            if m:
                label = m.group(1).strip().rstrip(":").strip()
                if label not in LABELS:
                    bad.append(f"line {num}: callout label {label}, use Note, Key point or Warning")
                per_section[section] = per_section.get(section, 0) + 1
                if per_section[section] > 1:
                    bad.append(f"line {num}: second callout in one section")
        prev_quote = is_quote
    return bad, "callouts use Note, Key point or Warning, at most one per section"


def check_html(doc):
    bad = [f"line {n}: HTML tag" for n, l in doc.outside() if HTML_RE.search(strip_code(l))]
    return bad, "no HTML"


def check_links(doc):
    slugs = set()
    seen = {}
    for _, _, text in doc.headings:
        s = slug(text)
        if s in seen:
            seen[s] += 1
            slugs.add(f"{s}-{seen[s]}")
        else:
            seen[s] = 0
            slugs.add(s)
    bad = []
    count = 0
    for num, line in doc.outside():
        for target in LINK_RE.findall(strip_code(line)):
            count += 1
            if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target) or target.startswith("/"):
                continue
            if target.startswith("#"):
                if target[1:] not in slugs:
                    bad.append(f"line {num}: {target} matches no heading")
                continue
            path_part = target.split("#", 1)[0].split("?", 1)[0]
            if path_part and not (doc.path.parent / path_part).exists():
                bad.append(f"line {num}: {target} does not resolve")
    return bad, f"{count} link(s): relative paths resolve, fragments match headings"


def check_figures(doc):
    bad = []
    count = 0
    for num, line in doc.outside():
        for m in LINK_RE.finditer(strip_code(line)):
            if not m.group(0).startswith("!"):
                continue
            count += 1
            alt = m.group(0)[2 : m.group(0).index("](")].strip()
            if not alt:
                bad.append(f"line {num}: image has no alt text")
            prev = next((doc.lines[j].strip() for j in range(num - 2, -1, -1) if doc.lines[j].strip()), "")
            label = FIGURE_LABEL_RE.match(prev)
            if not label:
                bad.append(f"line {num}: no **Figure N. ...** label line above the image")
            elif int(label.group(1)) != count:
                bad.append(f"line {num}: Figure {label.group(1)}, expected Figure {count}")
            target = m.group(1)
            if not target or re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target) or target.startswith(("/", "#")):
                bad.append(f"line {num}: image path {target[:40] or '(empty)'} is not a relative file path")
            elif not (doc.path.parent / target.split("#", 1)[0].split("?", 1)[0]).is_file():
                bad.append(f"line {num}: image {target} does not resolve")
    return bad, f"{count} figure(s) have alt text, a **Figure N.** label in order and a relative path that resolves"


def prose_items(doc):
    for num, line in doc.outside():
        text = LINK_TARGET_RE.sub("]", strip_code(line))
        if text.lstrip().startswith("|"):
            if SEP_ROW_RE.match(text):
                continue
            text = " | ".join(c for c in split_row(text) if not dwd_prose.is_data(c))
        yield f"line {num}", text


CHECKS = [
    ("encoding", check_encoding),
    ("title-block", check_title_block),
    ("front-matter", check_front_matter),
    ("heading-depth", check_heading_depth),
    ("heading-order", check_heading_order),
    ("h2-numbering", check_h2_numbering),
    ("heading-text", check_heading_text),
    ("list-markers", check_list_markers),
    ("tables", check_tables),
    ("figures", check_figures),
    ("fence-language", check_fence_language),
    ("callouts", check_callouts),
    ("html", check_html),
    ("links", check_links),
]


def main(argv):
    if len(argv) != 2:
        print("usage: python scripts/check_md.py path/to/file.md")
        return 2
    path = Path(argv[1])
    if not path.is_file():
        print(f"FAIL file: {path} not found")
        return 1
    doc = Doc(path)
    failed = False
    for name, fn in CHECKS:
        bad, ok = fn(doc)
        if bad:
            failed = True
            print(f"FAIL {name}: " + "; ".join(bad))
        else:
            print(f"PASS {name}: {ok}")
    failed = dwd_prose.report(dwd_prose.scan(prose_items(doc)), "body text") or failed
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
