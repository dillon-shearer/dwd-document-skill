import copy
import math
import re
from datetime import datetime
from xml.sax.saxutils import escape

from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION, XL_MARKER_STYLE
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_AUTO_SIZE, PP_ALIGN
from pptx.oxml import parse_xml
from pptx.oxml.ns import qn
from pptx.parts.image import Image
from pptx.util import Emu, Pt

TABLE_STYLE_ID = "{7A2E2E00-D0D0-4D0D-8000-000000000001}"

INK2 = "44403B"
INK3 = "6F6B64"
RULE = "E3E1DB"
ACCENT = "7A2E2E"

PALETTES = {
    "categorical": ["7A2E2E", "4A4239", "B8893B", "4A6B3A", "5A7A8A", "5C3A1A"],
    "sequential": ["F3E7E4", "DFBFB8", "C4928A", "A6635B", "7A2E2E", "5C2020"],
    "diverging": ["7A2E2E", "B07A6E", "E3D3CC", "D4DDCB", "86A274", "4A6B3A"],
}

BAR_TYPES = (XL_CHART_TYPE.COLUMN_CLUSTERED, XL_CHART_TYPE.BAR_CLUSTERED)
PIE_TYPES = (XL_CHART_TYPE.PIE, XL_CHART_TYPE.DOUGHNUT)
CHART_TYPES = BAR_TYPES + (XL_CHART_TYPE.LINE,) + PIE_TYPES

NUMBER_RE = re.compile(r"^[+-]?\$?[+-]?\d[\d,]*(\.\d+)?\s?(%|pts)?$")

FIXED_DATE = datetime(2026, 1, 1, 0, 0, 0)

NS = ('xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
      'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
      'xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"')

SLIDE_NUM_TEXT = '<a:p><a:fld id="{B6F15528-21DE-4FAA-801E-634DDDAF4B2B}" type="slidenum"><a:rPr lang="en-US"/><a:t>&lt;#&gt;</a:t></a:fld></a:p>'

CALLOUT_BAR = Pt(3)
CALLOUT_GAP = Pt(12)
CALLOUT_PAD = Pt(1.5)
CALLOUT_SIZE = 20
CALLOUT_LINE = 1.45


def is_number(text):
    return bool(NUMBER_RE.match(text.strip()))


def layout_named(prs, name):
    layout = next((l for l in prs.slide_layouts if l.name == name), None)
    if layout is None:
        raise KeyError(f"no layout named {name!r}; have " + ", ".join(l.name for l in prs.slide_layouts))
    return layout


def add_hf(slide, types, values):
    layout = slide.slide_layout
    tree_el = slide.shapes._spTree
    for shape in layout.placeholders:
        ph_el = shape._element.ph
        if ph_el is None or ph_el.get("type") not in types:
            continue
        el = copy.deepcopy(shape._element)
        sppr = el.find(qn("p:spPr"))
        for child in list(sppr):
            sppr.remove(child)
        txb = el.find(qn("p:txBody"))
        lst = txb.find(qn("a:lstStyle"))
        for child in list(lst):
            lst.remove(child)
        for p in txb.findall(qn("a:p")):
            txb.remove(p)
        kind = ph_el.get("type")
        if kind == "sldNum":
            num = len(slide.part.package.presentation_part.presentation.slides._sldIdLst)
            txb.append(parse_xml(SLIDE_NUM_TEXT.replace("&lt;#&gt;", str(num)).replace("<a:p>", f'<a:p {NS}>', 1)))
        else:
            txb.append(parse_xml(f'<a:p {NS}><a:r><a:rPr lang="en-US"/><a:t>{escape(values[kind])}</a:t></a:r></a:p>'))
        el.find(qn("p:nvSpPr")).find(qn("p:cNvPr")).set("id", str(100 + len(tree_el)))
        tree_el.append(el)


NUMBERED_PPR = (f'<a:pPr {NS}><a:buClr><a:srgbClr val="{ACCENT}"/></a:buClr>'
                '<a:buSzPct val="100000"/><a:buFont typeface="+mn-lt"/><a:buAutoNum type="arabicPeriod"/></a:pPr>')


def set_lines(frame, lines, numbered=False):
    frame.text = ""
    first = True
    for level, text in lines:
        para = frame.paragraphs[0] if first else frame.add_paragraph()
        first = False
        para.text = text
        para.level = level
        if numbered and level == 0:
            ppr = para._p.get_or_add_pPr()
            ppr.extend(list(parse_xml(NUMBERED_PPR)))
            ppr.set("marL", "285750")
            ppr.set("indent", "-285750")


def add_table(slide, placeholder, rows, numeric_cols=None):
    if numeric_cols is None:
        body = rows[1:]
        numeric_cols = [c for c in range(1, len(rows[0])) if body and all(is_number(row[c]) for row in body)]
    numeric = set(numeric_cols) - {0}
    x, y, w = placeholder.left, placeholder.top, placeholder.width
    placeholder._element.getparent().remove(placeholder._element)
    shape = slide.shapes.add_table(len(rows), len(rows[0]), x, y, w, Emu(457200 * len(rows)))
    tbl_pr = shape.table._tbl.tblPr
    tbl_pr.set("firstRow", "1")
    tbl_pr.set("bandRow", "0")
    tbl_pr.find(qn("a:tableStyleId")).text = TABLE_STYLE_ID
    table = shape.table
    for r, row in enumerate(rows):
        for c, value in enumerate(row):
            cell = table.cell(r, c)
            cell.text = value
            cell.margin_left = cell.margin_right = Pt(6)
            cell.margin_top = cell.margin_bottom = Pt(4.5)
            para = cell.text_frame.paragraphs[0]
            para.alignment = PP_ALIGN.RIGHT if r > 0 and c in numeric else PP_ALIGN.LEFT
            for run in para.runs:
                run.font.size = Pt(16)
    return table


def rgb(value):
    return RGBColor.from_string(value)


def style_chart(chart, chart_type=XL_CHART_TYPE.COLUMN_CLUSTERED, palette="categorical"):
    colors = PALETTES[palette]
    chart.font.size = Pt(12)
    chart.font.color.rgb = rgb(INK2)
    plot = chart.plots[0]
    if chart_type in PIE_TYPES:
        for i, point in enumerate(plot.series[0].points):
            point.format.fill.solid()
            point.format.fill.fore_color.rgb = rgb(colors[i % len(colors)])
            point.format.line.fill.background()
    else:
        for i, series in enumerate(plot.series):
            color = rgb(colors[i % len(colors)])
            if chart_type == XL_CHART_TYPE.LINE:
                series.format.line.color.rgb = color
                series.format.line.width = Pt(2.25)
                series.marker.style = XL_MARKER_STYLE.NONE
                series.smooth = False
            else:
                series.format.fill.solid()
                series.format.fill.fore_color.rgb = color
                series.format.line.fill.background()
        if chart_type in BAR_TYPES:
            plot.gap_width = 80
            plot.overlap = 0
        cat = chart.category_axis
        cat.format.line.color.rgb = rgb(INK3)
        cat.format.line.width = Emu(9525)
        val = chart.value_axis
        val.format.line.fill.background()
        val.has_major_gridlines = True
        val.major_gridlines.format.line.color.rgb = rgb(RULE)
        val.major_gridlines.format.line.width = Emu(9525)
    chart.has_legend = True
    chart.legend.position = XL_LEGEND_POSITION.BOTTOM
    chart.legend.include_in_layout = False
    chart.has_title = False


def add_chart(placeholder, chart_type, data, palette="categorical"):
    if chart_type not in CHART_TYPES:
        raise ValueError("unsupported chart type; use one of " + ", ".join(t.name for t in CHART_TYPES))
    if palette not in PALETTES:
        raise ValueError("unknown palette; use one of " + ", ".join(PALETTES))
    frame = placeholder.insert_chart(chart_type, data)
    style_chart(frame.chart, chart_type, palette)
    return frame


def add_image(slide, path, caption):
    box = slide.placeholders[13]
    left, top, width, height = box.left, box.top, box.width, box.height
    px_w, px_h = Image.from_file(path).size
    if hasattr(path, "seek"):
        path.seek(0)
    scale = min(width / px_w, height / px_h)
    pic = box.insert_picture(path)
    pic.crop_left = pic.crop_right = pic.crop_top = pic.crop_bottom = 0
    pic.left, pic.top = left, top
    pic.width, pic.height = Emu(int(px_w * scale)), Emu(int(px_h * scale))
    pic._element.nvPicPr.cNvPr.set("descr", caption)
    slide.placeholders[14].text = caption
    return pic


def add_callout(slide, placeholder, text):
    x, y, w = placeholder.left, placeholder.top, placeholder.width
    placeholder._element.getparent().remove(placeholder._element)
    text_w = w - CALLOUT_BAR - CALLOUT_GAP
    per_line = max(1, int(text_w / Pt(CALLOUT_SIZE * 0.5)))
    lines = max(1, math.ceil(len(text) / per_line))
    height = Emu(int(lines * Pt(CALLOUT_SIZE * CALLOUT_LINE)) + 2 * CALLOUT_PAD)
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, CALLOUT_BAR, height)
    bar._element.remove(bar._element.find(qn("p:style")))
    bar.name = "Callout Bar"
    bar.fill.solid()
    bar.fill.fore_color.rgb = rgb(ACCENT)
    bar.line.fill.background()
    box = slide.shapes.add_textbox(x + CALLOUT_BAR + CALLOUT_GAP, y, text_w, height)
    box.name = "Callout Text"
    frame = box.text_frame
    frame.word_wrap = True
    frame.auto_size = MSO_AUTO_SIZE.NONE
    frame.margin_left = frame.margin_right = 0
    frame.margin_top = frame.margin_bottom = CALLOUT_PAD
    lst = frame._txBody.find(qn("a:lstStyle"))
    lst.append(parse_xml(f'<a:lvl1pPr {NS}><a:lnSpc><a:spcPct val="{int(CALLOUT_LINE * 100000)}"/></a:lnSpc>'
                         f'<a:defRPr sz="{CALLOUT_SIZE * 100}"/></a:lvl1pPr>'))
    frame.text = text
    return box


def set_core(prs, title):
    core = prs.core_properties
    core.author = "Data With Dillon"
    core.last_modified_by = "Data With Dillon"
    core.title = title
    core.created = FIXED_DATE
    core.modified = FIXED_DATE
    core.last_printed = FIXED_DATE
    core.revision = 1
