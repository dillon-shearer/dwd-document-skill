import io
import re
import subprocess
import sys
import zipfile
from pathlib import Path

try:
    import pptx
    import xlsxwriter
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "python-pptx", "XlsxWriter"])
    import pptx

try:
    import matplotlib
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "matplotlib"])
    import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

from lxml import etree
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE
from pptx.opc.constants import RELATIONSHIP_TYPE as RT
from pptx.opc.packuri import PackURI
from pptx.oxml import parse_xml
from pptx.oxml.ns import qn
from pptx.util import Emu

sys.path.insert(0, str(Path(__file__).resolve().parent))
from dwd_pptx import (NS, PALETTES, SLIDE_NUM_TEXT, TABLE_STYLE_ID, add_callout, add_chart, add_hf, add_image,
                      add_table, layout_named, set_core, set_lines)

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
TEMPLATE = ASSETS / "dwd-template.pptx"
SAMPLE = ASSETS / "dwd-sample.pptx"

HEAD_FONT = "DM Sans"
BODY_FONT = "Aptos"
MONO_FONT = "IBM Plex Mono"

INK = "111110"
INK2 = "44403B"
INK3 = "6F6B64"
RULE = "E3E1DB"
ACCENT = "7A2E2E"
ACCENT_HOVER = "5C2020"
PAPER = "FAFAF8"
WHITE = "FFFFFF"
CHART = PALETTES["categorical"]
SEQUENTIAL = PALETTES["sequential"]

SLIDE_W = 12192000
SLIDE_H = 6858000
IN = 914400
LEFT = int(0.6 * IN)
TEXT_W = SLIDE_W - 2 * LEFT
BAR_W = int(0.08 * IN)

ZIP_DATE = (2026, 1, 1, 0, 0, 0)

A_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"

SQUARE = chr(0x25AA)
DASH = chr(0x2013)

LAYOUTS = ["Title", "Section", "Title and Content", "Two Content", "Chart", "Closing", "Picture"]


def inch(v):
    return int(round(v * IN))


def fill(color):
    if color in ("accent1", "bg1", "tx1", "tx2", "bg2"):
        return f'<a:solidFill><a:schemeClr val="{color}"/></a:solidFill>'
    return f'<a:solidFill><a:srgbClr val="{color}"/></a:solidFill>'


def font_tags(font):
    if font == "major":
        return '<a:latin typeface="+mj-lt"/><a:ea typeface="+mj-ea"/><a:cs typeface="+mj-cs"/>'
    if font == "minor":
        return '<a:latin typeface="+mn-lt"/><a:ea typeface="+mn-ea"/><a:cs typeface="+mn-cs"/>'
    return f'<a:latin typeface="{font}" pitchFamily="49" charset="0"/><a:cs typeface="{font}" pitchFamily="49" charset="0"/>'


def rpr(tag, size, color, font, bold=False, caps=False, spc=None):
    attrs = f'lang="en-US" sz="{int(size * 100)}"'
    if bold:
        attrs += ' b="1"'
    if caps:
        attrs += ' cap="all"'
    if spc is not None:
        attrs += f' spc="{spc}"'
    return f"<a:{tag} {attrs}>{fill(color)}{font_tags(font)}</a:{tag}>"


def mono_spc(size):
    return int(round(size * 8))


def lvl(n, size, color, font, algn="l", bullet=None, mar=0, indent=0, after=0, line=None, bold=False, caps=False, spc=None):
    parts = []
    if line:
        parts.append(f'<a:lnSpc><a:spcPct val="{line}"/></a:lnSpc>')
    parts.append('<a:spcBef><a:spcPts val="0"/></a:spcBef>')
    parts.append(f'<a:spcAft><a:spcPts val="{after}"/></a:spcAft>')
    if bullet:
        char, bcolor = bullet
        parts.append(fill(bcolor).replace("solidFill", "buClr"))
        parts.append('<a:buSzPct val="100000"/><a:buFont typeface="Arial" panose="020B0604020202020204" pitchFamily="34" charset="0"/>')
        parts.append(f'<a:buChar char="{char}"/>')
    else:
        parts.append("<a:buNone/>")
    parts.append(rpr("defRPr", size, color, font, bold, caps, spc))
    return f'<a:lvl{n}pPr marL="{mar}" indent="{indent}" algn="{algn}" defTabSz="914400" rtl="0">' + "".join(parts) + f"</a:lvl{n}pPr>"


def body_levels():
    sizes = [(20, SQUARE, "accent1"), (18, DASH, INK3), (16, DASH, INK3)]
    out = []
    for n in range(1, 10):
        size, char, bcolor = sizes[min(n, 3) - 1]
        mar = 285750 * min(n, 3)
        out.append(lvl(n, size, "tx1", "minor", bullet=(char, bcolor), mar=mar, indent=-285750, after=600, line=110000))
    return "".join(out)


def plain_levels(size, color, font, algn="l", bold=False, caps=False, spc=None, line=None, after=0):
    return "".join(lvl(n, size, color, font, algn=algn, bold=bold, caps=caps, spc=spc, line=line, after=after) for n in range(1, 10))


def xfrm(x, y, w, h):
    return f'<a:xfrm><a:off x="{x}" y="{y}"/><a:ext cx="{w}" cy="{h}"/></a:xfrm>'


def text_p(text, extra=""):
    if text is None:
        return '<a:p><a:endParaRPr lang="en-US"/></a:p>'
    return f'<a:p>{extra}<a:r><a:rPr lang="en-US"/><a:t>{text}</a:t></a:r></a:p>'


def ph(sid, name, ph_attrs, box=None, lst="", text="", anchor="t", body_attrs=""):
    sppr = f'<p:spPr>{xfrm(*box)}<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></p:spPr>' if box else "<p:spPr/>"
    paras = text if text and text.startswith("<a:p") else text_p(text or None)
    return (f'<p:sp><p:nvSpPr><p:cNvPr id="{sid}" name="{name}"/><p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr>'
            f'<p:nvPr><p:ph {ph_attrs}/></p:nvPr></p:nvSpPr>{sppr}'
            f'<p:txBody><a:bodyPr vert="horz" lIns="0" tIns="0" rIns="0" bIns="0" anchor="{anchor}" {body_attrs}><a:normAutofit/></a:bodyPr>'
            f'<a:lstStyle>{lst}</a:lstStyle>{paras}</p:txBody></p:sp>')


def rect(sid, name, box, color, text=None, text_rpr=""):
    body = ('<p:txBody><a:bodyPr lIns="0" tIns="0" rIns="0" bIns="0" anchor="ctr"/><a:lstStyle/>'
            f'<a:p><a:pPr algn="ctr"/><a:r>{text_rpr}<a:t>{text}</a:t></a:r></a:p></p:txBody>') if text else ""
    return (f'<p:sp><p:nvSpPr><p:cNvPr id="{sid}" name="{name}"/><p:cNvSpPr/><p:nvPr userDrawn="1"/></p:nvSpPr>'
            f'<p:spPr>{xfrm(*box)}<a:prstGeom prst="rect"><a:avLst/></a:prstGeom>{fill(color)}<a:ln><a:noFill/></a:ln></p:spPr>'
            f'{body}</p:sp>')


def text_box(sid, name, box, text, text_rpr, anchor="t"):
    return (f'<p:sp><p:nvSpPr><p:cNvPr id="{sid}" name="{name}"/><p:cNvSpPr txBox="1"/><p:nvPr userDrawn="1"/></p:nvSpPr>'
            f'<p:spPr>{xfrm(*box)}<a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:noFill/></p:spPr>'
            f'<p:txBody><a:bodyPr wrap="square" lIns="0" tIns="0" rIns="0" bIns="0" anchor="{anchor}"/><a:lstStyle/>'
            f'<a:p><a:r>{text_rpr}<a:t>{text}</a:t></a:r></a:p></p:txBody></p:sp>')


def rule_line(sid, name, x, y, w, color, width=9525):
    return (f'<p:cxnSp><p:nvCxnSpPr><p:cNvPr id="{sid}" name="{name}"/><p:cNvCxnSpPr/><p:nvPr userDrawn="1"/></p:nvCxnSpPr>'
            f'<p:spPr>{xfrm(x, y, w, 0)}<a:prstGeom prst="line"><a:avLst/></a:prstGeom>'
            f'<a:ln w="{width}">{fill(color)}</a:ln></p:spPr></p:cxnSp>')


def tree(shapes):
    return ('<p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>'
            '<p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>'
            + "".join(shapes) + "</p:spTree>")


FOOT_Y = inch(6.98)
FOOT_H = inch(0.3)
MARK_W = inch(0.62)
NUM_W = inch(1.5)
FOOT_SIZE = 9
FOOT_LST = plain_levels(FOOT_SIZE, INK3, MONO_FONT, caps=True, spc=mono_spc(FOOT_SIZE))
FOOT_NUM_LST = plain_levels(FOOT_SIZE, INK3, MONO_FONT, algn="r", caps=True, spc=mono_spc(FOOT_SIZE))

TITLE_BOX = (LEFT, inch(0.45), TEXT_W, inch(0.9))
BODY_BOX = (LEFT, inch(1.6), TEXT_W, inch(4.95))
FOOT_BOX = (LEFT + MARK_W + inch(0.2), FOOT_Y, TEXT_W - MARK_W - inch(0.2) - NUM_W, FOOT_H)
NUM_BOX = (LEFT + TEXT_W - NUM_W, FOOT_Y, NUM_W, FOOT_H)
DATE_BOX = (LEFT + inch(0.3), inch(6.6), inch(4), FOOT_H)


def footer_phs():
    return [ph(90, "Footer", 'type="ftr" sz="quarter" idx="11"', FOOT_BOX, anchor="ctr"),
            ph(91, "Slide Number", 'type="sldNum" sz="quarter" idx="12"', NUM_BOX, anchor="ctr", text=SLIDE_NUM_TEXT)]


def master_xml(layout_rids):
    mark_rpr = rpr("rPr", FOOT_SIZE, "bg1", MONO_FONT, bold=True, spc=mono_spc(FOOT_SIZE))
    shapes = [
        ph(2, "Title", 'type="title"', TITLE_BOX, anchor="b", text="Slide title"),
        ph(3, "Text", 'type="body" idx="1"', BODY_BOX, text="First level"),
        ph(4, "Date", 'type="dt" sz="half" idx="10"', DATE_BOX, lst=FOOT_LST, anchor="ctr", text="Month Year"),
        ph(5, "Footer", 'type="ftr" sz="quarter" idx="11"', FOOT_BOX, lst=FOOT_LST, anchor="ctr", text="Deck name"),
        ph(6, "Slide Number", 'type="sldNum" sz="quarter" idx="12"', NUM_BOX, lst=FOOT_NUM_LST, anchor="ctr", text=SLIDE_NUM_TEXT),
        rule_line(7, "Footer Rule", LEFT, inch(6.85), TEXT_W, RULE),
        rect(8, "DWD Mark", (LEFT, FOOT_Y, MARK_W, FOOT_H), "accent1", "DWD", mark_rpr),
    ]
    ids = "".join(f'<p:sldLayoutId id="{2147483649 + i}" r:id="{rid}"/>' for i, rid in enumerate(layout_rids))
    title_style = lvl(1, 28, "accent1", "major", bold=True, line=100000, spc=-28)
    other = plain_levels(18, "tx1", "minor")
    return (f'<p:sldMaster {NS}><p:cSld><p:bg><p:bgPr>{fill("bg2")}<a:effectLst/></p:bgPr></p:bg>{tree(shapes)}</p:cSld>'
            '<p:clrMap bg1="lt1" tx1="dk1" bg2="lt2" tx2="dk2" accent1="accent1" accent2="accent2" accent3="accent3" '
            'accent4="accent4" accent5="accent5" accent6="accent6" hlink="hlink" folHlink="folHlink"/>'
            f'<p:sldLayoutIdLst>{ids}</p:sldLayoutIdLst>'
            '<p:hf hdr="0" dt="0"/>'
            f'<p:txStyles><p:titleStyle>{title_style}</p:titleStyle><p:bodyStyle>{body_levels()}</p:bodyStyle>'
            f'<p:otherStyle>{other}</p:otherStyle></p:txStyles></p:sldMaster>')


def layout_xml(name, ltype, shapes, show_master=True):
    type_attr = f' type="{ltype}"' if ltype else ""
    show = "" if show_master else ' showMasterSp="0"'
    return (f'<p:sldLayout {NS}{type_attr} preserve="1"{show}><p:cSld name="{name}">{tree(shapes)}</p:cSld>'
            '<p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sldLayout>')


def eyebrow(sid, y):
    size = 12
    return text_box(sid, "Eyebrow", (LEFT + inch(0.3), y, inch(8), inch(0.35)), "Data With Dillon",
                    rpr("rPr", size, INK3, MONO_FONT, caps=True, spc=mono_spc(size)))


def accent_bar(sid):
    return rect(sid, "Accent Bar", (0, 0, BAR_W, SLIDE_H), "accent1")


def layouts():
    lead = LEFT + inch(0.3)
    lead_w = inch(9.5)
    title_lst = lvl(1, 54, INK, "major", bold=True, line=95000, spc=-108)
    sub_lst = plain_levels(20, INK2, "minor", line=110000)
    cover = [
        accent_bar(2),
        eyebrow(3, inch(2.1)),
        ph(4, "Title", 'type="ctrTitle"', (lead, inch(2.55), lead_w, inch(2.1)), lst=title_lst, anchor="t", text="Deck title"),
        ph(5, "Subtitle", 'type="subTitle" idx="1"', (lead, inch(4.75), lead_w, inch(0.9)), lst=sub_lst, text="One line on what the deck is"),
        ph(6, "Date", 'type="dt" sz="half" idx="10"', DATE_BOX, anchor="ctr", text="Month Year"),
    ]
    section_title = lvl(1, 40, "accent1", "major", bold=True, line=100000, spc=-40)
    section = [
        rect(2, "Section Bar", (LEFT, inch(2.35), inch(0.6), inch(0.06)), "accent1"),
        ph(3, "Title", 'type="title"', (LEFT, inch(2.6), TEXT_W, inch(1.3)), lst=section_title, anchor="t", text="1 - Section name"),
        ph(4, "Text", 'type="body" idx="1"', (LEFT, inch(4.0), inch(9), inch(1.2)), lst=sub_lst, text="One line on what the section covers"),
    ] + footer_phs()
    content = [
        ph(2, "Title", 'type="title"', TITLE_BOX, anchor="b", text="Slide title"),
        ph(3, "Content", 'idx="1"', BODY_BOX, text="First level"),
    ] + footer_phs()
    half = (TEXT_W - inch(0.4)) // 2
    two = [
        ph(2, "Title", 'type="title"', TITLE_BOX, anchor="b", text="Slide title"),
        ph(3, "Left Content", 'sz="half" idx="1"', (LEFT, BODY_BOX[1], half, BODY_BOX[3]), text="First level"),
        ph(4, "Right Content", 'sz="half" idx="2"', (LEFT + half + inch(0.4), BODY_BOX[1], half, BODY_BOX[3]), text="First level"),
    ] + footer_phs()
    cap_lst = plain_levels(10, INK3, MONO_FONT, caps=True, spc=mono_spc(10))
    chart = [
        ph(2, "Title", 'type="title"', TITLE_BOX, anchor="b", text="Slide title"),
        ph(3, "Chart", 'type="chart" idx="13"', (LEFT, BODY_BOX[1], TEXT_W, inch(4.45))),
        ph(4, "Caption", 'type="body" sz="quarter" idx="14"', (LEFT, inch(6.2), TEXT_W, inch(0.35)), lst=cap_lst, anchor="ctr", text="Figure 1. Caption"),
    ] + footer_phs()
    picture = [
        ph(2, "Title", 'type="title"', TITLE_BOX, anchor="b", text="Slide title"),
        ph(3, "Picture", 'type="pic" idx="13"', (LEFT, BODY_BOX[1], TEXT_W, inch(4.45))),
        ph(4, "Caption", 'type="body" sz="quarter" idx="14"', (LEFT, inch(6.2), TEXT_W, inch(0.35)), lst=cap_lst, anchor="ctr", text="Figure 1. Caption"),
    ] + footer_phs()
    closing = [
        accent_bar(2),
        eyebrow(3, inch(2.1)),
        ph(4, "Title", 'type="title"', (lead, inch(2.55), lead_w, inch(1.5)), lst=title_lst, anchor="t", text="Thank you"),
        ph(5, "Text", 'type="body" idx="1"', (lead, inch(4.2), lead_w, inch(1.4)), lst=sub_lst, text="Contact or next step"),
    ]
    return [
        layout_xml("Title", "title", cover, show_master=False),
        layout_xml("Section", "secHead", section),
        layout_xml("Title and Content", "obj", content),
        layout_xml("Two Content", "twoObj", two),
        layout_xml("Chart", "chart", chart),
        layout_xml("Closing", None, closing, show_master=False),
        layout_xml("Picture", "picTx", picture),
    ]


def theme_blob(blob):
    root = etree.fromstring(blob)
    a = "{%s}" % A_NS
    root.set("name", "DWD")
    elems = root.find(f"{a}themeElements")
    clr = elems.find(f"{a}clrScheme")
    for child in list(clr):
        clr.remove(child)
    clr.set("name", "DWD")
    colors = [("dk1", INK), ("lt1", WHITE), ("dk2", INK2), ("lt2", PAPER)]
    colors += [(f"accent{i + 1}", c) for i, c in enumerate(CHART)]
    colors += [("hlink", ACCENT), ("folHlink", ACCENT_HOVER)]
    for tag, value in colors:
        el = etree.SubElement(clr, f"{a}{tag}")
        etree.SubElement(el, f"{a}srgbClr", val=value)
    fonts = elems.find(f"{a}fontScheme")
    fonts.set("name", "DWD")
    for tag, face, pitch in (("majorFont", HEAD_FONT, "34"), ("minorFont", BODY_FONT, "34")):
        group = fonts.find(f"{a}{tag}")
        for child in list(group):
            group.remove(child)
        etree.SubElement(group, f"{a}latin", typeface=face, pitchFamily=pitch, charset="0")
        etree.SubElement(group, f"{a}ea", typeface="")
        etree.SubElement(group, f"{a}cs", typeface="")
    return etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)


def table_styles_blob():
    none = "<a:ln><a:noFill/></a:ln>"
    rule = f'<a:ln w="9525">{fill(RULE)}</a:ln>'
    return (f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<a:tblStyleLst xmlns:a="{A_NS}" def="{TABLE_STYLE_ID}">'
            f'<a:tblStyle styleId="{TABLE_STYLE_ID}" styleName="DWD Table">'
            '<a:wholeTbl><a:tcTxStyle><a:fontRef idx="minor"><a:prstClr val="black"/></a:fontRef><a:schemeClr val="tx1"/></a:tcTxStyle>'
            f'<a:tcStyle><a:tcBdr><a:left>{none}</a:left><a:right>{none}</a:right><a:top>{none}</a:top>'
            f'<a:bottom>{rule}</a:bottom><a:insideH>{rule}</a:insideH><a:insideV>{none}</a:insideV></a:tcBdr>'
            '<a:fill><a:noFill/></a:fill></a:tcStyle></a:wholeTbl>'
            '<a:firstRow><a:tcTxStyle b="on"><a:fontRef idx="minor"><a:prstClr val="black"/></a:fontRef><a:schemeClr val="bg1"/></a:tcTxStyle>'
            f'<a:tcStyle><a:tcBdr><a:bottom>{none}</a:bottom></a:tcBdr><a:fill>{fill("accent1")}</a:fill></a:tcStyle></a:firstRow>'
            '</a:tblStyle></a:tblStyleLst>').encode("utf-8")


def stable_xlsx(data):
    with zipfile.ZipFile(io.BytesIO(data)) as zin:
        items = [(info.filename, zin.read(info.filename)) for info in zin.infolist()]
    out = io.BytesIO()
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zout:
        for name, body in items:
            if name == "docProps/core.xml":
                body = re.sub(rb"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ", b"2026-01-01T00:00:00Z", body)
            zout.writestr(zipfile.ZipInfo(name, ZIP_DATE), body, compress_type=zipfile.ZIP_DEFLATED)
    return out.getvalue()


def save_stable(prs, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(path))
    with zipfile.ZipFile(path) as zin:
        items = [(info.filename, zin.read(info.filename)) for info in zin.infolist()]
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zout:
        for name, data in items:
            if name.endswith(".xlsx"):
                data = stable_xlsx(data)
            if name == "docProps/app.xml":
                data = data.replace(b"On-screen Show (4:3)", b"Widescreen").replace(b"Office Theme", b"DWD")
            zout.writestr(zipfile.ZipInfo(name, ZIP_DATE), data, compress_type=zipfile.ZIP_DEFLATED)


def build_template():
    prs = pptx.Presentation()
    prs.slide_width = Emu(SLIDE_W)
    prs.slide_height = Emu(SLIDE_H)
    prs.element.find(qn("p:sldSz")).attrib.pop("type", None)
    pres_part = prs.part
    master_rid = prs.element.find(qn("p:sldMasterIdLst"))[0].get(qn("r:id"))
    master_part = pres_part.related_part(master_rid)
    old = master_part._element.find(qn("p:sldLayoutIdLst"))
    rids = [el.get(qn("r:id")) for el in old]
    keep = rids[:len(LAYOUTS)]
    for rid in rids[len(LAYOUTS):]:
        master_part.drop_rel(rid)
    for i, (rid, xml) in enumerate(zip(keep, layouts()), 1):
        part = master_part.related_part(rid)
        part.partname = PackURI(f"/ppt/slideLayouts/slideLayout{i}.xml")
        part._element = parse_xml(xml)
    master_part._element = parse_xml(master_xml(keep))
    theme = master_part.part_related_by(RT.THEME)
    theme._blob = theme_blob(theme.blob)
    pres_part.part_related_by(RT.TABLE_STYLES)._blob = table_styles_blob()
    set_core(prs, "DWD template")
    save_stable(prs, TEMPLATE)


def heatmap_png():
    grey = "#" + INK3.lower()
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    hours = [f"{h}:00" for h in range(8, 20)]
    base = [3, 5, 8, 10, 12, 11, 9, 8, 9, 11, 12, 10]
    lift = [8, 8, 9, 9, 10, 13, 12]
    grid = [[b * f for b in base] for f in lift]
    cmap = LinearSegmentedColormap.from_list("dwd", ["#" + c.lower() for c in SEQUENTIAL])
    fig, ax = plt.subplots(figsize=(10, 4.45), dpi=200)
    fig.patch.set_alpha(0)
    image = ax.imshow(grid, cmap=cmap, aspect="auto")
    ax.set_xticks(range(len(hours)), hours)
    ax.set_yticks(range(len(days)), days)
    ax.tick_params(colors=grey, labelsize=12, length=0)
    for side in ax.spines.values():
        side.set_visible(False)
    bar = fig.colorbar(image, ax=ax, fraction=0.03, pad=0.02)
    bar.outline.set_visible(False)
    bar.ax.tick_params(colors=grey, labelsize=12, length=0)
    fig.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=200, transparent=True, metadata={"Software": None})
    plt.close(fig)
    buf.seek(0)
    return buf


def build_sample():
    prs = pptx.Presentation(str(TEMPLATE))
    deck = "Quarterly sales review"
    foot = {"ftr": deck, "dt": "November 2026"}

    s = prs.slides.add_slide(layout_named(prs, "Title"))
    s.shapes.title.text = deck
    s.placeholders[1].text = "What twelve months of orders say about repeat customers"
    add_hf(s, {"dt"}, foot)

    s = prs.slides.add_slide(layout_named(prs, "Section"))
    s.shapes.title.text = "1 - Summary"
    s.placeholders[1].text = "Repeat customers drove most of the growth this year."
    add_hf(s, {"ftr", "sldNum"}, foot)

    s = prs.slides.add_slide(layout_named(prs, "Title and Content"))
    s.shapes.title.text = "What changed"
    set_lines(s.placeholders[1].text_frame, [
        (0, "Email reminders went out after 30 days"),
        (1, "Sent to every first-time buyer"),
        (0, "Shipping became free over $75"),
        (0, "The returns window grew to 60 days"),
    ])
    add_hf(s, {"ftr", "sldNum"}, foot)

    s = prs.slides.add_slide(layout_named(prs, "Title and Content"))
    s.shapes.title.text = "The main finding"
    add_callout(s, s.placeholders[1], "Repeat customers placed 47% of Q4 orders, up from 38% in Q1.")
    add_hf(s, {"ftr", "sldNum"}, foot)

    s = prs.slides.add_slide(layout_named(prs, "Two Content"))
    s.shapes.title.text = "Key numbers"
    add_table(s, s.placeholders[1], [
        ["Measure", "Q1", "Q4"],
        ["Orders", "1,240", "1,610"],
        ["Repeat share", "38%", "47%"],
        ["Average order", "$84", "$91"],
    ])
    set_lines(s.placeholders[2].text_frame, [
        (0, "Orders rose 30% from Q1 to Q4"),
        (0, "Repeat share rose nine points"),
        (0, "Average order grew $7"),
    ])
    add_hf(s, {"ftr", "sldNum"}, foot)

    s = prs.slides.add_slide(layout_named(prs, "Two Content"))
    s.shapes.title.text = "Orders by channel"
    add_table(s, s.placeholders[1], [
        ["Channel", "Lead offer", "Q4 orders"],
        ["Email", "Reminder at 30 days", "620"],
        ["Search", "Free shipping", "540"],
        ["Social", "Returns window", "450"],
    ], numeric_cols=[2])
    set_lines(s.placeholders[2].text_frame, [
        (0, "Email reminders brought the most orders"),
        (0, "Search and social follow close behind"),
    ])
    add_hf(s, {"ftr", "sldNum"}, foot)

    s = prs.slides.add_slide(layout_named(prs, "Chart"))
    s.shapes.title.text = "Orders by quarter"
    data = CategoryChartData()
    data.categories = ["Q1", "Q2", "Q3", "Q4"]
    data.add_series("New", (769, 780, 812, 853))
    data.add_series("Repeat", (471, 560, 640, 757))
    data.add_series("Returned", (62, 58, 51, 44))
    caption = "Figure 1. Orders by customer type and quarter"
    frame = add_chart(s.placeholders[13], XL_CHART_TYPE.COLUMN_CLUSTERED, data)
    frame._element.nvGraphicFramePr.cNvPr.set("descr", caption)
    s.placeholders[14].text = caption
    add_hf(s, {"ftr", "sldNum"}, foot)

    s = prs.slides.add_slide(layout_named(prs, "Picture"))
    s.shapes.title.text = "When orders come in"
    add_image(s, heatmap_png(), "Figure 2. Orders by weekday and hour")
    add_hf(s, {"ftr", "sldNum"}, foot)

    s = prs.slides.add_slide(layout_named(prs, "Closing"))
    s.shapes.title.text = "Thank you"
    s.placeholders[1].text = "Next review: February 2027"

    set_core(prs, deck)
    save_stable(prs, SAMPLE)


def main():
    build_template()
    build_sample()
    print(f"wrote {TEMPLATE.relative_to(ROOT).as_posix()}")
    print(f"wrote {SAMPLE.relative_to(ROOT).as_posix()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
