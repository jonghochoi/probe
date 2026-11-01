#!/usr/bin/env python3
"""Check the adaptation track's folder against adaptation/AUTHORING.md.

`/adapt` writes nothing into the repository: a kit is drawn by NotebookLM
from someone else's paper, so it lives in the folder `PROBE_ADAPT_DIR` names
(`adaptation/SETUP.md` §2). No build reads it and no workflow can, which
makes this lint the track's only gate — the routine runs it before a brief
is sent and before the check note is final.

Checks, grouped by the contract section they enforce:

  AUTHORING §2   every `<id>--<alias>/` names a paper with a rewrite, and
             a folder holding a drawn file has a `check.md`.
  AUTHORING §3-1 the brief — the H1 alias and the metadata line agree with
             the folder name; only kind headers, each once and not empty;
             no `C#`, `METHOD §n`, `cfg:` or `path:line` anchor; with
             `PROBE_PRIVATE_DIR` set, no `MY-METHOD.md` §6 string.
  AUTHORING §3-2 the check note — the H1 alias and the metadata line agree
             with the folder name; the four headers verbatim and in order;
             every source the rewrite or an arXiv URL of that id; every
             생성물 bullet a kind and `점검함` / `미점검` (audio always
             `미점검`) with its files present; 대조 its count line and every
             bullet a verdict, a place and — but for `원문 없음` — a quote
             anchor; every 남은 오류 bullet a place.
  AUTHORING §5   brief length per kind.

Precision over recall, mirroring the repo's other gates: every check keys off
a literal token the contract fixes. Whether a grade is right is the check
pass's (AUTHORING §6).

Usage (repo root):
    python3 linters/check-adaptation-format.py [ADAPT_DIR]

No ADAPT_DIR -> `$PROBE_ADAPT_DIR`. The checkout's `analysis/` is resolved
next to this file.

Exit codes: 0 = clean / 1 = violations found / 2 = no folder to scan.
"""
from __future__ import annotations

import argparse
import glob
import os
import re
import sys

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# AUTHORING §2: `<alias>` is the alias with whitespace runs turned into `-`,
# so it holds no whitespace and no `--`, the separator.
_KIT_NAME = re.compile(r"^(\d{4}\.\d{5})--([^\s/-]+(?:-[^\s/-]+)*)$")
# Each kind as the NotebookLM CLI names it, and the files a run downloads for it.
_KINDS = {
    "slide-deck": ("slides.pdf", "slides.pptx"),
    "infographic": ("infographic.png",),
    "audio": ("audio.mp3",),
    "mind-map": ("mindmap.json",),
}
_SPINE = ("## 1 소스", "## 2 생성물", "## 3 대조", "## 4 남은 오류")
_VERDICTS = ("맞음", "틀림", "과장", "원문 없음")
_NONE = "- 없음"
_BRIEF_MAX = 2000

_BRIEF_H1 = " 각색 지시문"
_NOTE_H1 = " 각색 점검 — "
_BRIEF_META = re.compile(r"^Paper: (\d{4}\.\d{5}) · Rewrite: analysis/(\d{4}\.\d{5})\.md · Run: \d{4}-\d{2}-\d{2}$")
_NOTE_META = re.compile(
    r"^Paper: (\d{4}\.\d{5}) · Rewrite: analysis/(\d{4}\.\d{5})\.md · Notebook: \S+ · Run: \d{4}-\d{2}-\d{2}$"
)
_COUNT = re.compile(r"^점검 \d+ · 맞음 \d+ · 틀림 \d+ · 과장 \d+ · 원문 없음 \d+$")
_PLACE = re.compile(r"slide-deck p\.\d+|infographic|mind-map")
_DRAWN = re.compile(r"^- `(slide-deck|infographic|audio|mind-map)` — .+ · (점검함|미점검)$")
# A quote is the original's own words (`distinction/AUTHORING.md` §4): a
# section and at least a clause of English.
_QUOTE = re.compile(r'원문 §[^\s"]+ "[^"]*[A-Za-z][^"]{11,}"')
# The private side's anchors (`distinction/AUTHORING.md` §4) — none may
# leave the machine in a brief.
_PRIVATE = (
    re.compile(r"`C\d+`"),
    re.compile(r"`METHOD §[0-6]`"),
    re.compile(r"`cfg:[^`\s]+`"),
    re.compile(r"`[^`\s:]+:\d+`"),
)
_H2 = re.compile(r"^## ")
_BULLET = re.compile(r"^- ")
_FENCE = re.compile(r"^\s*(```|~~~)")

Finding = tuple[str, int, str]


def alias_slug(alias: str) -> str:
    return re.sub(r"\s+", "-", alias.strip())


def _read(path: str) -> list[str] | None:
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read().splitlines()
    except OSError:
        return None


def _sections(lines: list[str]) -> list[tuple[str, int, list[tuple[int, str]]]]:
    """(header, line, [(line, text)…]) per `##`."""
    out: list[tuple[str, int, list[tuple[int, str]]]] = []
    for lineno, raw in enumerate(lines, start=1):
        if _H2.match(raw):
            out.append((raw.rstrip(), lineno, []))
        elif out:
            out[-1][2].append((lineno, raw))
    return out


def _bullets(body: list[tuple[int, str]]) -> list[tuple[int, str]]:
    """Top-level `- ` bullets outside fences, continuation lines folded in."""
    out: list[tuple[int, str]] = []
    in_fence = False
    for lineno, raw in body:
        if _FENCE.match(raw):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if _BULLET.match(raw):
            out.append((lineno, raw))
        elif out and raw.startswith("  ") and raw.strip():
            out[-1] = (out[-1][0], out[-1][1] + " " + raw.strip())
    return out


def _opens_with(raw: str) -> str | None:
    text = raw[2:].lstrip()
    for v in sorted(_VERDICTS, key=len, reverse=True):
        for form in (v, f"**{v}**"):
            if text == form or text.startswith(form + " ") or text.startswith(form + ","):
                return v
    return None


def forbidden_strings() -> list[str]:
    """`MY-METHOD.md` §6 bullets, when `PROBE_PRIVATE_DIR` names the folder."""
    private = os.environ.get("PROBE_PRIVATE_DIR", "")
    lines = _read(os.path.join(private, "MY-METHOD.md")) if private else None
    out: list[str] = []
    for header, _, body in _sections(lines or []):
        if header == "## 6. 외부 발화 금지":
            for _, raw in _bullets(body):
                text = raw[2:].strip()
                if text and not (text.startswith("<") and text.endswith(">")):
                    out.append(text)
    return out


def _head(name: str, lines: list[str], h1: str, meta: re.Pattern, pid: str, slug: str,
          findings: list[Finding]) -> None:
    """The H1 names the folder's alias and the metadata line its id."""
    if not lines or not lines[0].startswith("# ") or h1 not in lines[0]:
        findings.append((name, 1, f"§3 line 1 is not the H1 `# <alias>{h1.rstrip(' —')}…`"))
    elif alias_slug(lines[0][2:].partition(h1)[0]) != slug:
        findings.append((name, 1, f"§2 the folder name says `{slug}`, the H1 alias makes `{alias_slug(lines[0][2:].partition(h1)[0])}`"))
    meta_line = next((ln for ln, raw in enumerate(lines[1:], start=2) if raw.strip()), None)
    mm = meta.match(lines[meta_line - 1]) if meta_line else None
    if not mm:
        findings.append((name, meta_line or 2, "§3 metadata line does not match the contract"))
    elif (mm.group(1), mm.group(2)) != (pid, pid):
        findings.append((name, meta_line, "§3 metadata `Paper:` / `Rewrite:` disagree with the folder name"))


def check_brief(name: str, lines: list[str], pid: str, slug: str, forbidden: list[str]) -> list[Finding]:
    findings: list[Finding] = []
    _head(name, lines, _BRIEF_H1, _BRIEF_META, pid, slug, findings)
    seen: set[str] = set()
    for header, lineno, body in _sections(lines):
        kind = header[3:].strip()
        if kind not in _KINDS:
            findings.append((name, lineno, f"§3-1 `{header}` is not a kind — {', '.join(_KINDS)}"))
        elif kind in seen:
            findings.append((name, lineno, f"§3-1 `{kind}` stands twice"))
        seen.add(kind)
        text = "\n".join(raw for _, raw in body).strip()
        if not text:
            findings.append((name, lineno, f"§3-1 `{kind}` holds no instruction"))
        elif len(text) > _BRIEF_MAX:
            findings.append((name, lineno, f"§5 `{kind}` is {len(text)} characters, ceiling is {_BRIEF_MAX}"))
    if not seen:
        findings.append((name, 0, "§3-1 the brief holds no kind"))
    for lineno, raw in enumerate(lines, start=1):
        hit = next((m for p in _PRIVATE if (m := p.search(raw))), None)
        if hit:
            findings.append((name, lineno, f"§3-1 `{hit.group(0).strip('`')}` is a private anchor — the brief leaves the machine"))
        if any(text in raw for text in forbidden):
            findings.append((name, lineno, "§3-1 carries a `MY-METHOD.md` §6 string"))
    return findings


def check_note(name: str, lines: list[str], folder: str, pid: str, slug: str, forbidden: list[str]) -> list[Finding]:
    findings: list[Finding] = []
    _head(name, lines, _NOTE_H1, _NOTE_META, pid, slug, findings)
    headers = [(raw.rstrip(), ln) for ln, raw in enumerate(lines, start=1) if _H2.match(raw)]
    if [h for h, _ in headers] != list(_SPINE):
        findings.append((name, headers[0][1] if headers else 0, "§3-2 the `##` headers are not the four of the spine, verbatim and in order"))
    sections = {h: body for h, _, body in _sections(lines)}
    sources, made, checked, standing = _SPINE

    public = re.compile(
        rf"^- (`analysis/{re.escape(pid)}\.md`|<?https://arxiv\.org/(?:html|pdf|abs)/{re.escape(pid)}(?:v\d+)?>?)$"
    )
    listed = _bullets(sections.get(sources, []))
    if not listed:
        findings.append((name, 0, "§3-2 소스 holds no bullet"))
    for ln, raw in listed:
        if not public.match(raw.strip()):
            findings.append((name, ln, f"§1 source is neither `analysis/{pid}.md` nor an arXiv URL of {pid} — only public material goes to NotebookLM"))

    kinds = _bullets(sections.get(made, []))
    if not kinds:
        findings.append((name, 0, "§3-2 생성물 holds no bullet"))
    for ln, raw in kinds:
        dm = _DRAWN.match(raw.strip())
        if not dm:
            findings.append((name, ln, "§3-2 생성물 bullet is not `` `<kind>` — <files> · 점검함 | 미점검 ``"))
            continue
        kind, state = dm.groups()
        if kind == "audio" and state != "미점검":
            findings.append((name, ln, "§3-2 audio is `미점검` — no reader here hears it"))
        for f in _KINDS[kind]:
            if not os.path.exists(os.path.join(folder, f)):
                findings.append((name, ln, f"§3-2 `{kind}` is listed but `{f}` is not in the kit"))

    body = [(ln, raw) for ln, raw in sections.get(checked, []) if raw.strip()]
    if not body or not _COUNT.match(body[0][1].strip()):
        findings.append((name, body[0][0] if body else 0, "§3-2 대조 does not open with `점검 N · 맞음 n · 틀림 n · 과장 n · 원문 없음 n`"))
    for ln, raw in _bullets(sections.get(checked, [])):
        if raw.strip() == _NONE:
            continue
        verdict = _opens_with(raw)
        if not verdict:
            findings.append((name, ln, "§3-2 대조 bullet does not open with 맞음 / 틀림 / 과장 / 원문 없음"))
        if not _PLACE.search(raw):
            findings.append((name, ln, "§3-2 대조 bullet names no place — `slide-deck p.<n>`, `infographic` or `mind-map`"))
        if verdict != "원문 없음" and not _QUOTE.search(raw):
            findings.append((name, ln, "§4 대조 bullet lacks a quote anchor"))

    left = _bullets(sections.get(standing, []))
    if standing in sections and not left:
        findings.append((name, 0, "§3-2 남은 오류 holds no bullet (write `- 없음` when nothing stands)"))
    for ln, raw in left:
        if raw.strip() != _NONE and not _PLACE.search(raw):
            findings.append((name, ln, "§3-2 남은 오류 bullet names no place"))

    for lineno, raw in enumerate(lines, start=1):
        if any(text in raw for text in forbidden):
            findings.append((name, lineno, "§3-2 carries a `MY-METHOD.md` §6 string"))
    return findings


def check_kit(folder: str, forbidden: list[str]) -> list[Finding]:
    kit = os.path.basename(folder)
    m = _KIT_NAME.match(kit)
    if not m:
        return [(kit, 0, "§2 folder name is not `<arxiv-id>--<alias>`")]
    pid, slug = m.groups()
    findings: list[Finding] = []
    if not os.path.exists(os.path.join(_REPO_ROOT, "analysis", pid + ".md")):
        findings.append((kit, 0, f"§1 analysis/{pid}.md does not exist — the paper has no rewrite"))
    brief = _read(os.path.join(folder, "brief.md"))
    note = _read(os.path.join(folder, "check.md"))
    drawn = [f for files in _KINDS.values() for f in files if os.path.exists(os.path.join(folder, f))]
    if brief is None:
        findings.append((kit, 0, "§2 no `brief.md` — the brief is the record of what was sent"))
    else:
        findings += check_brief(kit + "/brief.md", brief, pid, slug, forbidden)
    if note is None:
        if drawn:
            findings.append((kit, 0, f"§2 {', '.join(drawn)} drawn but no `check.md` — the kit is unchecked"))
    else:
        findings += check_note(kit + "/check.md", note, folder, pid, slug, forbidden)
    return findings


def check_folder(folder: str) -> list[Finding]:
    forbidden = forbidden_strings()
    findings: list[Finding] = []
    for path in sorted(glob.glob(os.path.join(folder, "*", ""))):
        path = os.path.dirname(path)
        if os.path.basename(path).startswith("."):
            continue
        findings += check_kit(path, forbidden)
    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Check the adaptation track's folder against adaptation/AUTHORING.md."
    )
    parser.add_argument("folder", nargs="?", default=os.environ.get("PROBE_ADAPT_DIR"),
                        help="the adaptation folder (default: $PROBE_ADAPT_DIR)")
    args = parser.parse_args(argv)

    if not args.folder or not os.path.isdir(args.folder):
        sys.stderr.write("[check-adaptation-format] no folder — pass a path or set PROBE_ADAPT_DIR\n")
        return 2

    findings = check_folder(args.folder)
    for name, lineno, message in findings:
        print(f"{name}:{lineno}: {message}")
    if findings:
        print(f"\n[check-adaptation-format] {len(findings)} violation(s) in {args.folder}")
        return 1
    print(f"[check-adaptation-format] clean — {args.folder}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
