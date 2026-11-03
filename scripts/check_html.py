import html
import os
import re
import shutil
import subprocess
import sys
import tempfile
from html.parser import HTMLParser
from pathlib import Path

TEMPLATE = Path(__file__).resolve().parent.parent / "assets" / "dwd-report.html"
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}
BRAND_HEX = {
    "fafaf8", "ffffff", "111110", "44403b", "6f6b64", "e3e1db", "7a2e2e", "5c2020", "f3e7e4",
    "4a4239", "b8893b", "4a6b3a", "5a7a8a", "5c3a1a",
    "dfbfb8", "c4928a", "a6635b",
    "b07a6e", "e3d3cc", "d4ddcb", "86a274",
}
HEX_RE = re.compile(r"#([0-9a-fA-F]{6}|[0-9a-fA-F]{3})(?![0-9a-fA-F])")
NUM_RE = re.compile(r"^[+\-]?\$?[+\-]?\d[\d,]*(\.\d+)?%?$")
WIDTH_RE = re.compile(r"^width:\s*\d+(\.\d+)?%;?$")
BARE_AMP_RE = re.compile(r"&(?![A-Za-z][A-Za-z0-9]*;|#[0-9]+;|#[xX][0-9a-fA-F]+;)")
LABELS = ("Note:", "Key point:", "Warning:")
FONTS_CSS = "https://fonts.googleapis.com/css"
PRECONNECTS = {"https://fonts.googleapis.com", "https://fonts.gstatic.com"}


class El:
    def __init__(self, tag, attrs, line, parent):
        self.tag = tag
        self.attrs = attrs
        self.line = line
        self.parent = parent
        self.children = []

    def classes(self):
        return (self.attrs.get("class") or "").split()

    def has(self, cls):
        return cls in self.classes()

    def elements(self):
        return [c for c in self.children if isinstance(c, El)]

    def text(self):
        out = []
        for c in self.children:
            out.append(c.text() if isinstance(c, El) else c)
        return "".join(out)

    def walk(self):
        for c in self.elements():
            yield c
            yield from c.walk()

    def prev_element(self):
        if self.parent is None:
            return None
        sibs = self.parent.elements()
        i = sibs.index(self)
        return sibs[i - 1] if i > 0 else None


class Tree(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.root = El("#root", {}, 1, None)
        self.stack = [self.root]
        self.text_lt = []

    def add(self, tag, attrs):
        el = El(tag, {k: (v if v is not None else "") for k, v in attrs}, self.getpos()[0], self.stack[-1])
        self.stack[-1].children.append(el)
        return el

    def handle_starttag(self, tag, attrs):
        el = self.add(tag, attrs)
        if tag not in VOID:
            self.stack.append(el)

    def handle_startendtag(self, tag, attrs):
        self.add(tag, attrs)

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i].tag == tag:
                del self.stack[i:]
                return

    def handle_data(self, data):
        cur = self.stack[-1]
        if cur.tag not in ("style", "script") and "<" in data:
            self.text_lt.append(self.getpos()[0] + data[: data.index("<")].count("\n"))
        cur.children.append(data)

    def handle_entityref(self, name):
        self.stack[-1].children.append(html.unescape("&" + name + ";"))

    def handle_charref(self, name):
        self.stack[-1].children.append(html.unescape("&#" + name + ";"))


def parse(text):
    tree = Tree()
    tree.feed(text)
    tree.close()
    return tree


def line_of(text, pos):
    return text.count("\n", 0, pos) + 1


def block_end(text, start):
    depth = 0
    for i in range(start, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return i + 1
    return len(text)


def style_lines(text):
    return [l.rstrip() for l in text.replace("\r\n", "\n").strip("\n").split("\n")]


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
        self.tree = parse(self.text)
        self.root = self.tree.root
        self.all = list(self.root.walk())

    def find(self, tag):
        return [e for e in self.all if e.tag == tag]


def check_encoding(doc):
    bad = []
    if not doc.utf8:
        bad.append("file is not valid UTF-8")
    if b"\r" in doc.data:
        ln = doc.data[: doc.data.index(b"\r")].count(b"\n") + 1
        bad.append(f"line {ln}: CR byte, use LF endings")
    if not doc.data.endswith(b"\n") or doc.data.endswith(b"\n\n"):
        ln = doc.text.count("\n") + 1
        bad.append(f"line {ln}: file must end with exactly one newline")
    return bad, "UTF-8, LF endings, one final newline"


def check_head(doc):
    bad = []
    htmls = doc.find("html")
    if not htmls or htmls[0].attrs.get("lang") != "en":
        bad.append(f"line {htmls[0].line if htmls else 1}: <html lang=\"en\"> missing")
    metas = doc.find("meta")
    if not any(m.attrs.get("charset", "").lower() == "utf-8" for m in metas):
        bad.append("line 1: no <meta charset=\"utf-8\">")
    if not any(m.attrs.get("name", "").lower() == "viewport" for m in metas):
        bad.append("line 1: no viewport meta")
    if not any(m.attrs.get("name", "").lower() == "color-scheme" and m.attrs.get("content", "").strip() == "light" for m in metas):
        bad.append("line 1: no <meta name=\"color-scheme\" content=\"light\">")
    titles = [t for t in doc.find("title") if t.parent.tag == "head"]
    if len(titles) != 1:
        bad.append(f"line {titles[1].line if titles else 1}: need exactly one <title>")
    elif not re.match(r"^\S.* - DWD$", titles[0].text().strip()):
        bad.append(f"line {titles[0].line}: title must read \"Document title - DWD\"")
    return bad, "lang, charset, viewport, color-scheme and title are set"


def check_resources(doc):
    bad = []
    for s in doc.find("script"):
        bad.append(f"line {s.line}: <script> is not allowed")
    sheets = 0
    pre = set()
    for l in doc.find("link"):
        rel = l.attrs.get("rel", "").lower().split()
        href = l.attrs.get("href", "")
        if rel == ["stylesheet"] and href.startswith(FONTS_CSS) and sheets == 0:
            sheets += 1
        elif rel == ["preconnect"] and href.rstrip("/") in PRECONNECTS and href.rstrip("/") not in pre:
            pre.add(href.rstrip("/"))
        else:
            bad.append(f"line {l.line}: link not allowed ({' '.join(rel)} {href})")
    for i in doc.find("img"):
        if re.match(r"^\s*(https?:)?//", i.attrs.get("src", ""), re.I):
            bad.append(f"line {i.line}: remote image")
    return bad, "no script; only the Google Fonts stylesheet and its preconnects"


def check_style_block(doc):
    styles = doc.find("style")
    if len(styles) != 1:
        return [f"line {styles[1].line if styles else 1}: need exactly one <style> block, found {len(styles)}"], ""
    if not TEMPLATE.is_file():
        return [f"line {styles[0].line}: template {TEMPLATE} not found"], ""
    ref_styles = [e for e in parse(TEMPLATE.read_text(encoding="utf-8")).root.walk() if e.tag == "style"]
    if not ref_styles:
        return [f"line {styles[0].line}: template has no <style> block"], ""
    ref = style_lines(ref_styles[0].text())
    got = style_lines(styles[0].text())
    lead = len(styles[0].text()) - len(styles[0].text().lstrip("\n"))
    for i, want in enumerate(ref):
        if i >= len(got) or got[i] != want:
            return [f"line {styles[0].line + lead + i}: style block differs from the template stylesheet (expected: {want.strip()})"], ""
    return [], f"one style block, starts with the template's {len(ref)} lines"


def check_style_attr(doc):
    bad = []
    for e in doc.all:
        if "style" in e.attrs:
            if not (e.has("bar") and WIDTH_RE.match(e.attrs["style"].strip())):
                bad.append(f"line {e.line}: style attribute on <{e.tag}> ({e.attrs['style']})")
    return bad, "style attributes only set width on .bar"


def masked_text(doc):
    text = doc.text
    keep = list(text)

    def blank(a, b):
        for i in range(a, b):
            if keep[i] != "\n":
                keep[i] = " "

    for m in re.finditer(r"<style[^>]*>(.*?)</style>", text, re.S | re.I):
        css = m.group(1)
        base = m.start(1)
        for r in re.finditer(r":root\b[^{]*\{|@page\b[^{]*\{", css):
            blank(base + r.start(), base + block_end(css, r.end() - 1))
    for m in re.finditer(r"<svg\b.*?</svg>", text, re.S | re.I):
        blank(m.start(), m.end())
    return "".join(keep)


def check_hex(doc):
    bad = []
    text = masked_text(doc)
    for m in HEX_RE.finditer(text):
        h = m.group(1).lower()
        if len(h) == 3:
            h = "".join(c * 2 for c in h)
        if h in BRAND_HEX:
            bad.append(f"line {line_of(text, m.start())}: brand hex #{m.group(1)}, use var(...)")
    return bad, "no brand hex outside :root, @page and svg"


def check_mark(doc):
    bad = []
    marks = [e for e in doc.all if e.tag == "span" and e.has("mark")]
    for m in marks:
        if m.text().strip() != "DWD":
            bad.append(f"line {m.line}: mark reads \"{m.text().strip()}\", must be \"DWD\"")
    return bad, f"{len(marks)} marks read DWD"


def check_headings(doc):
    bad = []
    prev = 0
    n = 0
    for e in doc.all:
        if e.tag in ("h4", "h5", "h6"):
            bad.append(f"line {e.line}: <{e.tag}> is not allowed")
            continue
        if e.tag not in ("h1", "h2", "h3"):
            continue
        level = int(e.tag[1])
        if level > prev + 1:
            bad.append(f"line {e.line}: <{e.tag}> skips a level")
        prev = level
        if level != 1:
            continue
        n += 1
        t = e.text().strip()
        m = re.match(r"^(\d+)\. \S", t)
        if not m or int(m.group(1)) != n:
            bad.append(f"line {e.line}: h1 \"{t}\" should start \"{n}. \"")
        hdr = e.prev_element()
        if hdr is None or hdr.tag != "header" or not hdr.has("doc-header"):
            bad.append(f"line {e.line}: h1 not directly preceded by header.doc-header")
            continue
        parts = hdr.elements()
        right = parts[-1].text().strip() if parts else ""
        hm = re.match(r"^(\d+) - ", right)
        if not hm or int(hm.group(1)) != n:
            bad.append(f"line {hdr.line}: header text \"{right}\" should start \"{n} - \"")
    if n == 0:
        bad.append("line 1: no h1 sections")
    return bad, f"{n} numbered h1 sections with header blocks, no h4 to h6, no skipped levels"


def check_footer(doc):
    bad = [f"line {e.line}: screen footer .doc-footer is not used" for e in doc.all if e.has("doc-footer")]
    return bad, "no doc-footer"


def check_captions(doc):
    bad = []
    tables = doc.find("table")
    for n, t in enumerate(tables, 1):
        cap = t.prev_element()
        if cap is None or cap.tag != "div" or not cap.has("caption"):
            bad.append(f"line {t.line}: table not preceded by div.caption")
        else:
            m = re.match(r"^Table (\d+)\. \S", cap.text().strip())
            if not m or int(m.group(1)) != n:
                bad.append(f"line {cap.line}: caption should start \"Table {n}. \"")
            if not cap.attrs.get("id") or t.attrs.get("aria-labelledby") != cap.attrs.get("id"):
                bad.append(f"line {t.line}: table aria-labelledby does not point at its caption id")
        if not any(c.tag == "thead" for c in t.elements()):
            bad.append(f"line {t.line}: table has no thead")
        for th in (e for e in t.walk() if e.tag == "th"):
            if th.attrs.get("scope") != "col":
                bad.append(f"line {th.line}: th without scope=\"col\"")
    figures = doc.find("figure")
    for n, f in enumerate(figures, 1):
        caps = [c for c in f.elements() if c.tag == "figcaption" and c.has("caption")]
        if not caps:
            bad.append(f"line {f.line}: figure has no figcaption.caption")
        elif not re.match(rf"^Figure {n}\. \S", caps[0].text().strip()):
            bad.append(f"line {caps[0].line}: caption should start \"Figure {n}. \"")
    return bad, f"{len(tables)} tables and {len(figures)} figures captioned in order"


def rows(table):
    return [e for e in table.walk() if e.tag == "tr"]


def cells(tr):
    out = []
    col = 0
    for c in tr.elements():
        if c.tag in ("td", "th"):
            out.append((col, c))
            try:
                col += max(1, int(c.attrs.get("colspan", "1")))
            except ValueError:
                col += 1
    return out


def check_cells(doc):
    bad = []
    for t in doc.find("table"):
        heads = {}
        thead = [c for c in t.elements() if c.tag == "thead"]
        if thead:
            hrows = rows(thead[0])
            if hrows:
                heads = dict(cells(hrows[-1]))
        for tr in rows(t):
            for col, c in cells(tr):
                if c.tag != "td":
                    continue
                txt = c.text().strip()
                if not txt and not c.elements():
                    bad.append(f"line {c.line}: empty td, write - or n/a")
                elif NUM_RE.match(txt):
                    if not c.has("num"):
                        bad.append(f"line {c.line}: number cell \"{txt}\" needs class num")
                    h = heads.get(col)
                    if h is not None and not h.has("num"):
                        bad.append(f"line {h.line}: header \"{h.text().strip()}\" of a number column needs class num")
    return bad, "no empty cells; number cells and headers carry num"


def check_callouts(doc):
    bad = []
    section = 0
    seen = {}
    for e in doc.all:
        if e.tag == "h1":
            section += 1
        if e.tag == "div" and e.has("callout"):
            first = e.children[0] if e.children else None
            lead = ""
            for c in e.children:
                if isinstance(c, El):
                    first = c
                    break
                lead += c
            if lead.strip() or not isinstance(first, El) or first.tag != "strong" or first.text().strip() not in LABELS:
                bad.append(f"line {e.line}: callout must start <strong>Note:</strong>, <strong>Key point:</strong> or <strong>Warning:</strong>")
            if section in seen:
                bad.append(f"line {e.line}: second callout in h1 section {section} (first at line {seen[section]})")
            else:
                seen[section] = e.line
    return bad, f"{len(seen)} callouts, at most one per h1 section"


def check_charts(doc):
    bad = []
    charts = [e for e in doc.all if e.has("bar-chart") or e.tag == "svg"]
    for e in charts:
        if e.attrs.get("role") != "img":
            bad.append(f"line {e.line}: <{e.tag}> chart needs role=\"img\"")
        if e.tag == "svg":
            kids = [c.tag for c in e.elements()]
            if "title" not in kids or "desc" not in kids:
                bad.append(f"line {e.line}: svg needs <title> and <desc>")
    return bad, f"{len(charts)} charts with role img; svg has title and desc"


def check_quotes(doc):
    bad = []
    qs = doc.find("blockquote")
    for q in qs:
        tags = {e.tag for e in q.walk()}
        if "p" not in tags or "footer" not in tags:
            bad.append(f"line {q.line}: blockquote needs a p and a footer")
    return bad, f"{len(qs)} quotes with p and footer"


def check_escapes(doc):
    bad = []
    text = doc.text
    style_spans = [(m.start(), m.end()) for m in re.finditer(r"<style[^>]*>.*?</style>", text, re.S | re.I)]
    for m in BARE_AMP_RE.finditer(text):
        if not any(a <= m.start() < b for a, b in style_spans):
            bad.append(f"line {line_of(text, m.start())}: bare &, write &amp;")
    for ln in doc.tree.text_lt:
        bad.append(f"line {ln}: < in text, write &lt;")
    return bad, "no bare & and no < in text"


CHECKS = [
    ("encoding", check_encoding),
    ("head", check_head),
    ("resources", check_resources),
    ("style-block", check_style_block),
    ("style-attr", check_style_attr),
    ("brand-hex", check_hex),
    ("mark", check_mark),
    ("headings", check_headings),
    ("no-footer", check_footer),
    ("captions", check_captions),
    ("cells", check_cells),
    ("callouts", check_callouts),
    ("charts", check_charts),
    ("quotes", check_quotes),
    ("escapes", check_escapes),
]


def find_browser():
    for name in ("chrome", "chrome.exe", "msedge", "msedge.exe", "google-chrome", "google-chrome-stable", "chromium", "chromium-browser"):
        hit = shutil.which(name)
        if hit:
            return hit
    bases = [os.environ.get(env) for env in ("PROGRAMFILES", "PROGRAMFILES(X86)", "LOCALAPPDATA")]
    if os.name == "nt":
        bases += [r"C:\Program Files", r"C:\Program Files (x86)"]
    for base in bases:
        if not base:
            continue
        for rel in (("Google", "Chrome", "Application", "chrome.exe"), ("Microsoft", "Edge", "Application", "msedge.exe")):
            p = Path(base).joinpath(*rel)
            if p.is_file():
                return str(p)
    return None


def print_render(path):
    browser = find_browser()
    if not browser:
        return "SKIP", "no Chrome or Edge found"
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
        pdf = Path(tmp) / "out.pdf"
        cmd = [
            browser, "--headless=new", "--disable-gpu", "--no-first-run", "--no-default-browser-check",
            f"--user-data-dir={Path(tmp) / 'profile'}", "--no-pdf-header-footer",
            f"--print-to-pdf={pdf}", Path(path).resolve().as_uri(),
        ]
        try:
            subprocess.run(cmd, capture_output=True, timeout=180)
        except (OSError, subprocess.TimeoutExpired) as exc:
            return "FAIL", f"{Path(browser).name} did not finish: {exc}"
        if not pdf.is_file():
            return "FAIL", f"{Path(browser).name} wrote no PDF"
        pages = len(re.findall(rb"/Type\s*/Page(?![A-Za-z])", pdf.read_bytes()))
    return "PASS", f"{Path(browser).name} printed {pages} pages"


def main(argv):
    if len(argv) != 2:
        print("usage: python scripts/check_html.py path/to/file.html")
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
    status, detail = print_render(path)
    print(f"{status} print-render: {detail}")
    failed = failed or status == "FAIL"
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
