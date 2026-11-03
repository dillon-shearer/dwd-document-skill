import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SKIP_DIRS = {".kanban95", ".remember", ".git"}
TEXT_EXTS = {".md", ".html", ".py", ".json"}
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
FENCE_RE = re.compile(r"^\s*(```|~~~)")
INLINE_CODE_RE = re.compile(r"`[^`]*`")


def repo_files(exts):
    for path in sorted(ROOT.rglob("*")):
        rel = path.relative_to(ROOT)
        if rel.parts and rel.parts[0] in SKIP_DIRS:
            continue
        if path.is_file() and path.suffix.lower() in exts:
            yield path


def check_skill():
    skill = ROOT / "SKILL.md"
    if not skill.exists():
        return "SKIP", "SKILL.md not present yet"
    lines = skill.read_text(encoding="utf-8", errors="replace").splitlines()
    if not lines or lines[0].strip() != "---":
        return "FAIL", "SKILL.md has no frontmatter block"
    try:
        end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    except StopIteration:
        return "FAIL", "SKILL.md frontmatter block is not closed"
    block = lines[1:end]
    missing = [k for k in ("name:", "description:") if not any(l.startswith(k) for l in block)]
    if missing:
        return "FAIL", "SKILL.md frontmatter missing " + ", ".join(missing)
    return "PASS", "SKILL.md frontmatter has name and description"


def check_links():
    bad = []
    for md in repo_files({".md"}):
        in_fence = False
        text = md.read_text(encoding="utf-8", errors="replace")
        for num, line in enumerate(text.splitlines(), 1):
            if FENCE_RE.match(line):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            for target in LINK_RE.findall(INLINE_CODE_RE.sub("", line)):
                if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target) or target.startswith(("#", "/")):
                    continue
                path_part = target.split("#", 1)[0].split("?", 1)[0]
                if not path_part:
                    continue
                if not (md.parent / path_part).exists():
                    bad.append(f"{md.relative_to(ROOT).as_posix()}:{num} -> {target}")
    if bad:
        return "FAIL", "broken relative links: " + "; ".join(bad)
    return "PASS", "all relative markdown links resolve"


def check_ascii():
    bad = []
    for path in repo_files(TEXT_EXTS):
        data = path.read_bytes()
        for num, line in enumerate(data.split(b"\n"), 1):
            if any(b > 127 for b in line):
                bad.append(f"{path.relative_to(ROOT).as_posix()}:{num}")
    if bad:
        return "FAIL", "non-ASCII bytes in: " + "; ".join(bad)
    return "PASS", "all checked files are ASCII"


def check_docx():
    script = ROOT / "scripts" / "check_docx.py"
    sample = ROOT / "assets" / "dwd-sample.docx"
    if not script.exists() or not sample.exists():
        return "SKIP", "scripts/check_docx.py or assets/dwd-sample.docx not present"
    run = subprocess.run([sys.executable, str(script), str(sample)], capture_output=True, text=True)
    lines = run.stdout.splitlines()
    if run.returncode != 0:
        bad = [l for l in lines if l.startswith("FAIL")] or [run.stderr.strip().splitlines()[-1] if run.stderr.strip() else "exit " + str(run.returncode)]
        return "FAIL", "check_docx.py on assets/dwd-sample.docx: " + "; ".join(bad)
    return "PASS", f"check_docx.py passes {len(lines)} checks on assets/dwd-sample.docx"


def check_pptx():
    script = ROOT / "scripts" / "check_deck.py"
    sample = ROOT / "assets" / "dwd-sample.pptx"
    if not script.exists() or not sample.exists():
        return "SKIP", "scripts/check_deck.py or assets/dwd-sample.pptx not present"
    run = subprocess.run([sys.executable, str(script), str(sample)], capture_output=True, text=True)
    lines = run.stdout.splitlines()
    if run.returncode != 0:
        bad = [l for l in lines if l.startswith("FAIL")] or [run.stderr.strip().splitlines()[-1] if run.stderr.strip() else "exit " + str(run.returncode)]
        return "FAIL", "check_deck.py on assets/dwd-sample.pptx: " + "; ".join(bad)
    return "PASS", f"check_deck.py passes {len(lines)} checks on assets/dwd-sample.pptx"


def check_md():
    script = ROOT / "scripts" / "check_md.py"
    sample = ROOT / "assets" / "dwd-sample.md"
    if not script.exists() or not sample.exists():
        return "SKIP", "scripts/check_md.py or assets/dwd-sample.md not present"
    run = subprocess.run([sys.executable, str(script), str(sample)], capture_output=True, text=True)
    lines = run.stdout.splitlines()
    if run.returncode != 0:
        bad = [l for l in lines if l.startswith("FAIL")] or [run.stderr.strip().splitlines()[-1] if run.stderr.strip() else "exit " + str(run.returncode)]
        return "FAIL", "check_md.py on assets/dwd-sample.md: " + "; ".join(bad)
    return "PASS", f"check_md.py passes {len(lines)} checks on assets/dwd-sample.md"


def main():
    checks = [
        ("skill-frontmatter", check_skill),
        ("md-links", check_links),
        ("ascii-only", check_ascii),
        ("docx-sample", check_docx),
        ("pptx-sample", check_pptx),
        ("md-sample", check_md),
    ]
    failed = False
    for name, fn in checks:
        status, detail = fn()
        print(f"{status} {name}: {detail}")
        failed = failed or status == "FAIL"
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
