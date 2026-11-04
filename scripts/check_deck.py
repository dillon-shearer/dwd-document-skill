import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dwd_prose

try:
    import pptx
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "python-pptx"])
    import pptx

from pptx.enum.shapes import MSO_SHAPE_TYPE, PP_PLACEHOLDER
from pptx.enum.text import PP_ALIGN
from pptx.opc.constants import RELATIONSHIP_TYPE as RT
from pptx.oxml.ns import qn

TABLE_STYLE_ID = "{7A2E2E00-D0D0-4D0D-8000-000000000001}"
LAYOUTS = ["Title", "Section", "Title and Content", "Two Content", "Chart", "Picture", "Closing"]
NO_FOOTER = ("Title", "Closing")
NUMBER_RE = re.compile(r"^[+-]?\$?[+-]?\d[\d,]*(\.\d+)?\s?(%|pts)?$")
EXEMPT_PH = (PP_PLACEHOLDER.FOOTER, PP_PLACEHOLDER.SLIDE_NUMBER, PP_PLACEHOLDER.DATE)
MAX_ROWS = 7
MAX_COLS = 5
MAX_BULLETS = 6
MAX_TITLE = 55
ACCENT = "7A2E2E"
TYPED_NUM_RE = re.compile(r"^\s*\d+[.)]\s")


def layout_name(slide):
    return slide.slide_layout.name


def ph_type(shape):
    return shape.placeholder_format.type if shape.is_placeholder else None


def short(text):
    return text if len(text) <= 30 else text[:27] + "..."


def check_style(prs):
    blob = prs.part.part_related_by(RT.TABLE_STYLES).blob.decode("utf-8", "replace")
    if f'styleId="{TABLE_STYLE_ID}"' not in blob:
        return False, "tableStyles.xml lacks the DWD Table style; start from assets/dwd-template.pptx"
    return True, "tableStyles.xml defines DWD Table"


def check_layouts(prs):
    bad = [f"slide {i} '{layout_name(s)}'" for i, s in enumerate(prs.slides, 1) if layout_name(s) not in LAYOUTS]
    if bad:
        return False, "layouts outside the template: " + "; ".join(bad)
    return True, "every slide uses a DWD layout"


def check_ends(prs):
    slides = list(prs.slides)
    if not slides:
        return False, "deck has no slides"
    first, last = layout_name(slides[0]), layout_name(slides[-1])
    if first != "Title" or last != "Closing":
        return False, f"first slide is '{first}', last is '{last}'; want Title and Closing"
    return True, "first slide is Title, last is Closing"


def check_footer(prs):
    bad = []
    for i, slide in enumerate(prs.slides, 1):
        if layout_name(slide) in NO_FOOTER:
            continue
        types = {ph_type(s): s for s in slide.placeholders}
        foot = types.get(PP_PLACEHOLDER.FOOTER)
        if foot is None or not foot.text_frame.text.strip():
            bad.append(f"slide {i} footer")
        if PP_PLACEHOLDER.SLIDE_NUMBER not in types:
            bad.append(f"slide {i} slide number")
    if bad:
        return False, "missing: " + "; ".join(bad)
    return True, "every content slide has a footer and slide number"


def check_direct(prs):
    bad = []
    for i, slide in enumerate(prs.slides, 1):
        for shape in slide.placeholders:
            if ph_type(shape) in EXEMPT_PH or not shape.has_text_frame:
                continue
            for r_pr in shape.text_frame._txBody.iter(qn("a:rPr")):
                tags = []
                if r_pr.get("sz") is not None:
                    tags.append("sz")
                if r_pr.find(qn("a:latin")) is not None:
                    tags.append("latin")
                if r_pr.find(qn("a:solidFill")) is not None:
                    tags.append("solidFill")
                if tags:
                    text = "".join(t.text or "" for t in r_pr.getparent().iter(qn("a:t")))
                    bad.append(f"slide {i} '{short(text)}' ({', '.join(tags)})")
    if bad:
        return False, "direct run formatting: " + "; ".join(bad[:5])
    return True, "no placeholder run has direct latin, sz or solidFill"


def tables(prs):
    for i, slide in enumerate(prs.slides, 1):
        for shape in slide.shapes:
            if shape.has_table:
                yield i, shape.table


def check_tables(prs):
    bad = []
    count = 0
    for i, table in tables(prs):
        count += 1
        tbl = table._tbl
        style = tbl.tblPr.find(qn("a:tableStyleId"))
        if style is None or style.text != TABLE_STYLE_ID:
            bad.append(f"slide {i} not DWD Table")
        rows, cols = len(table.rows), len(table.columns)
        if rows > MAX_ROWS or cols > MAX_COLS:
            bad.append(f"slide {i} is {rows}x{cols}")
        for tc in tbl.iter(qn("a:tc")):
            if any(tc.get(a) for a in ("gridSpan", "rowSpan", "hMerge", "vMerge")):
                bad.append(f"slide {i} has merged cells")
                break
        for r in range(1, rows):
            for c in range(1, cols):
                cell = table.cell(r, c)
                if not NUMBER_RE.match(cell.text.strip()):
                    continue
                if any(p.alignment != PP_ALIGN.RIGHT for p in cell.text_frame.paragraphs):
                    bad.append(f"slide {i} '{cell.text}' not right aligned")
    if bad:
        return False, "; ".join(bad[:5])
    return True, f"{count} tables use DWD Table, fit 7x5, no merges, numbers right aligned"


def check_bullets(prs):
    bad = []
    for i, slide in enumerate(prs.slides, 1):
        for shape in slide.placeholders:
            if ph_type(shape) != PP_PLACEHOLDER.OBJECT or not shape.has_text_frame:
                continue
            paras = [p for p in shape.text_frame.paragraphs if p.text.strip()]
            if len(paras) > MAX_BULLETS:
                bad.append(f"slide {i} has {len(paras)} bullets")
            deep = [p for p in paras if p.level >= 2]
            if deep:
                bad.append(f"slide {i} '{short(deep[0].text)}' at level {deep[0].level}")
    if bad:
        return False, "; ".join(bad)
    return True, "bullets keep to six items and two levels"


def check_numbering(prs):
    bad = []
    for i, slide in enumerate(prs.slides, 1):
        for shape in slide.placeholders:
            if ph_type(shape) in EXEMPT_PH or not shape.has_text_frame:
                continue
            section_title = slide.slide_layout.name == "Section" and shape == slide.shapes.title
            for p in shape.text_frame.paragraphs:
                ppr = p._p.pPr
                auto = ppr is not None and ppr.find(qn("a:buAutoNum")) is not None
                if auto:
                    clr = ppr.find(qn("a:buClr"))
                    srgb = clr.find(qn("a:srgbClr")) if clr is not None else None
                    if srgb is None or (srgb.get("val") or "").upper() != ACCENT:
                        bad.append(f"slide {i} '{short(p.text)}' numbered without #7a2e2e buClr")
                if p.level == 0 and TYPED_NUM_RE.match(p.text) and not section_title:
                    bad.append(f"slide {i} '{short(p.text)}' has a typed number")
    if bad:
        return False, "; ".join(bad[:5])
    return True, "numbered lists use buAutoNum in #7a2e2e and no typed numbers"


def check_titles(prs):
    bad = []
    for i, slide in enumerate(prs.slides, 1):
        title = slide.shapes.title
        if title is not None and len(title.text_frame.text) > MAX_TITLE:
            bad.append(f"slide {i} is {len(title.text_frame.text)} characters")
    if bad:
        return False, f"titles over {MAX_TITLE} characters: " + "; ".join(bad)
    return True, f"every title is at most {MAX_TITLE} characters"


def caption_text(slide):
    for shape in slide.placeholders:
        if shape.placeholder_format.idx == 14 and shape.has_text_frame:
            return shape.text_frame.text.strip()
    return ""


def check_figures(prs):
    bad = []
    for i, slide in enumerate(prs.slides, 1):
        name = layout_name(slide)
        if name == "Chart":
            if not any(s.has_chart for s in slide.shapes if s.shape_type in (MSO_SHAPE_TYPE.CHART, MSO_SHAPE_TYPE.PLACEHOLDER)):
                bad.append(f"slide {i} has no native chart")
        elif name == "Picture":
            pics = [s for s in slide.shapes if s._element.tag == qn("p:pic")]
            if not pics:
                bad.append(f"slide {i} has no picture")
            elif not all(s._element.nvPicPr.cNvPr.get("descr", "").strip() for s in pics):
                bad.append(f"slide {i} picture has no alt text")
        else:
            continue
        if not caption_text(slide):
            bad.append(f"slide {i} has no caption")
    if bad:
        return False, "; ".join(bad)
    return True, "chart slides hold a native chart, picture slides have alt text, both have captions"


def check_name(path):
    if " " in path.name:
        return False, f"file name '{path.name}' has spaces"
    return True, f"file name '{path.name}' has no spaces"


def prose_shapes(shapes):
    for s in shapes:
        if s.shape_type == MSO_SHAPE_TYPE.GROUP:
            yield from prose_shapes(s.shapes)
        elif s.has_text_frame:
            yield s.text_frame.text
        elif getattr(s, "has_table", False) and s.has_table:
            for row in s.table.rows:
                for cell in row.cells:
                    if not dwd_prose.is_data(cell.text):
                        yield cell.text


def prose_items(prs):
    for i, slide in enumerate(prs.slides, 1):
        for text in prose_shapes(slide.shapes):
            yield f"slide {i}", text
        if slide.has_notes_slide:
            yield f"slide {i} notes", slide.notes_slide.notes_text_frame.text


def main():
    if len(sys.argv) != 2:
        print("usage: python scripts/check_deck.py path/to/file.pptx")
        return 2
    path = Path(sys.argv[1])
    prs = pptx.Presentation(str(path))
    checks = [
        ("template", lambda: check_style(prs)),
        ("layouts", lambda: check_layouts(prs)),
        ("first-last", lambda: check_ends(prs)),
        ("footer", lambda: check_footer(prs)),
        ("direct-format", lambda: check_direct(prs)),
        ("tables", lambda: check_tables(prs)),
        ("bullets", lambda: check_bullets(prs)),
        ("numbering", lambda: check_numbering(prs)),
        ("titles", lambda: check_titles(prs)),
        ("charts-pictures", lambda: check_figures(prs)),
        ("file-name", lambda: check_name(path)),
    ]
    failed = False
    for name, fn in checks:
        ok, detail = fn()
        print(f"{'PASS' if ok else 'FAIL'} {name}: {detail}")
        failed = failed or not ok
    failed = dwd_prose.report(dwd_prose.scan(prose_items(prs)), "slide text and notes") or failed
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
