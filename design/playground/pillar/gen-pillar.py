"""Pillar-page drafts for the 조율실: one page per axis and an overview, every
variant's markup present and switched by `data-*` on <html> (assets/pl.css).

usage: python3 gen-pillar.py <built-site-dir>
"""
import re
import sys
from pathlib import Path

import os
# The checkout whose site/ carries the redesign (the port branch, or main once
# it lands); the design branch keeps only the records.
REPO = Path(os.environ.get("PROBE_REPO") or Path(__file__).resolve().parents[3])
sys.path.insert(0, str(REPO / "site"))
from builder import components as c, corpus, comparisons, scouting  # noqa: E402
from builder.corpus import PILLAR_LABELS, PILLAR_NAMES  # noqa: E402
from builder.pages import _alias, scout_split, _md_date, _scout_chip  # noqa: E402

OUT = Path(sys.argv[1])
papers, _ = corpus.discover()
papers.sort(key=lambda p: p.order_key, reverse=True)
by_id = {p.stem: p for p in papers}
comps, _ = comparisons.discover(by_id)
comps.sort(key=lambda x: x.order_key, reverse=True)
runs, _ = scouting.discover()

# MASTER §4: the one line each pillar row states, in English.
EN_LINE = {}
for line in (REPO / "context" / "MASTER.md").read_text().splitlines():
    m = re.match(r"^\| (P\d) — [^|]+\| ([^|]+) \|", line)
    if m:
        EN_LINE[m.group(1)] = m.group(2).strip()
# A Korean rendering of the same line — a draft for the owner to rewrite.
KO_DRAFT = {
    "P0": "손 조작 정책을 배우는 데이터와, 그 위에서 성능을 재는 도구. 데이터가 방법보다 먼저다.",
    "P1": "행동 디코더를 둘 이상의 전문가로 나누는 방식 — 몸과 손이라는 몸의 이음매, 빠름과 느림이라는 시간의 이음매.",
    "P2": "감각이 정책에 닿기 전에 일어나는 일 — 공간 정합, 손가락별 접촉 귀속, 인코더.",
    "P3": "동역학을 예측하는 모델을 스택에 들이는 방식 — 역할, 통합, 예측 공간, 조건화.",
    "P4": "배포 전에 정하는 것들 — 계보 × 코퍼스 × 레시피 — 과 그 뒤 그것을 지키는 비용.",
}

# The decisions each pillar file defines: title, the bolded current choice,
# whether it is OPEN, and how many rewrites cite it.
DECS = {}
for code in PILLAR_NAMES:
    text = (REPO / "context" / f"{code}.md").read_text()
    for m in re.finditer(r"^#### \[(D\w{3})\] (.+?) \((P\d)\)( — \*\*OPEN\*\*)?\n- (.+)$", text, re.M):
        did, title, _, open_, bullet = m.groups()
        bold = re.search(r"\*\*(.+?)\*\*", bullet.replace("**Working, not settled** —", ""))
        choice = bold.group(1) if bold else re.sub(r"[*`]", "", bullet)[:80]
        DECS.setdefault(code, []).append({"id": did, "title": title, "choice": choice,
                                          "open": bool(open_)})
cited = {}
for p in papers:
    for did in set(re.findall(r"\bD\d[A-HJ-NP-Z]{2}\b", p.body)):
        cited[did] = cited.get(did, 0) + 1


def chip(code, href=True):
    if href:
        return (f'<a class="chip pillar" data-p="{code}" href="../{code}/index.html" '
                f'title="{c.esc(PILLAR_LABELS[code])}">{code}</a>')
    return f'<span class="chip pillar" data-p="{code}">{code}</span>'


def chips(codes):
    return "".join(chip(k) for k in codes)


def axis_line(here):
    items = "".join(
        f'<a class="rail-item pillar" data-p="{k}" href="../{k}/index.html"'
        + (' aria-current="page"' if k == here else "")
        + f'><span class="sw"></span><b>{k}</b><span class="rl">{c.esc(PILLAR_LABELS[k])}</span></a>'
        for k in PILLAR_NAMES)
    return (f'<nav class="pline pl-axes" aria-label="다른 연구 축">'
            f'<span class="pline-ic" aria-hidden="true">{c.icon("layers", 18)}</span>'
            f'<div class="pline-items" data-pline>{items}</div></nav>')


def chip_row(here):
    return ('<nav class="pl-chiprow" aria-label="다른 연구 축">'
            + "".join(f'<a class="pl-sw{" is-on" if k == here else ""}" href="../{k}/index.html">'
                      f'{chip(k, False)}<span>{c.esc(PILLAR_LABELS[k])}</span></a>' for k in PILLAR_NAMES)
            + "</nav>")


def paper_rows(ps):
    return "".join(
        f'<li class="tl-row{" pl-more" if i >= 5 else ""}"><span class="tl-id">{_md_date(p.date)}</span>'
        f'<a class="tl-id" href="https://arxiv.org/abs/{p.stem}" target="_blank" rel="noopener">{p.stem}</a>'
        f'<a class="tl-main" href="../../p/{p.stem}/index.html"><span class="tl-t">{c.esc(p.title)}</span>'
        f'<span class="tl-g">{c.esc(p.tagline)}</span></a><span class="tl-p">{chips(p.filed)}</span></li>'
        for i, p in enumerate(ps))


def paper_cards(ps):
    return "".join(
        f'<a class="card{" pl-more" if i >= 6 else ""}" href="../../p/{p.stem}/index.html">'
        f'<div class="card-top"><p class="card-chips">{"".join(chip(k, False) for k in p.filed)}</p>'
        f'<span class="card-id">{_md_date(p.date)}</span></div>'
        f'<h3>{c.esc(_alias(p))}</h3><p class="card-title">{c.esc(p.title)}</p>'
        f'<p class="card-gist">{c.esc(p.tagline)}</p></a>'
        for i, p in enumerate(ps))


def scout_rows(code):
    out = []
    for run in runs[:4]:
        first, more = scout_split(run)
        for p in first + more:
            pick = next((k for k in p.picks if k.pillar == code and k.full), None)
            if pick:
                out.append((run.date, pick.rank, p, pick))
    out.sort(key=lambda t: (t[0], -t[1]), reverse=True)
    return "".join(
        f'<li class="tl-row"><span class="tl-id">{_md_date(d)}</span>'
        f'<a class="tl-id" href="https://arxiv.org/abs/{p.paper_id}" target="_blank" rel="noopener">{p.paper_id}</a>'
        f'<a class="tl-main" href="../../s/{d}/index.html#p-{p.paper_id}"><span class="tl-t">{c.esc(p.alias)}</span>'
        f'<span class="tl-g">{c.esc(re.sub(r"[*`]", "", p.gist))}</span></a>'
        f'<span class="tl-p">{_scout_chip(pick)}</span></li>'
        for d, _, p, pick in out[:8]), len(out)


def cmp_cards(cs):
    if not cs:
        return '<p class="sh-empty">아직 이 축의 비교가 없습니다.</p>'
    out = []
    for x in cs:
        names = [_alias(by_id[i]) if i in by_id else i for i in x.paper_ids]
        st = x.stances if len(x.stances) == len(names) else [""] * len(names)
        sides = "".join(f'<p class="cmp-st"><b>{c.esc(n)}</b><span>{c.esc(s)}</span></p>' for n, s in zip(names, st))
        out.append(f'<a class="card cmp-card" href="../../c/{x.slug}/index.html">'
                   f'<div class="card-top"><p class="card-chips">{"".join(chip(k, False) for k in x.pillars)}</p>'
                   f'<span class="card-id">{_md_date(x.date)}</span></div><h3>{c.esc(x.title)}</h3>'
                   + (f'<p class="cmp-common"><b>공통</b>{c.esc(x.common)}</p>' if x.common else "")
                   + f'<div class="cmp-sts">{sides}</div></a>')
    cols = min(3, len(cs))
    return f'<div class="cards" style="--cols:{cols}">{"".join(out)}</div>'


def dec_list(code):
    ds = sorted(DECS.get(code, []), key=lambda d: -cited.get(d["id"], 0))
    return "".join(
        f'<li class="pl-dec"><div class="pl-dec-t"><b>{c.esc(d["title"])}</b>'
        + ('<span class="pl-open">미결</span>' if d["open"] else "")
        + f'<span class="pl-dcode">{d["id"]}</span></div>'
        f'<p class="pl-dec-c"><span class="pl-dec-k">현재 선택</span>{c.esc(d["choice"])}</p>'
        f'<span class="pl-dec-n">분석 {cited.get(d["id"], 0)}편이 인용</span></li>'
        for d in ds), len(ds)


def noun(n, sub, count=""):
    return (f'<h2 class="hm-h pl-h">{n}<span class="hm-sub">{sub}'
            + (f" · {count}" if count != "" else "") + "</span></h2>")


def pillar_page(code):
    ps = [p for p in papers if code in p.filed]
    cs = [x for x in comps if code in x.pillars]
    srows, n_s = scout_rows(code)
    drows, n_d = dec_list(code)
    head = f'''<header class="pl-head" style="--pc:var(--{code.lower()});--pci:var(--{code.lower()}-ink)">
<div class="pl-head-in">
  <p class="pl-crumb"><a href="../index.html">연구 축</a> › {code}</p>
  <p class="pl-eyebrow">{code} · {c.esc(corpus.PILLAR_NAMES[code])}</p>
  <div class="pl-title">{chip(code, False)}<h1>{c.esc(PILLAR_LABELS[code])}</h1></div>
  <p class="pl-en">{c.esc(corpus.PILLAR_NAMES[code])}</p>
  <p class="pl-desc pl-desc-en">{c.esc(EN_LINE.get(code, ""))}</p>
  <p class="pl-desc pl-desc-ko">{c.esc(KO_DRAFT[code])}<span class="pl-draft">초안</span></p>
  <p class="pl-stats"><span>분석 <b>{len(ps)}</b>편</span><span>비교 <b>{len(cs)}</b>개</span><span>최근 4회차 탐색 <b>{n_s}</b>편</span><span>결정 <b>{n_d}</b>개</span></p>
</div></header>'''
    sec = {
        "a": (noun("분석", "이 축으로 분류된 재작성본", len(ps)),
              f'<div class="pl-a-table"><div class="tl-head" aria-hidden="true"><span>재작성</span><span>arXiv</span><span>논문 · 한 줄</span><span>연구 축</span></div><ul class="tl">{paper_rows(ps)}</ul></div>'
              f'<div class="pl-a-cards cards" style="--cols:3">{paper_cards(ps)}</div>'
              f'<p class="pl-morelink"><a href="../../p/index.html#p={code}">이 축의 분석 {len(ps)}편 모두 보기 →</a></p>'),
        "s": (noun("탐색", "최근 4회차에서 이 축이 고른 논문", n_s),
              f'<div class="tl-head" aria-hidden="true"><span>회차</span><span>arXiv</span><span>논문 · 한 줄</span><span>순위</span></div><ul class="tl">{srows}</ul>'),
        "c": (noun("비교", "이 축의 질문", len(cs)), cmp_cards(cs)),
        "d": (noun("결정", "이 축에서 정한 것과 아직 열린 것", n_d), f'<ul class="pl-decs">{drows}</ul>'),
    }
    counts = {"a": len(ps), "s": n_s, "c": len(cs), "d": n_d}
    names = {"a": "분석", "s": "탐색", "c": "비교", "d": "결정"}
    tabbar = ('<div class="pl-tabs" role="tablist">'
              + "".join(f'<button type="button" role="tab" data-pl-tab="{k}" aria-selected="{str(k == "a").lower()}">'
                        f'{names[k]}<span class="tab-n">{counts[k]}</span></button>' for k in "asdc")
              + "</div>")
    body_secs = "".join(f'<section class="pl-sec" data-sec="{k}">{h}{b}</section>' for k, (h, b) in sec.items())
    body = f"""{head}
<div class="deck pl" data-pl>
  {axis_line(code)}
  {chip_row(code)}
  {tabbar}
  <div class="pl-body">{body_secs}</div>
</div>
"""
    return c.page(title=f"{code} {PILLAR_LABELS[code]} · PROBE", body=body, depth=2,
                  scripts=["pl.js"],
                  extra_head='<link rel="stylesheet" href="../../assets/index.css">'
                             '<link rel="stylesheet" href="../../assets/pl.css">')


def overview_page():
    cards = []
    for code in PILLAR_NAMES:
        n_a = sum(1 for p in papers if code in p.filed)
        n_c = sum(1 for x in comps if code in x.pillars)
        n_d = len(DECS.get(code, []))
        cards.append(
            f'<a class="card pi-card" href="{code}/index.html" style="--pc:var(--{code.lower()});--pci:var(--{code.lower()}-ink)">'
            f'<div class="card-top"><p class="card-chips">{chip(code, False)}</p></div>'
            f'<h3>{c.esc(PILLAR_LABELS[code])}</h3><p class="card-title">{c.esc(corpus.PILLAR_NAMES[code])}</p>'
            f'<p class="card-gist pl-desc-en">{c.esc(EN_LINE.get(code, ""))}</p>'
            f'<p class="card-gist pl-desc-ko">{c.esc(KO_DRAFT[code])}</p>'
            f'<p class="card-tags"><span>분석 {n_a}</span><span>비교 {n_c}</span><span>결정 {n_d}</span></p></a>')
    body = (c.mast(eyebrow="Research axes", title="연구 축, 다섯 갈래로 나눠 봅니다")
            + f'<div class="deck pl"><div class="cards" style="--cols:3">{"".join(cards)}</div></div>')
    return c.page(title="연구 축 · PROBE", body=body, depth=1, scripts=["pl.js"],
                  extra_head='<link rel="stylesheet" href="../assets/index.css">'
                             '<link rel="stylesheet" href="../assets/pl.css">')


for code in PILLAR_NAMES:
    d = OUT / "pl" / code
    d.mkdir(parents=True, exist_ok=True)
    (d / "index.html").write_text(pillar_page(code))
(OUT / "pl" / "index.html").write_text(overview_page())
print("pillar drafts:", ", ".join(f"{k} 분석 {sum(1 for p in papers if k in p.filed)} 결정 {len(DECS.get(k, []))}" for k in PILLAR_NAMES))
