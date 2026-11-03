import re

EM_DASH = "\u2014"
EN_DASH = "\u2013"
BANNED = [
    r"delv(?:e|es|ed|ing)",
    r"robust(?:ly|ness)?",
    r"leverag(?:e|es|ed|ing)",
    r"seamless(?:ly)?",
    r"crucial(?:ly)?",
    r"landscapes?",
    r"journeys?",
    r"unlock(?:s|ed|ing)?",
    r"harness(?:es|ed|ing)?",
    r"tapestr(?:y|ies)",
    r"navigat(?:e|es|ed|ing)",
    r"in today's fast-paced world",
    r"it is important to note",
    r"in conclusion",
    r"overall,",
    r"not only",
    r"may potentially",
]
BANNED_RE = re.compile(r"(?<![\w-])(?:" + "|".join(BANNED) + r")(?![\w-])", re.IGNORECASE)
DASH_RE = re.compile("[" + EM_DASH + EN_DASH + "]")
URL_RE = re.compile(r"(?:https?|ftp|mailto):[^\s<>()\"']+|www\.[^\s<>()\"']+", re.IGNORECASE)
LETTER_RE = re.compile(r"[A-Za-z]{2,}")


def snippet(text, start, end, width=25):
    a = max(0, start - width)
    b = min(len(text), end + width)
    out = text[a:b].replace(EM_DASH, "<em dash>").replace(EN_DASH, "<en dash>")
    out = " ".join(out.split()).encode("ascii", "replace").decode("ascii")
    return ("..." if a else "") + out + ("..." if b < len(text) else "")


def find_banned(text):
    text = URL_RE.sub(" ", text or "")
    hits = []
    for m in DASH_RE.finditer(text):
        hits.append(("em dash" if m.group() == EM_DASH else "en dash", snippet(text, m.start(), m.end())))
    for m in BANNED_RE.finditer(text):
        hits.append((m.group().lower(), snippet(text, m.start(), m.end())))
    return hits


def is_data(text):
    return LETTER_RE.search(text or "") is None


def scan(items):
    hits = []
    for where, text in items:
        for word, snip in find_banned(text):
            hits.append((where, word, snip))
    return hits


def report(hits, scope):
    for where, word, snip in hits:
        print(f"FAIL prose: {where}: {word} in '{snip}'")
    if not hits:
        print(f"PASS prose: no em dash, en dash or banned word in {scope}")
    return bool(hits)
