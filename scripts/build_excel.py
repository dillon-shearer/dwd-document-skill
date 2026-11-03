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

from openpyxl.styles import Font
from openpyxl.utils.indexed_list import IndexedList
from openpyxl.writer.theme import theme_xml

sys.path.insert(0, str(Path(__file__).resolve().parent))

from dwd_excel import (
    ACCENT, BODY_FONT, CHART, HEAD_FONT, HEADER_ROW, INK, INK2, RULE,
    add_chart, add_table, argb, finish, new_sheet, set_widths, setup_sheet, styles,
)

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
TEMPLATE = ASSETS / "dwd-template.xlsx"
SAMPLE = ASSETS / "dwd-sample.xlsx"

FIXED_DATE = datetime(2026, 1, 1, 0, 0, 0)
ZIP_DATE = (2026, 1, 1, 0, 0, 0)


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


def build_template():
    wb = new_workbook("DWD template")
    ws = wb.active
    setup_sheet(ws, "Sheet1", "Workbook title", "One line on what this sheet holds", date(2026, 1, 1))
    heads = ["Item", "Value 1", "Value 2", "Value 3", "Value 4"]
    for c, h in enumerate(heads, 1):
        ws.cell(row=HEADER_ROW, column=c, value=h).style = "DWD Header"
    set_widths(ws, [24, 14, 14, 14, 14])
    save_stable(wb, TEMPLATE)


def build_orders(wb):
    ws = wb.active
    setup_sheet(ws, "Orders", "Orders by region", "Order count per region and quarter, 2026; returns are negative", date(2026, 11, 3))
    heads = ["Region", "Q1", "Q2", "Q3", "Q4", "Q4 share"]
    rows = [
        ["North", 1240, 1315, 1402, 1530],
        ["South", 980, 1022, 1105, 1187],
        ["East", 1410, 1388, 1460, 1602],
        ["West", 860, 912, 975, 1044],
        ["Central", 1120, 1176, 1210, 1298],
        ["Online", 1650, 1804, 1932, 2110],
        ["Wholesale", 0, 140, 265, 310],
        ["Returns", -95, -110, -122, -138],
    ]
    rows = [r + ["=E{row}/SUM(B{row}:E{row})"] for r in rows]
    set_widths(ws, [24, 14, 14, 14, 14, 14])
    first, last, nxt = add_table(
        ws, heads, rows,
        ["DWD Text", "DWD Integer", "DWD Integer", "DWD Integer", "DWD Integer", "DWD Percent"],
        total=["Total", None, None, None, None, "=E{row}/SUM(B{row}:E{row})"],
        caption="Table 1. Orders by region and quarter",
    )
    add_chart(ws, "column", first, last, 5, f"A{nxt + 1}")
    ws.cell(row=nxt + 19, column=1, value="Figure 1. Orders by region and quarter").style = "DWD Caption"


def build_notes(wb):
    ws = new_sheet(wb, "Notes", "Notes on the data", "Sources, definitions and known gaps for this workbook", date(2026, 11, 3))
    set_widths(ws, [24, 40])
    add_table(
        ws, ["Topic", "Note"],
        [
            ["Source", "Order system export taken on 2 November 2026, all channels, net of cancellations."],
            ["Returns", "Returned orders are counted in the quarter of the return and shown as negative values."],
            ["Wholesale", "The wholesale channel opened in April 2026, so Q1 is a true zero, not missing data."],
            ["Revenue", "Revenue is in US dollar millions at list price before discounts, rounded to one decimal."],
        ],
        ["DWD Text", "DWD Text Wrap"],
        caption="Table 2. Sources and definitions",
    )


def build_trend(wb):
    ws = new_sheet(wb, "Trend", "Revenue by month", "Revenue in $ millions, January to June, 2024 to 2026", date(2026, 11, 3))
    heads = ["Month", "2024", "2025", "2026"]
    rows = [
        ["January", 4.2, 4.6, 5.1],
        ["February", 3.9, 4.4, 4.8],
        ["March", 4.5, 5.0, 5.6],
        ["April", 4.7, 5.2, 5.9],
        ["May", 4.9, 5.5, 6.2],
        ["June", 5.3, 5.8, 6.6],
    ]
    set_widths(ws, [24, 14, 14, 14])
    first, last, nxt = add_table(
        ws, heads, rows,
        ["DWD Text", "DWD Decimal", "DWD Decimal", "DWD Decimal"],
        total="Total",
        caption="Table 3. Revenue by month, $ millions",
    )
    add_chart(ws, "line", first, last, 4, f"A{nxt + 1}", palette="sequential")
    ws.cell(row=nxt + 19, column=1, value="Figure 2. Revenue by month, 2024 to 2026").style = "DWD Caption"


def build_raw(wb):
    regions = ["North", "South", "East", "West", "Central", "Online"]
    channels = ["Store", "Web", "Phone"]
    products = ["Starter kit", "Refill pack", "Pro bundle", "Gift card"]
    prices = [24.0, 9.5, 59.0, 25.0]
    rows = []
    for i in range(12):
        p = i % 4
        rows.append([
            f"ORD-{1001 + i}",
            date(2026, 10, 1 + i * 2),
            regions[i % 6],
            channels[i % 3],
            products[p],
            1 + (i * 7) % 5,
            prices[p],
            [0, 0.05, 0.1][i % 3],
            "=F{row}*G{row}*(1-H{row})",
            "Yes" if i in (3, 8) else "No",
        ])
    ws = new_sheet(wb, "Raw", "Order lines", f"Raw order lines, October 2026, {len(rows)} rows", date(2026, 11, 3), landscape=True)
    ws.freeze_panes = "B7"
    heads = ["Order ID", "Date", "Region", "Channel", "Product", "Units", "Unit price", "Discount", "Revenue", "Returned"]
    set_widths(ws, [14, 14, 12, 12, 16, 10, 12, 12, 12, 12])
    add_table(
        ws, heads, rows,
        ["DWD Text", "DWD Date Cell", "DWD Text", "DWD Text", "DWD Text", "DWD Integer", "DWD Decimal", "DWD Percent", "DWD Decimal", "DWD Text"],
        caption="Table 4. Order lines, October 2026",
        autofilter=True,
    )


def build_sample():
    wb = new_workbook("DWD sample workbook")
    build_orders(wb)
    build_notes(wb)
    build_trend(wb)
    build_raw(wb)
    finish(wb)
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
