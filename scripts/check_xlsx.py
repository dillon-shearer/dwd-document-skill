import re
import subprocess
import sys
from datetime import date, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import dwd_prose

try:
    import openpyxl
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "openpyxl"])
    import openpyxl

STYLES = [
    "DWD Eyebrow", "DWD Title", "DWD Subtitle", "DWD Date", "DWD Header", "DWD Text", "DWD Text Wrap",
    "DWD Integer", "DWD Decimal", "DWD Percent", "DWD Date Cell", "DWD Total Label", "DWD Total Integer",
    "DWD Total Decimal", "DWD Caption",
]
NUMBER_STYLES = {"DWD Integer", "DWD Decimal", "DWD Percent", "DWD Date Cell", "DWD Total Integer", "DWD Total Decimal"}
STOP_STYLES = {"DWD Header", "DWD Caption", "DWD Total Label", "DWD Total Integer", "DWD Total Decimal"}
TOTAL_STYLES = {"DWD Total Label", "DWD Total Integer", "DWD Total Decimal"}
BRAND = {
    "7A2E2E", "4A4239", "B8893B", "4A6B3A", "5A7A8A", "5C3A1A",
    "F3E7E4", "DFBFB8", "C4928A", "A6635B", "5C2020",
    "B07A6E", "E3D3CC", "D4DDCB", "86A274",
}
EYEBROW = "DWD - DATA WITH DILLON"
NOTE_LABELS = {"Note", "Key point", "Warning", "Summary", "Quote"}
STEP_RE = re.compile(r"Step (\d+)")
TOPIC_RE = re.compile(r"[A-Za-z][A-Za-z0-9'-]*(?: [A-Za-z0-9][A-Za-z0-9'-]*)?")
HEADER_ROW = 6


def short(items, limit=6):
    items = list(items)
    if len(items) <= limit:
        return "; ".join(items)
    return "; ".join(items[:limit]) + f"; and {len(items) - limit} more"


def result(bad, good):
    if bad:
        return False, short(bad)
    return True, good


def is_formula(v):
    return isinstance(v, str) and v.startswith("=")


def cells_from(ws, row):
    for r in ws.iter_rows(min_row=row):
        for c in r:
            if c.value is not None:
                yield c


def check_template(wb):
    have = {s.name for s in wb._named_styles}
    missing = [s for s in STYLES if s not in have]
    theme = (wb.loaded_theme or b"").decode("utf-8", "replace")
    bad = []
    if missing:
        bad.append("missing named styles: " + ", ".join(missing))
    if '<a:clrScheme name="DWD">' not in theme:
        bad.append("theme colour scheme is not named DWD")
    if bad:
        bad.append("start from assets/dwd-template.xlsx")
    return result(bad, "all fifteen DWD named styles defined; theme colour scheme is DWD")


def check_title_block(wb):
    bad = []
    for ws in wb.worksheets:
        n = ws.title
        a1 = ws["A1"]
        if a1.value != EYEBROW or a1.style != "DWD Eyebrow":
            bad.append(f"{n}!A1 is not '{EYEBROW}' in DWD Eyebrow")
        for ref, name in (("A2", "DWD Title"), ("A3", "DWD Subtitle")):
            c = ws[ref]
            if c.value in (None, "") or c.style != name:
                bad.append(f"{n}!{ref} is empty or not in {name}")
        a4 = ws["A4"]
        if not isinstance(a4.value, (date, datetime)) or a4.style != "DWD Date":
            bad.append(f"{n}!A4 is not a date value in DWD Date")
        full = [c.coordinate for c in ws[5] if c.value is not None]
        if full:
            bad.append(f"{n} row 5 is not empty: " + ", ".join(full))
    return result(bad, "every sheet has the title block in A1:A4 and an empty row 5")


def check_styles(wb):
    bad = []
    named = {s.name: s for s in wb._named_styles}
    for ws in wb.worksheets:
        for c in cells_from(ws, HEADER_ROW):
            where = f"{ws.title}!{c.coordinate}"
            if not c.style.startswith("DWD "):
                bad.append(f"{where} uses style '{c.style}'")
                continue
            s = named.get(c.style)
            if s is None:
                continue
            diffs = [k for k, a, b in (("font", c.font, s.font), ("fill", c.fill, s.fill), ("number format", c.number_format, s.number_format)) if a != b]
            if diffs:
                bad.append(f"{where} has a direct {', '.join(diffs)} over {c.style}")
    return result(bad, "every cell from row 6 down uses a DWD style with no direct font, fill or number format")


def check_header(wb):
    bad = []
    for ws in wb.worksheets:
        for c in ws[HEADER_ROW]:
            if c.value is None:
                continue
            where = f"{ws.title}!{c.coordinate}"
            if c.style != "DWD Header":
                bad.append(f"{where} is not DWD Header")
            elif c.font.color is None or not c.font.color.auto:
                bad.append(f"{where} header font colour is not Automatic")
    return result(bad, "row 6 uses DWD Header with font colour Automatic")


def tables(ws):
    rows = ws.max_row
    for r in range(HEADER_ROW, rows + 1):
        cols = [c.column for c in ws[r] if c.style == "DWD Header" and c.value is not None]
        if not cols:
            continue
        body_end = r
        for b in range(r + 1, rows + 1):
            cells = [ws.cell(row=b, column=c) for c in cols]
            if all(x.value is None for x in cells) or any(x.style in STOP_STYLES for x in cells):
                break
            body_end = b
        yield r, cols, body_end


def check_columns(wb):
    bad = []
    for ws in wb.worksheets:
        for head, cols, end in tables(ws):
            for col in cols:
                used = {}
                for r in range(head + 1, end + 1):
                    c = ws.cell(row=r, column=col)
                    if c.value is not None:
                        used.setdefault(c.style, c.coordinate)
                if len(used) > 1:
                    bad.append(f"{ws.title} column {ws.cell(row=head, column=col).column_letter} mixes " + ", ".join(sorted(used)))
        for c in cells_from(ws, HEADER_ROW):
            if c.style in NUMBER_STYLES and not is_formula(c.value):
                if isinstance(c.value, bool) or not isinstance(c.value, (int, float, date, datetime)):
                    bad.append(f"{ws.title}!{c.coordinate} in {c.style} holds text")
    return result(bad, "each body column uses one style; number and date cells hold numbers or dates")


def check_totals(wb):
    bad = []
    for ws in wb.worksheets:
        for row in ws.iter_rows(min_row=HEADER_ROW):
            if not any(c.style == "DWD Total Label" for c in row):
                continue
            for c in row:
                if c.style == "DWD Percent" and is_formula(c.value) and "SUM(" in c.value.upper() and "/" not in c.value:
                    bad.append(f"{ws.title}!{c.coordinate} sums percentages; use a ratio of totals")
    return result(bad, "no total row sums a percent column")


def check_merged_hidden(wb):
    bad = []
    for ws in wb.worksheets:
        for m in ws.merged_cells.ranges:
            bad.append(f"{ws.title}!{m.coord} is merged")
        for k, d in ws.row_dimensions.items():
            if d.hidden:
                bad.append(f"{ws.title} row {k} is hidden")
        for k, d in ws.column_dimensions.items():
            if d.hidden:
                bad.append(f"{ws.title} column {k} is hidden")
    return result(bad, "no merged cells, no hidden rows or columns")


def check_setup(wb):
    bad = []
    for ws in wb.worksheets:
        n = ws.title
        if ws.freeze_panes not in ("A7", "B7"):
            bad.append(f"{n} freeze pane is {ws.freeze_panes}, want A7 or B7")
        if ws.sheet_view.showGridLines is not False:
            bad.append(f"{n} gridlines are on")
        if (ws.print_title_rows or "").replace("$", "") != "6:6":
            bad.append(f"{n} print titles are '{ws.print_title_rows}', want row 6")
        fit = ws.sheet_properties.pageSetUpPr
        if not (fit and fit.fitToPage) or ws.page_setup.fitToWidth not in (1, None):
            bad.append(f"{n} does not fit to one page wide")
        hf = [p.text or "" for h in (ws.oddHeader, ws.oddFooter) for p in (h.left, h.center, h.right)]
        if not any("DWD" in t for t in hf):
            bad.append(f"{n} print header and footer lack 'DWD'")
    return result(bad, "every sheet has the freeze pane, gridlines off, print titles row 6, one page wide and the DWD header")


def anchor_cell(chart):
    a = chart.anchor
    m = getattr(a, "_from", None)
    if m is not None:
        return m.row + 1, m.col + 1
    if isinstance(a, str):
        c = openpyxl.utils.cell.coordinate_from_string(a)
        return c[1], openpyxl.utils.column_index_from_string(c[0])
    return 1, 1


def captions(ws, prefix):
    out = []
    for c in cells_from(ws, HEADER_ROW):
        if c.style == "DWD Caption" and isinstance(c.value, str) and re.match(prefix + r" \d+\.", c.value):
            out.append(c)
    return out


def check_captions(wb):
    bad = []
    for ws in wb.worksheets:
        for head, cols, end in tables(ws):
            r = end + 1
            while any(ws.cell(row=r, column=c).style in TOTAL_STYLES for c in cols):
                r += 1
            c = ws.cell(row=r, column=cols[0])
            if c.style != "DWD Caption" or not re.match(r"Table \d+\.", str(c.value or "")):
                bad.append(f"{ws.title} table at row {head} has no 'Table N.' DWD Caption at {c.coordinate}")
        figs = captions(ws, "Figure")
        used = set()
        for i, ch in sorted(enumerate(ws._charts), key=lambda x: anchor_cell(x[1])):
            row, col = anchor_cell(ch)
            hit = next((c for c in sorted(figs, key=lambda c: c.row) if c.row > row and c.column == col and c.coordinate not in used), None)
            if hit is None:
                bad.append(f"{ws.title} chart {i + 1} at row {row} has no 'Figure N.' DWD Caption below it")
            else:
                used.add(hit.coordinate)
    return result(bad, "every table has a 'Table N.' caption and every chart a 'Figure N.' caption")


def color_of(fill):
    if fill is None:
        return None
    if fill.srgbClr is not None:
        v = fill.srgbClr if isinstance(fill.srgbClr, str) else fill.srgbClr.val
        return str(v).upper()[-6:]
    if fill.schemeClr is not None:
        return "scheme"
    return "other"


def check_charts(wb):
    bad = []
    count = 0
    for ws in wb.worksheets:
        for i, ch in enumerate(ws._charts, 1):
            count += 1
            where = f"{ws.title} chart {i}"
            if ch.title is not None:
                bad.append(f"{where} has a title; use a DWD Caption under it")
            for j, s in enumerate(ch.series, 1):
                sp = s.graphicalProperties
                fill = sp.solidFill if sp is not None else None
                if fill is None and sp is not None and sp.line is not None:
                    fill = sp.line.solidFill
                col = color_of(fill)
                if col not in (None, "scheme") and col not in BRAND:
                    bad.append(f"{where} series {j} colour #{col} is not a brand colour")
    return result(bad, f"{count} charts: series colours are brand colours, no chart titles")


def check_notes(wb):
    sheets = [ws for ws in wb.worksheets if ws.title == "Notes"]
    if not sheets:
        return True, "no Notes sheet"
    ws = sheets[0]
    found = list(tables(ws))
    if len(found) != 1:
        return False, f"Notes has {len(found)} tables, want one"
    head, cols, end = found[0]
    bad = []
    step = 0
    keys = 0
    for r in range(head + 1, end + 1):
        c = ws.cell(row=r, column=cols[0])
        v = str(c.value or "").strip()
        m = STEP_RE.fullmatch(v)
        if m:
            step += 1
            if int(m.group(1)) != step:
                bad.append(f"Notes!{c.coordinate} is '{v}', want 'Step {step}'")
        elif v == "Key point":
            keys += 1
            if keys == 2:
                bad.append(f"Notes!{c.coordinate} is a second Key point row")
        elif v not in NOTE_LABELS and not TOPIC_RE.fullmatch(v):
            bad.append(f"Notes!{c.coordinate} label '{v}' is not an allowed label or a one or two word topic")
    return result(bad, f"Notes has one table, {end - head} labelled rows, steps in order, at most one Key point")


def check_calc(wb):
    has = any(is_formula(c.value) for ws in wb.worksheets for c in cells_from(ws, 1))
    if has and not (wb.calculation and wb.calculation.fullCalcOnLoad):
        return False, "workbook holds formulas but fullCalcOnLoad is not set; call dwd_excel.finish(wb)"
    return True, "fullCalcOnLoad is set" if has else "no formulas"


def check_names(wb, path):
    bad = [f"sheet '{ws.title}' has a default name" for ws in wb.worksheets if ws.title in ("Sheet", "Sheet1")]
    if " " in path.name:
        bad.append(f"file name '{path.name}' has spaces")
    return result(bad, f"sheets named; file name '{path.name}' has no spaces")


def prose_items(wb):
    for ws in wb.worksheets:
        for c in cells_from(ws, 1):
            if isinstance(c.value, str) and not is_formula(c.value) and not dwd_prose.is_data(c.value):
                yield f"{ws.title}!{c.coordinate}", c.value


def main():
    if len(sys.argv) != 2:
        print("usage: python scripts/check_xlsx.py path/to/file.xlsx")
        return 2
    path = Path(sys.argv[1])
    wb = openpyxl.load_workbook(str(path))
    checks = [
        ("template", lambda: check_template(wb)),
        ("title-block", lambda: check_title_block(wb)),
        ("cell-styles", lambda: check_styles(wb)),
        ("header-row", lambda: check_header(wb)),
        ("columns", lambda: check_columns(wb)),
        ("totals", lambda: check_totals(wb)),
        ("merged-hidden", lambda: check_merged_hidden(wb)),
        ("sheet-setup", lambda: check_setup(wb)),
        ("captions", lambda: check_captions(wb)),
        ("charts", lambda: check_charts(wb)),
        ("notes", lambda: check_notes(wb)),
        ("calculation", lambda: check_calc(wb)),
        ("names", lambda: check_names(wb, path)),
    ]
    failed = False
    for name, fn in checks:
        ok, detail = fn()
        print(f"{'PASS' if ok else 'FAIL'} {name}: {detail}")
        failed = failed or not ok
    failed = dwd_prose.report(dwd_prose.scan(prose_items(wb)), "text cells") or failed
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
