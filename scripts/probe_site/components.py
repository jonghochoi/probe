"""HTML components as plain functions returning strings.

No template engine: a handful of page types and ~20 components do not justify
a fifth dependency. Every interpolation goes through `esc()`.
"""

from __future__ import annotations

import html

LINK_LABEL = {
    "arxiv": "arXiv",
    "web": "Website",
    "github": "GitHub",
    "hf": "HuggingFace",
}
LINK_ORDER = {"arxiv": 0, "web": 1, "github": 2, "hf": 3}


# A reticle in the brand orange, inlined as a data URI so the zero-third-party
# rule holds and no extra request is made for 16 px of decoration.
FAVICON = (
    "data:image/svg+xml,"
    "%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E"
    "%3Crect width='32' height='32' rx='8' fill='%23D97757'/%3E"
    "%3Ccircle cx='16' cy='16' r='7.5' fill='none' stroke='%23fff' stroke-width='3'/%3E"
    "%3Ccircle cx='16' cy='16' r='2' fill='%23fff'/%3E%3C/svg%3E"
)


def esc(text: str) -> str:
    return html.escape(str(text), quote=True)


def chip(label: str, cls: str = "", *, href: str = "", data: dict | None = None) -> str:
    attrs = "".join(f' data-{k}="{esc(v)}"' for k, v in (data or {}).items())
    inner = esc(label)
    classes = f"chip {cls}".strip()
    if href:
        return (
            f'<a class="{classes} link" href="{esc(href)}" target="_blank" '
            f'rel="noopener"{attrs}>{inner}</a>'
        )
    return f'<span class="{classes}"{attrs}>{inner}</span>'


def pillar_chips(pillars: list[str]) -> str:
    return "".join(chip(p, "pillar", data={"p": p}) for p in pillars)


def tag_chips(tags: list[str]) -> str:
    return "".join(chip(t, "tag") for t in tags)


def link_chips(links: list[tuple[str, str]], arxiv_id: str) -> str:
    out = []
    for kind, url in sorted(links, key=lambda kv: LINK_ORDER.get(kv[0], 9)):
        label = LINK_LABEL.get(kind, "Link")
        if kind == "arxiv" and arxiv_id and not arxiv_id.startswith("⚠"):
            label = f"arXiv:{arxiv_id}"
        out.append(chip(label, "src-link", href=url))
    return "".join(out)


def callout(icon: str, body_html: str, cls: str = "") -> str:
    classes = f"callout {cls}".strip()
    return (
        f'<div class="{classes}"><span class="ci">{icon}</span>'
        f"<div>{body_html}</div></div>"
    )



def memo_panel(paper_id: str, title: str, paper_url: str, discussions_new: str) -> str:
    return f"""
<button class="memo-fab" data-memo-fab data-has-memo="0" aria-label="메모 열기">
  📝 <span>메모</span><span class="count"></span>
</button>
<div class="scrim" data-scrim data-open="0"></div>
<aside class="memo" data-memo-root data-open="0"
       data-paper-id="{esc(paper_id)}"
       data-paper-title="{esc(title)}"
       data-paper-url="{esc(paper_url)}"
       data-discussions-new="{esc(discussions_new)}"
       aria-label="이 논문의 메모">
  <div class="memo-head">
    <h3>메모</h3>
    <span class="memo-status" data-memo-status aria-live="polite"></span>
  </div>
  <p class="memo-anchor" data-memo-anchor hidden></p>
  <textarea data-memo-input placeholder="읽다가 생긴 의문·확인할 것을 적어두세요."></textarea>
  <p class="memo-note">
    초안은 <strong>이 브라우저에만</strong> 저장됩니다 — 다른 기기에서는 보이지 않고,
    사이트 데이터를 지우면 사라집니다. 남길 메모는 Discussions 로 발행하세요.
  </p>
  <div class="memo-actions">
    <button type="button" class="primary" data-memo-action="publish">Discussions 로 발행</button>
    <button type="button" data-memo-action="export">내보내기</button>
    <span class="spacer"></span>
    <button type="button" class="danger" data-memo-action="clear">삭제</button>
  </div>
</aside>
""".strip()


def page(
    *,
    title: str,
    body: str,
    depth: int,
    description: str = "",
    scripts: list[str] | None = None,
    extra_head: str = "",
    base: str = "",
) -> str:
    """Full document shell.

    Hrefs are relative and computed from page depth, so `--serve` on
    localhost, a `file://` open, and the deployed `/probe/` subpath all behave
    identically — and a future custom domain needs no rebuild.

    `base` overrides that with an absolute prefix. Exactly one page needs it:
    Pages serves `404.html` at whatever depth the bad URL had, so a relative
    `assets/site.css` resolves against `/probe/p/typo/` and the error page
    arrives unstyled with dead links.
    """
    up = base or "../" * depth
    # Classic scripts, not ES modules: `type="module"` is blocked by CORS on
    # `file://`, and opening a built page directly is the fastest way to check
    # a render. Shared state goes on `window.ProbeMemo` instead of exports.
    # theme.js is unconditional — the nav button it drives is on every page.
    script_tags = "".join(
        f'<script src="{up}assets/{s}" defer></script>'
        for s in ["theme.js", *(scripts or [])]
    )
    return f"""<!DOCTYPE html>
<html lang="ko" data-theme="light">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(title)}</title>
{f'<meta name="description" content="{esc(description)}">' if description else ""}
<link rel="icon" href="{FAVICON}">
<link rel="stylesheet" href="{up}assets/fonts.css">
<link rel="stylesheet" href="{up}assets/katex/katex.min.css">
<link rel="stylesheet" href="{up}assets/site.css">
<link rel="stylesheet" href="{up}assets/pygments.css">
{extra_head}
<script>
/* Runs before first paint. Two jobs: set the theme (otherwise a dark-mode
   reader gets a white flash on every navigation) and mark the document as
   scripted, so JS-only controls can hide themselves in CSS instead of
   appearing and then vanishing once a deferred script loads. */
(function(){{document.documentElement.classList.add('js');
try{{var t=localStorage.getItem('probe.theme');
if(!t)t=matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light';
document.documentElement.setAttribute('data-theme',t);}}catch(e){{}}}})();
</script>
</head>
<body>
{nav(up)}
{body}
{script_tags}
</body>
</html>
"""


def nav(up: str) -> str:
    return f"""<nav>
  <div class="nav-inner">
    <a class="nav-logo" href="{up}index.html">PROBE <span>· 분석</span></a>
    <span class="nav-spacer"></span>
    <ul class="nav-links">
      <li><a href="{up}index.html">논문</a></li>
      <li><a href="{up}memos/index.html">메모</a></li>
    </ul>
    <button class="icon-btn" data-theme-toggle aria-label="다크 모드로">☾</button>
  </div>
</nav>"""

