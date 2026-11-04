import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dwd_prose

try:
    import docx
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "python-docx"])
    import docx

from docx.oxml.ns import qn

REQUIRED_STYLES = [
    "Title", "Heading1", "Heading2", "Heading3", "ListBullet", "ListNumber", "Quote",
    "Callout", "Caption", "DWDTable", "DWMark", "CoverEyebrow", "CoverDate",
]
H1_RE = re.compile(r"^\d+\. \S")
NUMBER_RE = re.compile(r"^[+-]?\$?[+-]?\d[\d,]*(\.\d+)?\s?(%|pts)?$")
DIRECT_TAGS = ("w:rFonts", "w:sz", "w:color")
HEAD_LEVELS = {"Heading1": 1, "Heading2": 2, "Heading3": 3}
TITLE_RIGHT_IND = 2600
TITLE_CHARS = 13
WORD_SPLIT_RE = re.compile(r"[\s-]+")


def para_style(p):
    p_pr = p.find(qn("w:pPr"))
    if p_pr is None:
        return None
    style = p_pr.find(qn("w:pStyle"))
    return None if style is None else style.get(qn("w:val"))


def para_text(el):
    return "".join(t.text or "" for t in el.iter(qn("w:t")))


def title_text(p):
    out = []
    for el in p.iter(qn("w:t"), qn("w:br"), qn("w:cr"), qn("w:tab"), qn("w:softHyphen"), qn("w:noBreakHyphen")):
        if el.tag == qn("w:t"):
            out.append(el.text or "")
        elif el.tag in (qn("w:softHyphen"), qn("w:noBreakHyphen")):
            out.append("-")
        else:
            out.append(" ")
    return "".join(out)


def check_title_width(doc):
    bad = []
    for p in body_paras(doc):
        if para_style(p) != "Title":
            continue
        bad.extend(w for w in WORD_SPLIT_RE.split(title_text(p)) if len(w) > TITLE_CHARS)
    if bad:
        return False, f"Title word longer than {TITLE_CHARS} characters breaks mid-word: " + ", ".join(bad)
    return True, f"every Title word fits the {TITLE_CHARS} character line"


def check_styles(doc):
    ids = {s.get(qn("w:styleId")) for s in doc.styles.element.findall(qn("w:style"))}
    missing = [s for s in REQUIRED_STYLES if s not in ids]
    if missing:
        return False, "styles.xml lacks " + ", ".join(missing)
    return True, "styles.xml defines every DWD style"


def check_direct(doc):
    bad = []
    for r in doc.element.body.iter(qn("w:r")):
        r_pr = r.find(qn("w:rPr"))
        if r_pr is None:
            continue
        style = r_pr.find(qn("w:rStyle"))
        if style is not None and style.get(qn("w:val")) == "DWMark":
            continue
        tags = [t.split(":")[1] for t in DIRECT_TAGS if r_pr.find(qn(t)) is not None]
        if tags:
            bad.append(f"'{para_text(r)[:30]}' ({', '.join(tags)})")
    if bad:
        return False, "direct run formatting: " + "; ".join(bad[:5])
    return True, "no body run has direct rFonts, sz or color"


def body_paras(doc):
    return [p for p in doc.element.body.iter(qn("w:p")) if p.getparent().tag == qn("w:body")]


def check_h1(doc):
    bad = [para_text(p) for p in body_paras(doc) if para_style(p) == "Heading1" and not H1_RE.match(para_text(p))]
    if bad:
        return False, "Heading 1 not 'N. Name': " + "; ".join(bad)
    return True, "every Heading 1 reads 'N. Name'"


def check_levels(doc):
    level = 0
    for p in body_paras(doc):
        new = HEAD_LEVELS.get(para_style(p))
        if new is None:
            continue
        if new > level + 1:
            return False, f"Heading {new} '{para_text(p)}' follows level {level}"
        level = new
    return True, "heading levels never skip"


def tables(doc):
    return doc.element.body.findall(qn("w:tbl"))


def check_table_style(doc):
    bad = []
    for i, tbl in enumerate(tables(doc), 1):
        style = tbl.find(qn("w:tblPr") + "/" + qn("w:tblStyle"))
        if style is None or style.get(qn("w:val")) != "DWDTable":
            bad.append(f"table {i} not DWDTable")
        nxt = tbl.getnext()
        if nxt is None or nxt.tag != qn("w:p") or para_style(nxt) != "Caption":
            bad.append(f"table {i} has no Caption after it")
    if bad:
        return False, "; ".join(bad)
    return True, "every table uses DWDTable and has a Caption after it"


def check_tbl_header(doc):
    bad = []
    for i, tbl in enumerate(tables(doc), 1):
        first = tbl.find(qn("w:tr"))
        if first is None or first.find(qn("w:trPr") + "/" + qn("w:tblHeader")) is None:
            bad.append(str(i))
    if bad:
        return False, "first row lacks w:tblHeader in table " + ", ".join(bad)
    return True, "every table's first row has w:tblHeader"


def check_numbers(doc):
    bad = []
    for i, tbl in enumerate(tables(doc), 1):
        for tr in tbl.findall(qn("w:tr"))[1:]:
            for tc in tr.findall(qn("w:tc")):
                text = para_text(tc).strip()
                if not NUMBER_RE.match(text):
                    continue
                for p in tc.findall(qn("w:p")):
                    jc = p.find(qn("w:pPr") + "/" + qn("w:jc"))
                    if jc is None or jc.get(qn("w:val")) not in ("right", "end"):
                        bad.append(f"table {i} '{text}'")
                        break
    if bad:
        return False, "numbers not right aligned: " + "; ".join(bad[:5])
    return True, "number cells in body rows are right aligned"


def check_name(path):
    if " " in path.name:
        return False, f"file name '{path.name}' has spaces"
    return True, "file name has no spaces"


def styleref_text(part):
    out = []
    for fld in part._element.iter(qn("w:fldSimple")):
        if "STYLEREF" in (fld.get(qn("w:instr")) or ""):
            out.append(para_text(fld))
    for p in part._element.iter(qn("w:p")):
        state = None
        text = ""
        for r in p.iter(qn("w:r")):
            ch = r.find(qn("w:fldChar"))
            instr = r.find(qn("w:instrText"))
            if instr is not None and "STYLEREF" in (instr.text or ""):
                state = "instr"
            elif ch is not None and state == "instr" and ch.get(qn("w:fldCharType")) == "separate":
                state = "result"
            elif ch is not None and state == "result" and ch.get(qn("w:fldCharType")) == "end":
                out.append(text)
                state, text = None, ""
            elif state == "result":
                text += para_text(r)
    return out


def check_placeholders(doc):
    bad = []
    refs = []
    for sec in doc.sections:
        date = sec.first_page_footer.paragraphs
        if any(p.text.strip().lower() == "month year" for p in date):
            bad.append("first-page footer still says 'Month Year'")
        for part in (sec.header, sec.even_page_header):
            if not part.is_linked_to_previous:
                refs.extend(styleref_text(part))
    if not refs:
        bad.append("no STYLEREF field in the header")
    if any(t.strip() == "1. Section" for t in refs):
        bad.append("STYLEREF cached text is still '1. Section'")
    if bad:
        return False, "; ".join(sorted(set(bad)))
    return True, "cover date and header section text are filled in"


def prose_items(doc):
    for i, p in enumerate(body_paras(doc), 1):
        yield f"paragraph {i}", para_text(p)
    for t, tbl in enumerate(tables(doc), 1):
        for r, tr in enumerate(tbl.findall(qn("w:tr")), 1):
            for c, tc in enumerate(tr.findall(qn("w:tc")), 1):
                text = para_text(tc)
                if not dwd_prose.is_data(text):
                    yield f"table {t} row {r} cell {c}", text


def main():
    if len(sys.argv) != 2:
        print("usage: python scripts/check_docx.py path/to/file.docx")
        return 2
    path = Path(sys.argv[1])
    doc = docx.Document(str(path))
    checks = [
        ("template-styles", lambda: check_styles(doc)),
        ("no-direct-format", lambda: check_direct(doc)),
        ("title-width", lambda: check_title_width(doc)),
        ("h1-format", lambda: check_h1(doc)),
        ("heading-order", lambda: check_levels(doc)),
        ("table-style-caption", lambda: check_table_style(doc)),
        ("table-header-row", lambda: check_tbl_header(doc)),
        ("numbers-right", lambda: check_numbers(doc)),
        ("file-name", lambda: check_name(path)),
        ("placeholders", lambda: check_placeholders(doc)),
    ]
    failed = False
    for name, fn in checks:
        ok, detail = fn()
        print(f"{'PASS' if ok else 'FAIL'} {name}: {detail}")
        failed = failed or not ok
    failed = dwd_prose.report(dwd_prose.scan(prose_items(doc)), "body paragraphs and text cells") or failed
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
