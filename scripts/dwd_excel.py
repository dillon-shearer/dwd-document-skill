from openpyxl.chart import BarChart, LineChart, Reference
from openpyxl.chart.shapes import GraphicalProperties
from openpyxl.chart.text import RichText
from openpyxl.drawing.line import LineProperties
from openpyxl.drawing.text import CharacterProperties, Font as DrawingFont, Paragraph, ParagraphProperties
from openpyxl.styles import Alignment, Border, Font, NamedStyle, PatternFill, Side
from openpyxl.styles.colors import Color
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.properties import PageSetupProperties

HEAD_FONT = "DM Sans"
BODY_FONT = "Aptos"
MONO_FONT = "IBM Plex Mono"

INK = "111110"
INK2 = "44403B"
INK3 = "6F6B64"
RULE = "E3E1DB"
ACCENT = "7A2E2E"
CHART = ["7A2E2E", "4A4239", "B8893B", "4A6B3A", "5A7A8A", "5C3A1A"]
SEQUENTIAL = ["F3E7E4", "DFBFB8", "C4928A", "A6635B", "7A2E2E", "5C2020"]
DIVERGING = ["7A2E2E", "B07A6E", "E3D3CC", "D4DDCB", "86A274", "4A6B3A"]
PALETTES = {"categorical": CHART, "sequential": SEQUENTIAL, "diverging": DIVERGING}
CHART_KINDS = ("column", "bar", "line")

FMT_INT = "#,##0;-#,##0;0"
FMT_DEC = "#,##0.0;-#,##0.0;0.0"
FMT_PCT = "0.0%"
FMT_DATE = "yyyy-mm-dd"
FMT_LONG_DATE = "d mmmm yyyy"

TITLE_ROWS = 4
HEADER_ROW = 6
HEADER_HEIGHT = 22
HEADER_WRAP_HEIGHT = 30
LINE_WIDTH = 28575
AXIS_WIDTH = 9525

HAIR = Side(style="thin", color="FF" + RULE)
AXIS = Side(style="thin", color="FF" + INK3)

TOTAL_STYLES = {"DWD Integer": "DWD Total Integer", "DWD Decimal": "DWD Total Decimal", "DWD Percent": "DWD Percent"}


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
    total_rule = Border(top=AXIS)
    left = Alignment(horizontal="left", vertical="center")
    right = Alignment(horizontal="right", vertical="center")
    return [
        style("DWD Eyebrow", font(MONO_FONT, 9, INK3), align=left),
        style("DWD Title", font(HEAD_FONT, 20, ACCENT, bold=True), align=Alignment(horizontal="left", vertical="bottom")),
        style("DWD Subtitle", font(BODY_FONT, 12, INK2), align=left),
        style("DWD Date", font(MONO_FONT, 9, INK3), FMT_LONG_DATE, align=left),
        style("DWD Header", auto_font(BODY_FONT, 11, bold=True), fill=ACCENT, align=Alignment(horizontal="left", vertical="center", wrap_text=True)),
        style("DWD Text", font(BODY_FONT, 11, INK), border=body_rule, align=left),
        style("DWD Text Wrap", font(BODY_FONT, 11, INK), border=body_rule, align=Alignment(horizontal="left", vertical="top", wrap_text=True)),
        style("DWD Integer", font(BODY_FONT, 11, INK), FMT_INT, border=body_rule, align=right),
        style("DWD Decimal", font(BODY_FONT, 11, INK), FMT_DEC, border=body_rule, align=right),
        style("DWD Percent", font(BODY_FONT, 11, INK), FMT_PCT, border=body_rule, align=right),
        style("DWD Date Cell", font(BODY_FONT, 11, INK), FMT_DATE, border=body_rule, align=right),
        style("DWD Total Label", font(BODY_FONT, 11, INK, bold=True), border=total_rule, align=left),
        style("DWD Total Integer", font(BODY_FONT, 11, INK, bold=True), FMT_INT, border=total_rule, align=right),
        style("DWD Total Decimal", font(BODY_FONT, 11, INK, bold=True), FMT_DEC, border=total_rule, align=right),
        style("DWD Caption", font(MONO_FONT, 8, INK3), align=left),
    ]


def setup_sheet(ws, name, title, subtitle, when, landscape=False):
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
    ws.row_dimensions[HEADER_ROW].height = HEADER_HEIGHT
    ws.freeze_panes = ws.cell(row=HEADER_ROW + 1, column=1)
    ws.page_setup.orientation = "landscape" if landscape else "portrait"
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


def new_sheet(wb, name, title, subtitle, when, landscape=False):
    ws = wb.create_sheet(name)
    setup_sheet(ws, name, title, subtitle, when, landscape=landscape)
    return ws


def set_widths(ws, widths):
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w


def fill_formula(value, row, first, last):
    if isinstance(value, str) and value.startswith("="):
        return value.format(row=row, first=first, last=last)
    return value


def header_wraps(ws, heads):
    for c, h in enumerate(heads, 1):
        text = str(h)
        width = ws.column_dimensions[get_column_letter(c)].width or 8.43
        if "\n" in text or len(text) > width:
            return True
    return False


def add_table(ws, heads, rows, styles, first_row=HEADER_ROW, total=None, caption=None, autofilter=False):
    if len(styles) != len(heads):
        raise ValueError("styles needs one style name per column")
    for c, h in enumerate(heads, 1):
        ws.cell(row=first_row, column=c, value=h).style = "DWD Header"
    c = len(heads) + 1
    while ws.cell(row=first_row, column=c).style == "DWD Header":
        ws.cell(row=first_row, column=c).value = None
        ws.cell(row=first_row, column=c).style = "Normal"
        c += 1
    ws.row_dimensions[first_row].height = HEADER_WRAP_HEIGHT if header_wraps(ws, heads) else HEADER_HEIGHT
    first = first_row + 1
    last = first_row + len(rows)
    for r, row in enumerate(rows, first):
        for c, v in enumerate(row, 1):
            ws.cell(row=r, column=c, value=fill_formula(v, r, first, last)).style = styles[c - 1]
    nxt = last + 1
    if total is not None:
        cells = [total] if isinstance(total, str) else list(total)
        cells += [None] * (len(heads) - len(cells))
        for c, v in enumerate(cells, 1):
            col = get_column_letter(c)
            body = styles[c - 1]
            if c == 1:
                ws.cell(row=nxt, column=c, value=v).style = "DWD Total Label"
                continue
            if v is None and body in ("DWD Integer", "DWD Decimal"):
                v = f"=SUM({col}{first}:{col}{last})"
            cell = ws.cell(row=nxt, column=c, value=fill_formula(v, nxt, first, last) if v != "" else None)
            cell.style = TOTAL_STYLES.get(body, "DWD Total Label")
        nxt += 1
    if caption:
        ws.cell(row=nxt, column=1, value=caption).style = "DWD Caption"
        nxt += 1
    if autofilter:
        ws.auto_filter.ref = f"A{first_row}:{get_column_letter(len(heads))}{last}"
    return first, last, nxt


def chart_text(size, color, bold=False):
    cp = CharacterProperties(sz=size * 100, b=bold, solidFill=color, latin=DrawingFont(typeface=BODY_FONT))
    return RichText(p=[Paragraph(pPr=ParagraphProperties(defRPr=cp), endParaRPr=cp)])


def series_colors(palette, n):
    colors = PALETTES[palette]
    if palette == "categorical" or n >= len(colors):
        return [colors[i % len(colors)] for i in range(n)]
    if palette == "sequential":
        return colors[len(colors) - n:]
    if n == 1:
        return [colors[0]]
    return [colors[round(i * (len(colors) - 1) / (n - 1))] for i in range(n)]


def add_chart(ws, kind, first, last, ncols, anchor, palette="categorical", label_col=1):
    if kind not in CHART_KINDS:
        raise ValueError(f"unknown chart kind {kind!r}; use column, bar or line")
    if palette not in PALETTES:
        raise ValueError(f"unknown palette {palette!r}; use categorical, sequential or diverging")
    if kind == "line":
        ch = LineChart()
        ch.grouping = "standard"
    else:
        ch = BarChart()
        ch.type = "col" if kind == "column" else "bar"
        ch.grouping = "clustered"
        ch.overlap = -10
        ch.gapWidth = 80
    ch.title = None
    ch.style = 2
    data = Reference(ws, min_col=label_col + 1, max_col=label_col + ncols - 1, min_row=first - 1, max_row=last)
    cats = Reference(ws, min_col=label_col, min_row=first, max_row=last)
    ch.add_data(data, titles_from_data=True)
    ch.set_categories(cats)
    for s, color in zip(ch.series, series_colors(palette, len(ch.series))):
        if kind == "line":
            s.graphicalProperties.line.solidFill = color
            s.graphicalProperties.line.width = LINE_WIDTH
            s.marker.symbol = "none"
            s.smooth = False
        else:
            s.graphicalProperties.solidFill = color
            s.graphicalProperties.line.noFill = True
    fmt = ws.cell(row=first, column=label_col + 1).number_format
    fmt = fmt if fmt in (FMT_INT, FMT_DEC, FMT_PCT) else FMT_INT
    ch.x_axis.delete = False
    ch.y_axis.delete = False
    ch.x_axis.graphicalProperties = GraphicalProperties(ln=LineProperties(solidFill=INK3, w=AXIS_WIDTH))
    ch.y_axis.graphicalProperties = GraphicalProperties(ln=LineProperties(noFill=True))
    ch.y_axis.majorGridlines.spPr = GraphicalProperties(ln=LineProperties(solidFill=RULE, w=AXIS_WIDTH))
    ch.y_axis.numFmt = fmt
    ch.y_axis.number_format = fmt
    if palette == "diverging":
        ch.x_axis.crosses = None
        ch.x_axis.crossesAt = 0
        ch.x_axis.tickLblPos = "low"
    ch.x_axis.txPr = chart_text(9, INK3)
    ch.y_axis.txPr = chart_text(9, INK3)
    ch.legend.position = "b"
    ch.legend.txPr = chart_text(9, INK2)
    ch.graphical_properties = GraphicalProperties(ln=LineProperties(noFill=True))
    ch.width = 18
    ch.height = 8.5
    ws.add_chart(ch, anchor)
    return ch


def finish(wb):
    wb.calculation.fullCalcOnLoad = True
    for ws in list(wb.worksheets):
        if len(wb.worksheets) == 1:
            break
        if ws.title in ("Sheet", "Sheet1") and not any(c.value is not None for row in ws.iter_rows() for c in row):
            wb.remove(ws)
    return wb
