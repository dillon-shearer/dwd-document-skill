import io
import re
import subprocess
import sys
import zipfile
from datetime import date, datetime
from pathlib import Path

try:
    import openpyxl
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "openpyxl"])
    import openpyxl

from openpyxl.chart import BarChart, Reference
from openpyxl.chart.shapes import GraphicalProperties
from openpyxl.chart.text import RichText
from openpyxl.drawing.line import LineProperties
from openpyxl.drawing.text import CharacterProperties, Font as DrawingFont, Paragraph, ParagraphProperties
from openpyxl.styles import Alignment, Border, Font, NamedStyle, PatternFill, Side
from openpyxl.styles.colors import Color
from openpyxl.utils import get_column_letter
from openpyxl.utils.indexed_list import IndexedList
from openpyxl.worksheet.properties import PageSetupProperties
from openpyxl.writer.theme import theme_xml

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
TEMPLATE = ASSETS / "dwd-template.xlsx"
SAMPLE = ASSETS / "dwd-sample.xlsx"

HEAD_FONT = "DM Sans"
BODY_FONT = "Aptos"
MONO_FONT = "IBM Plex Mono"

INK = "111110"
INK2 = "44403B"
INK3 = "6F6B64"
RULE = "E3E1DB"
ACCENT = "7A2E2E"
CHART = ["7A2E2E", "4A4239", "B8893B", "4A6B3A", "5A7A8A", "5C3A1A"]

FIXED_DATE = datetime(2026, 1, 1, 0, 0, 0)
ZIP_DATE = (2026, 1, 1, 0, 0, 0)

FMT_INT = "#,##0;-#,##0;0"
FMT_DEC = "#,##0.0;-#,##0.0;0.0"
FMT_PCT = "0.0%"
FMT_DATE = "yyyy-mm-dd"
FMT_LONG_DATE = "d mmmm yyyy"

TITLE_ROWS = 4
HEADER_ROW = 6

HAIR = Side(style="thin", color="FF" + RULE)
AXIS = Side(style="thin", color="FF" + INK3)


def argb(hexv):
    return "FF" + hexv


def font(name, size, color, bold=False):
    return Font(name=name, size=size, bold=bold, color=argb(color))


def auto_font(name, size, bold=False):
    return Font(name=name, size=size, bold=bold, color=Color(auto=True))


def style(name, fnt, fmt="General", fill=None, border=None, align=None):
    s = NamedStyle(name=name)
    s.font = fnt
    s.number_format = fmt
    if fill:
        s.fill = PatternFill("solid", fgColor=argb(fill))
    if border:
        s.border = border
    s.alignment = align or Alignment(vertical="center")
    return s


def styles():
    body_rule = Border(bottom=HAIR)
    left = Alignment(horizontal="left", vertical="center")
    right = Alignment(horizontal="right", vertical="center")
    return [
        style("DWD Eyebrow", font(MONO_FONT, 9, INK3), align=left),
        style("DWD Title", font(HEAD_FONT, 20, ACCENT, bold=True), align=Alignment(horizontal="left", vertical="bottom")),
        style("DWD Subtitle", font(BODY_FONT, 12, INK2), align=left),
        style("DWD Date", font(MONO_FONT, 9, INK3), FMT_LONG_DATE, align=left),
        style("DWD Header", auto_font(BODY_FONT, 11, bold=True), fill=ACCENT, align=Alignment(horizontal="left", vertical="center", wrap_text=True)),
        style("DWD Text", font(BODY_FONT, 11, INK), border=body_rule, align=left),
        style("DWD Integer", font(BODY_FONT, 11, INK), FMT_INT, border=body_rule, align=right),
        style("DWD Decimal", font(BODY_FONT, 11, INK), FMT_DEC, border=body_rule, align=right),
        style("DWD Percent", font(BODY_FONT, 11, INK), FMT_PCT, border=body_rule, align=right),
        style("DWD Date Cell", font(BODY_FONT, 11, INK), FMT_DATE, border=body_rule, align=right),
        style("DWD Total", font(BODY_FONT, 11, INK, bold=True), FMT_INT, border=Border(top=AXIS), align=right),
        style("DWD Caption", font(MONO_FONT, 8, INK3), align=left),
    ]


def brand_theme():
    t = theme_xml
    for slot, hexv in zip(["accent1", "accent2", "accent3", "accent4", "accent5", "accent6"], CHART):
        t = re.sub(rf"(<a:{slot}>\s*<a:srgbClr val=\")[0-9A-F]{{6}}", rf"\g<1>{hexv}", t)
    t = re.sub(r"(<a:dk2>\s*<a:srgbClr val=\")[0-9A-F]{6}", rf"\g<1>{INK2}", t)
    t = re.sub(r"(<a:lt2>\s*<a:srgbClr val=\")[0-9A-F]{6}", rf"\g<1>{RULE}", t)
    t = re.sub(r"(<a:hlink>\s*<a:srgbClr val=\")[0-9A-F]{6}", rf"\g<1>{ACCENT}", t)
    t = re.sub(r"(<a:folHlink>\s*<a:srgbClr val=\")[0-9A-F]{6}", rf"\g<1>{INK2}", t)
    t = t.replace('<a:clrScheme name="Office">', '<a:clrScheme name="DWD">')
    t = t.replace('<a:fontScheme name="Office">', '<a:fontScheme name="DWD">')
    t = t.replace('<a:latin typeface="Cambria"', f'<a:latin typeface="{HEAD_FONT}"')
    t = t.replace('<a:latin typeface="Calibri"', f'<a:latin typeface="{BODY_FONT}"')
    return t.encode("utf-8")


def new_workbook(title):
    wb = openpyxl.Workbook()
    base = Font(name=BODY_FONT, size=11, color=argb(INK), family=2, scheme="minor")
    wb._fonts = IndexedList([base])
    wb._named_styles["Normal"].font = base
    for s in styles():
        wb.add_named_style(s)
    wb.loaded_theme = brand_theme()
    wb.properties.title = title
    wb.properties.creator = "Data With Dillon"
    wb.properties.lastModifiedBy = "Data With Dillon"
    wb.properties.created = FIXED_DATE
    wb.properties.modified = FIXED_DATE
    return wb


def setup_sheet(ws, name, title, subtitle, when):
    ws.title = name
    ws.sheet_view.showGridLines = False
    ws.sheet_view.zoomScale = 100
    ws["A1"] = "DWD - DATA WITH DILLON"
    ws["A1"].style = "DWD Eyebrow"
    ws["A2"] = title
    ws["A2"].style = "DWD Title"
    ws["A3"] = subtitle
    ws["A3"].style = "DWD Subtitle"
    ws["A4"] = when
    ws["A4"].style = "DWD Date"
    ws.row_dimensions[2].height = 30
    ws.row_dimensions[HEADER_ROW].height = 22
    ws.freeze_panes = ws.cell(row=HEADER_ROW + 1, column=1)
    ws.page_setup.orientation = "portrait"
    ws.page_setup.paperSize = ws.PAPERSIZE_LETTER
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.sheet_properties.pageSetUpPr = PageSetupProperties(fitToPage=True)
    ws.page_margins.left = ws.page_margins.right = 1.0
    ws.page_margins.top = ws.page_margins.bottom = 1.0
    ws.page_margins.header = ws.page_margins.footer = 0.5
    ws.print_title_rows = f"{HEADER_ROW}:{HEADER_ROW}"
    for part, text in ((ws.oddHeader.left, "DWD"), (ws.oddHeader.right, "&A"), (ws.oddFooter.right, "&P")):
        part.text = text
        part.font = f"{MONO_FONT},Regular"
        part.size = 8
        part.color = INK3


def set_widths(ws, widths):
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w


def build_template():
    wb = new_workbook("DWD template")
    ws = wb.active
    setup_sheet(ws, "Sheet1", "Workbook title", "One line on what this sheet holds", date(2026, 1, 1))
    heads = ["Item", "Value", "Value", "Value", "Value"]
    for c, h in enumerate(heads, 1):
        ws.cell(row=HEADER_ROW, column=c, value=h).style = "DWD Header"
    set_widths(ws, [24, 14, 14, 14, 14])
    save_stable(wb, TEMPLATE)


def chart_text(size, color, bold=False):
    cp = CharacterProperties(sz=size * 100, b=bold, solidFill=color, latin=DrawingFont(typeface=BODY_FONT))
    return RichText(p=[Paragraph(pPr=ParagraphProperties(defRPr=cp), endParaRPr=cp)])


def add_chart(ws, first, last, ncols, anchor):
    ch = BarChart()
    ch.type = "col"
    ch.grouping = "clustered"
    ch.overlap = -10
    ch.gapWidth = 80
    ch.title = None
    ch.style = 2
    data = Reference(ws, min_col=2, max_col=ncols, min_row=first - 1, max_row=last)
    cats = Reference(ws, min_col=1, min_row=first, max_row=last)
    ch.add_data(data, titles_from_data=True)
    ch.set_categories(cats)
    for i, s in enumerate(ch.series):
        s.graphicalProperties.solidFill = CHART[i % len(CHART)]
        s.graphicalProperties.line.noFill = True
    ch.x_axis.delete = False
    ch.y_axis.delete = False
    ch.x_axis.graphicalProperties = GraphicalProperties(ln=LineProperties(solidFill=INK3, w=9525))
    ch.y_axis.graphicalProperties = GraphicalProperties(ln=LineProperties(noFill=True))
    ch.y_axis.majorGridlines.spPr = GraphicalProperties(ln=LineProperties(solidFill=RULE, w=9525))
    ch.y_axis.numFmt = FMT_INT
    ch.y_axis.number_format = FMT_INT
    ch.x_axis.txPr = chart_text(9, INK3)
    ch.y_axis.txPr = chart_text(9, INK3)
    ch.legend.position = "b"
    ch.legend.txPr = chart_text(9, INK2)
    ch.graphical_properties = GraphicalProperties(ln=LineProperties(noFill=True))
    ch.width = 18
    ch.height = 8.5
    ws.add_chart(ch, anchor)


def build_sample():
    wb = new_workbook("DWD sample workbook")
    ws = wb.active
    setup_sheet(ws, "Orders", "Orders by region", "Order count per region and quarter, 2026", date(2026, 11, 3))
    heads = ["Region", "Q1", "Q2", "Q3", "Q4"]
    rows = [
        ["North", 1240, 1315, 1402, 1530],
        ["South", 980, 1022, 1105, 1187],
        ["East", 1410, 1388, 1460, 1602],
        ["West", 860, 912, 975, 1044],
        ["Central", 1120, 1176, 1210, 1298],
        ["Online", 1650, 1804, 1932, 2110],
    ]
    for c, h in enumerate(heads, 1):
        ws.cell(row=HEADER_ROW, column=c, value=h).style = "DWD Header"
    first = HEADER_ROW + 1
    for r, row in enumerate(rows, first):
        for c, v in enumerate(row, 1):
            ws.cell(row=r, column=c, value=v).style = "DWD Text" if c == 1 else "DWD Integer"
    last = first + len(rows) - 1
    ws.cell(row=last + 1, column=1, value="Table 1. Orders by region and quarter").style = "DWD Caption"
    set_widths(ws, [24, 14, 14, 14, 14])
    add_chart(ws, first, last, len(heads), f"A{last + 3}")
    ws.cell(row=last + 21, column=1, value="Figure 1. Orders by region and quarter").style = "DWD Caption"
    save_stable(wb, SAMPLE)


def save_stable(wb, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    buf = io.BytesIO()
    wb.save(buf)
    with zipfile.ZipFile(io.BytesIO(buf.getvalue())) as zin:
        items = [(info.filename, zin.read(info.filename)) for info in zin.infolist()]
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zout:
        for name, data in items:
            if name == "docProps/core.xml":
                data = re.sub(rb"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ", b"2026-01-01T00:00:00Z", data)
            zout.writestr(zipfile.ZipInfo(name, ZIP_DATE), data, compress_type=zipfile.ZIP_DEFLATED)


def main():
    build_template()
    build_sample()
    print(f"wrote {TEMPLATE.relative_to(ROOT).as_posix()}")
    print(f"wrote {SAMPLE.relative_to(ROOT).as_posix()}")


if __name__ == "__main__":
    main()
