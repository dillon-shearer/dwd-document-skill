import io
import re
import subprocess
import sys
import zipfile
from datetime import datetime
from pathlib import Path

try:
    import docx
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "python-docx"])
    import docx

try:
    import matplotlib
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "matplotlib"])
    import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls, qn
from docx.shared import Inches

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_docx import NUMBER_RE, TITLE_RIGHT_IND

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
TEMPLATE = ASSETS / "dwd-template.docx"
SAMPLE = ASSETS / "dwd-sample.docx"

HEAD_FONT = "DM Sans"
BODY_FONT = "Aptos"
MONO_FONT = "IBM Plex Mono"
FALLBACKS = [
    (HEAD_FONT, "Segoe UI", "swiss", "variable"),
    (BODY_FONT, "Calibri", "swiss", "variable"),
    (MONO_FONT, "Consolas", "modern", "fixed"),
]

INK = "111110"
INK2 = "44403B"
INK3 = "6F6B64"
RULE = "E3E1DB"
ACCENT = "7A2E2E"
ACCENT_HOVER = "5C2020"
PAPER = "FAFAF8"
WHITE = "FFFFFF"
CHART = ["7A2E2E", "4A4239", "B8893B", "4A6B3A", "5A7A8A", "5C3A1A"]

PAGE_W = 12240
PAGE_H = 15840
MARGIN = 1440
TEXT_W = PAGE_W - 2 * MARGIN

BULLET_NUM = 90
NUMBER_NUM = 91
BULLET_CHAR = chr(0xF0A7)

FIXED_DATE = datetime(2026, 1, 1, 0, 0, 0)
ZIP_DATE = (2026, 1, 1, 0, 0, 0)


def rpr(font=None, size=None, color=None, bold=False, italic=False, caps=False, spacing=None, shd=None):
    parts = []
    if font:
        parts.append(f'<w:rFonts w:ascii="{font}" w:hAnsi="{font}" w:eastAsia="{font}" w:cs="{font}"/>')
    if bold:
        parts.append("<w:b/><w:bCs/>")
    if italic:
        parts.append("<w:i/><w:iCs/>")
    if caps:
        parts.append("<w:caps/>")
    if color:
        parts.append(f'<w:color w:val="{color}"/>')
    if spacing is not None:
        parts.append(f'<w:spacing w:val="{spacing}"/>')
    if size:
        half = int(round(size * 2))
        parts.append(f'<w:sz w:val="{half}"/><w:szCs w:val="{half}"/>')
    if shd:
        parts.append(f'<w:shd w:val="clear" w:color="auto" w:fill="{shd}"/>')
    return "<w:rPr>" + "".join(parts) + "</w:rPr>"


def ppr(keep=False, num=None, border=None, tabs=None, before=None, after=None, line=None, ind=None, jc=None, outline=None):
    parts = []
    if keep:
        parts.append("<w:keepNext/><w:keepLines/>")
    if num is not None:
        parts.append(f'<w:numPr><w:ilvl w:val="0"/><w:numId w:val="{num}"/></w:numPr>')
    if border:
        side, sz, space, color = border
        parts.append(f'<w:pBdr><w:{side} w:val="single" w:sz="{sz}" w:space="{space}" w:color="{color}"/></w:pBdr>')
    if tabs:
        parts.append("<w:tabs>" + "".join(f'<w:tab w:val="{v}" w:pos="{p}"/>' for v, p in tabs) + "</w:tabs>")
    attrs = []
    if before is not None:
        attrs.append(f'w:before="{before}"')
    if after is not None:
        attrs.append(f'w:after="{after}"')
    if line is not None:
        attrs.append(f'w:line="{line}" w:lineRule="auto"')
    if attrs:
        parts.append("<w:spacing " + " ".join(attrs) + "/>")
    if ind:
        parts.append("<w:ind " + " ".join(f'w:{k}="{v}"' for k, v in ind.items()) + "/>")
    if jc:
        parts.append(f'<w:jc w:val="{jc}"/>')
    if outline is not None:
        parts.append(f'<w:outlineLvl w:val="{outline}"/>')
    return "<w:pPr>" + "".join(parts) + "</w:pPr>"


def put_style(styles_el, kind, style_id, name, body, based="Normal", nxt=None, ui=None, custom=False):
    for old in styles_el.findall(qn("w:style")):
        if old.get(qn("w:styleId")) == style_id:
            styles_el.remove(old)
    head = f'<w:name w:val="{name}"/>'
    if based:
        head += f'<w:basedOn w:val="{based}"/>'
    if nxt:
        head += f'<w:next w:val="{nxt}"/>'
    if ui is not None:
        head += f'<w:uiPriority w:val="{ui}"/>'
    head += "<w:qFormat/>"
    flag = ' w:customStyle="1"' if custom else ""
    default = ' w:default="1"' if style_id == "Normal" else ""
    xml = f'<w:style {nsdecls("w")} w:type="{kind}"{default}{flag} w:styleId="{style_id}">{head}{body}</w:style>'
    styles_el.append(parse_xml(xml))


def build_styles(doc):
    styles_el = doc.styles.element
    defaults = styles_el.find(qn("w:docDefaults"))
    styles_el.remove(defaults)
    styles_el.insert(0, parse_xml(
        f'<w:docDefaults {nsdecls("w")}>'
        f'<w:rPrDefault>{rpr(BODY_FONT, 11)}</w:rPrDefault>'
        f'<w:pPrDefault>{ppr(after=132, line=276)}</w:pPrDefault>'
        "</w:docDefaults>"
    ))
    put_style(styles_el, "paragraph", "Normal", "Normal", rpr(BODY_FONT, 11, INK), based=None)
    heads = [
        ("Heading1", "heading 1", 21, -4, 480, 120, ("bottom", 6, 4, INK3), 0),
        ("Heading2", "heading 2", 15, -3, 360, 120, None, 1),
        ("Heading3", "heading 3", 11.5, -2, 240, 80, None, 2),
    ]
    for sid, name, size, spacing, before, after, border, level in heads:
        put_style(styles_el, "paragraph", sid, name,
                  ppr(keep=True, border=border, before=before, after=after, line=276, outline=level)
                  + rpr(HEAD_FONT, size, ACCENT, bold=True, spacing=spacing),
                  nxt="Normal", ui=9)
    put_style(styles_el, "paragraph", "Title", "Title",
              ppr(before=0, after=240, line=252, ind={"right": TITLE_RIGHT_IND})
              + rpr(HEAD_FONT, 44, INK, bold=True, spacing=-18),
              nxt="Subtitle", ui=10)
    put_style(styles_el, "paragraph", "Subtitle", "Subtitle",
              ppr(before=0, after=0, line=276, ind={"right": 3000}) + rpr(BODY_FONT, 14, INK2),
              ui=11)
    put_style(styles_el, "paragraph", "CoverEyebrow", "Cover Eyebrow",
              ppr(before=3840, after=240) + rpr(MONO_FONT, 9, INK3, caps=True, spacing=14),
              nxt="Title", custom=True)
    put_style(styles_el, "paragraph", "CoverDate", "Cover Date",
              ppr(before=0, after=0) + rpr(MONO_FONT, 9, INK3, caps=True, spacing=14),
              custom=True)
    put_style(styles_el, "paragraph", "Header", "header",
              ppr(border=("bottom", 6, 4, RULE), tabs=[("right", TEXT_W)], before=0, after=0, line=240)
              + rpr(MONO_FONT, 8, INK3, caps=True, spacing=13))
    put_style(styles_el, "paragraph", "Footer", "footer",
              ppr(border=("top", 6, 4, RULE), before=0, after=0, line=240, jc="right")
              + rpr(MONO_FONT, 8, INK3, caps=True, spacing=13))
    put_style(styles_el, "character", "DWMark", "DW Mark",
              rpr(MONO_FONT, 8, "auto", bold=True, caps=True, spacing=13, shd=ACCENT),
              based=None, custom=True)
    put_style(styles_el, "paragraph", "ListBullet", "List Bullet",
              ppr(num=BULLET_NUM, after=90), ui=99)
    put_style(styles_el, "paragraph", "ListNumber", "List Number",
              ppr(num=NUMBER_NUM, after=90), ui=99)
    put_style(styles_el, "paragraph", "Quote", "Quote",
              ppr(before=120, after=200, line=300, ind={"left": 440, "right": 440})
              + rpr(BODY_FONT, 12, INK2, italic=True),
              nxt="Normal", ui=29)
    put_style(styles_el, "paragraph", "Callout", "Callout",
              ppr(border=("left", 18, 9, ACCENT), before=200, after=200, line=348, ind={"left": 240})
              + rpr(BODY_FONT, 11, INK),
              nxt="Normal", custom=True)
    put_style(styles_el, "paragraph", "Caption", "caption",
              ppr(before=80, after=200) + rpr(MONO_FONT, 8, INK3, caps=True, spacing=13),
              nxt="Normal", ui=35)
    put_style(styles_el, "table", "DWDTable", "DWD Table",
              ppr(before=0, after=0, line=240)
              + "<w:tblPr><w:tblBorders>"
              + '<w:top w:val="nil"/><w:left w:val="nil"/>'
              + f'<w:bottom w:val="single" w:sz="6" w:space="0" w:color="{RULE}"/>'
              + '<w:right w:val="nil"/>'
              + f'<w:insideH w:val="single" w:sz="6" w:space="0" w:color="{RULE}"/>'
              + '<w:insideV w:val="nil"/></w:tblBorders>'
              + '<w:tblCellMar><w:top w:w="90" w:type="dxa"/><w:left w:w="120" w:type="dxa"/>'
              + '<w:bottom w:w="90" w:type="dxa"/><w:right w:w="120" w:type="dxa"/></w:tblCellMar>'
              + "</w:tblPr>"
              + '<w:tblStylePr w:type="firstRow">' + rpr(color="auto", bold=True)
              + '<w:tblPr/><w:trPr><w:tblHeader/></w:trPr>'
              + f'<w:tcPr><w:shd w:val="clear" w:color="auto" w:fill="{ACCENT}"/></w:tcPr>'
              + "</w:tblStylePr>",
              based="TableNormal", custom=True)


def build_numbering(doc):
    numbering = doc.part.numbering_part.element
    bullet = (
        f'<w:abstractNum {nsdecls("w")} w:abstractNumId="{BULLET_NUM}">'
        '<w:multiLevelType w:val="singleLevel"/>'
        '<w:lvl w:ilvl="0"><w:start w:val="1"/><w:numFmt w:val="bullet"/>'
        f'<w:lvlText w:val="{BULLET_CHAR}"/><w:lvlJc w:val="left"/>'
        '<w:pPr><w:ind w:left="330" w:hanging="270"/></w:pPr>'
        '<w:rPr><w:rFonts w:ascii="Wingdings" w:hAnsi="Wingdings" w:hint="default"/>'
        f'<w:color w:val="{ACCENT}"/><w:sz w:val="16"/></w:rPr></w:lvl></w:abstractNum>'
    )
    number = (
        f'<w:abstractNum {nsdecls("w")} w:abstractNumId="{NUMBER_NUM}">'
        '<w:multiLevelType w:val="singleLevel"/>'
        '<w:lvl w:ilvl="0"><w:start w:val="1"/><w:numFmt w:val="decimal"/>'
        '<w:lvlText w:val="%1."/><w:lvlJc w:val="left"/>'
        '<w:pPr><w:ind w:left="360" w:hanging="360"/></w:pPr>'
        f'<w:rPr><w:b/><w:color w:val="{ACCENT}"/></w:rPr></w:lvl></w:abstractNum>'
    )
    first_num = numbering.find(qn("w:num"))
    for xml in (bullet, number):
        el = parse_xml(xml)
        if first_num is not None:
            first_num.addprevious(el)
        else:
            numbering.append(el)
    for num_id in (BULLET_NUM, NUMBER_NUM):
        numbering.append(parse_xml(
            f'<w:num {nsdecls("w")} w:numId="{num_id}"><w:abstractNumId w:val="{num_id}"/></w:num>'
        ))


def part_by_name(doc, name):
    for rel in doc.part.rels.values():
        if not rel.is_external and str(rel.target_part.partname) == name:
            return rel.target_part
    raise KeyError(name)


def build_fonts(doc):
    part = part_by_name(doc, "/word/fontTable.xml")
    text = part.blob.decode("utf-8")
    entries = "".join(
        f'<w:font w:name="{name}"><w:altName w:val="{alt}"/><w:charset w:val="00"/>'
        f'<w:family w:val="{family}"/><w:pitch w:val="{pitch}"/></w:font>'
        for name, alt, family, pitch in FALLBACKS
    )
    part._blob = text.replace("</w:fonts>", entries + "</w:fonts>").encode("utf-8")


def build_theme(doc):
    part = part_by_name(doc, "/word/theme/theme1.xml")
    text = part.blob.decode("utf-8")
    colours = {"dk1": INK, "lt1": WHITE, "dk2": INK2, "lt2": PAPER, "hlink": ACCENT, "folHlink": ACCENT_HOVER}
    for i, hexval in enumerate(CHART, 1):
        colours[f"accent{i}"] = hexval
    for slot, hexval in colours.items():
        text = re.sub(rf"<a:{slot}>.*?</a:{slot}>", f'<a:{slot}><a:srgbClr val="{hexval}"/></a:{slot}>', text, flags=re.S)
    text = re.sub(r'(<a:majorFont>\s*<a:latin typeface=")[^"]*', rf"\g<1>{HEAD_FONT}", text)
    text = re.sub(r'(<a:minorFont>\s*<a:latin typeface=")[^"]*', rf"\g<1>{BODY_FONT}", text)
    part._blob = text.encode("utf-8")


def field(instr, cached):
    instr = instr.replace('"', "&quot;")
    return parse_xml(f'<w:fldSimple {nsdecls("w")} w:instr=" {instr} "><w:r><w:t>{cached}</w:t></w:r></w:fldSimple>')


def clear_paragraph(paragraph):
    for child in list(paragraph._p):
        if child.tag != qn("w:pPr"):
            paragraph._p.remove(child)


def set_header_footer(doc, section_text, date_text):
    sec = doc.sections[0]
    sec.different_first_page_header_footer = True
    head = sec.header.paragraphs[0]
    clear_paragraph(head)
    head.style = doc.styles["Header"]
    head.add_run(" DWD ", style=doc.styles["DW Mark"])
    head.add_run("\t")
    head._p.append(field('STYLEREF "Heading 1" \\* MERGEFORMAT', section_text))
    foot = sec.footer.paragraphs[0]
    clear_paragraph(foot)
    foot.style = doc.styles["Footer"]
    foot._p.append(field("PAGE \\* MERGEFORMAT", "2"))
    first_head = sec.first_page_header.paragraphs[0]
    first_head.style = doc.styles["Normal"]
    first_head.paragraph_format.space_after = 0
    first_foot = sec.first_page_footer.paragraphs[0]
    first_foot.style = doc.styles["Cover Date"]
    first_foot.text = date_text


def set_page(doc):
    sec = doc.sections[0]
    sec.page_width = PAGE_W * 635
    sec.page_height = PAGE_H * 635
    for side in ("top_margin", "bottom_margin", "left_margin", "right_margin"):
        setattr(sec, side, MARGIN * 635)
    sec.header_distance = 720 * 635
    sec.footer_distance = 720 * 635
    sect = sec._sectPr
    old = sect.find(qn("w:pgBorders"))
    if old is not None:
        sect.remove(old)
    sect.find(qn("w:pgMar")).addnext(parse_xml(
        f'<w:pgBorders {nsdecls("w")} w:display="firstPage" w:offsetFrom="page">'
        f'<w:left w:val="single" w:sz="36" w:space="0" w:color="{ACCENT}"/></w:pgBorders>'
    ))


def set_settings(doc):
    settings = doc.settings.element
    for old in settings.findall(qn("w:updateFields")):
        settings.remove(old)
    el = parse_xml(f'<w:updateFields {nsdecls("w")} w:val="true"/>')
    anchor = None
    for tag in ("w:hdrShapeDefaults", "w:footnotePr", "w:endnotePr", "w:compat", "w:docVars", "w:rsids"):
        anchor = settings.find(qn(tag))
        if anchor is not None:
            break
    if anchor is not None:
        anchor.addprevious(el)
    else:
        settings.append(el)


def set_core(doc, title):
    core = doc.core_properties
    core.author = "Data With Dillon"
    core.last_modified_by = "Data With Dillon"
    core.title = title
    core.created = FIXED_DATE
    core.modified = FIXED_DATE
    core.last_printed = FIXED_DATE
    core.revision = 1


def save_stable(doc, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(path))
    with zipfile.ZipFile(path) as zin:
        items = [(info.filename, zin.read(info.filename)) for info in zin.infolist()]
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zout:
        for name, data in items:
            zout.writestr(zipfile.ZipInfo(name, ZIP_DATE), data, compress_type=zipfile.ZIP_DEFLATED)


def clear_body(doc):
    body = doc.element.body
    for p in body.findall(qn("w:p")):
        body.remove(p)


def build_template():
    doc = docx.Document()
    build_styles(doc)
    build_numbering(doc)
    build_fonts(doc)
    build_theme(doc)
    set_page(doc)
    set_header_footer(doc, "1. Section", "Month Year")
    set_settings(doc)
    clear_body(doc)
    doc.add_paragraph("")
    set_core(doc, "DWD template")
    save_stable(doc, TEMPLATE)


def add_table(doc, rows):
    table = doc.add_table(rows=len(rows), cols=len(rows[0]))
    table.style = doc.styles["DWD Table"]
    numeric = {c for c in range(len(rows[0])) if all(NUMBER_RE.match(row[c].strip()) for row in rows[1:])}
    for r, row in enumerate(rows):
        for c, value in enumerate(row):
            cell = table.cell(r, c)
            cell.text = value
            if (r > 0 and c > 0) or (r == 0 and c in numeric):
                cell.paragraphs[0].alignment = 2
    tr_pr = table.rows[0]._tr.get_or_add_trPr()
    if tr_pr.find(qn("w:tblHeader")) is None:
        tr_pr.append(parse_xml(f'<w:tblHeader {nsdecls("w")}/>'))
    return table


def restart_numbering(doc, abstract_id=NUMBER_NUM):
    numbering = doc.part.numbering_part.element
    ids = [int(n.get(qn("w:numId"))) for n in numbering.findall(qn("w:num"))]
    num_id = max(ids) + 1
    numbering.append(parse_xml(
        f'<w:num {nsdecls("w")} w:numId="{num_id}"><w:abstractNumId w:val="{abstract_id}"/>'
        '<w:lvlOverride w:ilvl="0"><w:startOverride w:val="1"/></w:lvlOverride></w:num>'
    ))
    return num_id


def set_num(paragraph, num_id):
    p_pr = paragraph._p.get_or_add_pPr()
    old = p_pr.find(qn("w:numPr"))
    if old is not None:
        p_pr.remove(old)
    el = parse_xml(f'<w:numPr {nsdecls("w")}><w:ilvl w:val="0"/><w:numId w:val="{num_id}"/></w:numPr>')
    style = p_pr.find(qn("w:pStyle"))
    if style is not None:
        style.addnext(el)
    else:
        p_pr.insert(0, el)


def chart_png(labels, series, names):
    grey = "#" + INK3.lower()
    fig, ax = plt.subplots(figsize=(6.5, 3.25), dpi=200)
    fig.patch.set_alpha(0)
    ax.patch.set_alpha(0)
    for values, name, colour in zip(series, names, CHART):
        ax.plot(labels, values, color="#" + colour.lower(), linewidth=2, label=name)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(grey)
        ax.spines[side].set_linewidth(0.75)
    ax.tick_params(colors=grey, labelsize=8, width=0.75)
    ax.legend(frameon=False, fontsize=8, labelcolor=grey)
    fig.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=200, transparent=True, metadata={"Software": None})
    plt.close(fig)
    buf.seek(0)
    return buf


def build_sample():
    doc = docx.Document(str(TEMPLATE))
    clear_body(doc)
    set_header_footer(doc, "1. Summary", "November 2026")
    doc.add_paragraph("Data With Dillon", style="Cover Eyebrow")
    doc.add_paragraph("Quarterly review", style="Title")
    doc.add_paragraph("What twelve months of orders say about repeat customers", style="Subtitle")
    h1 = doc.add_paragraph("1. Summary", style="Heading 1")
    h1.paragraph_format.page_break_before = True
    doc.add_paragraph(
        "Repeat customers drove most of the growth this year. New customer numbers held steady, "
        "while orders from returning buyers rose in every quarter."
    )
    doc.add_paragraph("Key numbers", style="Heading 2")
    doc.add_paragraph("The table below compares the first and last quarter of the year.")
    add_table(doc, [
        ["Measure", "Q1", "Q4"],
        ["Orders", "1,240", "1,610"],
        ["Repeat share", "38%", "47%"],
        ["Average order", "$84", "$91"],
    ])
    doc.add_paragraph("Table 1. Orders by quarter", style="Caption")
    doc.add_paragraph("What changed", style="Heading 3")
    for text in ["Email reminders went out after 30 days.", "Shipping became free over $75.", "The returns window grew to 60 days."]:
        doc.add_paragraph(text, style="List Bullet")
    for text in ["Keep the reminder emails.", "Test a lower free shipping line.", "Review the returns cost in Q2."]:
        doc.add_paragraph(text, style="List Number")
    doc.add_paragraph(
        "Repeat share rose nine points in a year. That is the single biggest change in the data.",
        style="Callout",
    )
    doc.add_paragraph(
        "\"I came back because the second order was as easy as the first.\" - Customer survey, October",
        style="Quote",
    )
    doc.add_paragraph("2. Orders by week", style="Heading 1")
    doc.add_paragraph("Weekly orders for the year. The header row repeats when the table crosses a page.")
    rows = [["Week", "Orders", "Repeat share", "Change"]]
    for week in range(1, 53):
        orders = 230 + (week * 37) % 90 + week * 2
        share = 36 + week // 5
        change = (week * 13) % 11 - 5
        rows.append([f"Week {week}", f"{orders:,}", f"{share}%", f"{change:+d} pts"])
    add_table(doc, rows)
    doc.add_paragraph("Table 2. Orders by week", style="Caption")
    doc.add_paragraph("3. Trend", style="Heading 1")
    doc.add_paragraph("Repeat orders overtook new orders in the second quarter and stayed ahead.")
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    repeat = [180, 192, 205, 231, 248, 262, 270, 284, 297, 310, 322, 341]
    new = [240, 236, 241, 229, 233, 238, 231, 236, 240, 234, 237, 239]
    doc.add_picture(chart_png(months, [repeat, new], ["Repeat", "New"]), width=Inches(6.5))
    doc.add_paragraph("Figure 1. Orders by month", style="Caption")
    doc.add_paragraph("4. Next steps", style="Heading 1")
    doc.add_paragraph("The numbered list below restarts at 1.")
    num_id = restart_numbering(doc)
    for text in ["Share the review with the team.", "Agree the Q1 targets.", "Book the next review for March."]:
        set_num(doc.add_paragraph(text, style="List Number"), num_id)
    set_core(doc, "Quarterly review")
    save_stable(doc, SAMPLE)


def main():
    build_template()
    build_sample()
    print(f"wrote {TEMPLATE.relative_to(ROOT).as_posix()}")
    print(f"wrote {SAMPLE.relative_to(ROOT).as_posix()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
