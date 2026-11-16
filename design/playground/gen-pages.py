"""Generate the playground's mock pages: the new first screen, the new scouting page and the pillar pages.

usage: python3 design/playground/gen-pages.py <base-build-dir> <playground-site-dir>
Reads the shell and corpus.json from the base build and writes home.html, scout-new.html,
pillar-P0..P4.html, pillar-index.html and assets/pillar-data.json into the playground site.
"""
import html
import json
import re
import sys
from pathlib import Path

BASE, OUT = Path(sys.argv[1]), Path(sys.argv[2])
REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "site"))
from builder import scouting  # noqa: E402

e = html.escape
corpus = json.loads((BASE / "corpus.json").read_text())
PILL = corpus["pillars"]
papers = sorted(corpus["papers"], key=lambda p: (p.get("date") or "", p["id"]), reverse=True)
comps = sorted(corpus["comparisons"], key=lambda c: c.get("date") or "", reverse=True)
DECS = corpus["decisions"]
runs, _ = scouting.discover()

REAL = {3: "실물 정량, 다수 과제", 2: "실물 정량 결과", 1: "실물 시연만", 0: "실물 결과 없음"}
RANK = {"🥇": "1위", "🥈": "2위", "🥉": "3위", "🌱": "인접", "📋": "추가"}


def run_data(r):
    items = []
    for p in r.papers:
        lead = p.lead
        real = (lead.dims or {}).get("Real")
        tags = [t for t in (REAL.get(real) if real is not None else "", lead.code) if t]
        picks = sorted(p.picks, key=lambda k: (not k.full, k.rank))
        title = p.title[len(p.alias) + 1:].strip() if p.title.startswith(p.alias + ":") else p.title
        items.append({
            "id": p.paper_id, "alias": p.alias, "title": title, "gist": p.gist,
            "group": p.group, "rank": lead.rank, "full": lead.full,
            "picks": [[k.pillar, RANK.get(k.kind, "")] for k in picks], "tags": tags,
        })
    items.sort(key=lambda x: (x["group"] != "shared", not x["full"], x["rank"]))
    near = [{"p": n.pillar, "id": n.paper_id, "alias": n.alias, "cond": n.condition} for n in r.near]
    return {"date": r.date, "arrived": r.arrived, "missing": r.missing, "items": items, "near": near}


RUNS = [run_data(r) for r in runs]

# Robotics and ML calendar. "ok" means the official site states it; "check" means only aggregators agree so far.
EVENTS = [
    {"name": "CoRL 2026", "kind": "conf", "start": "2026-11-09", "end": "2026-11-12", "place": "Austin, Texas", "url": "https://2026.corl.org/", "ok": True},
    {"name": "CVPR 2027 논문 마감", "kind": "deadline", "start": "2026-11-16", "end": "2026-11-16", "place": "AoE", "url": "https://cvpr.thecvf.com/", "ok": False},
    {"name": "RSS 2027 초록 마감", "kind": "deadline", "start": "2026-12-04", "end": "2026-12-04", "place": "AoE", "url": "https://roboticsconference.org/", "ok": True},
    {"name": "Humanoids 2026", "kind": "conf", "start": "2026-12-06", "end": "2026-12-09", "place": "Santa Clara", "url": "https://2026.ieee-humanoids.org/", "ok": True},
    {"name": "NeurIPS 2026", "kind": "conf", "start": "2026-12-06", "end": "2026-12-12", "place": "Sydney", "url": "https://neurips.cc/", "ok": True},
    {"name": "ICML 2027 논문 마감", "kind": "deadline", "start": "2027-01-22", "end": "2027-01-22", "place": "AoE · 잠정", "url": "https://icml.cc/", "ok": False},
    {"name": "ICRA 2027 결과 발표", "kind": "notice", "start": "2027-01-31", "end": "2027-01-31", "place": "", "url": "https://2027.ieee-icra.org/", "ok": True},
    {"name": "RSS 2027 1단계 결과", "kind": "notice", "start": "2027-02-05", "end": "2027-02-05", "place": "", "url": "https://roboticsconference.org/", "ok": True},
    {"name": "IROS 2027 논문 마감", "kind": "deadline", "start": "2027-03-01", "end": "2027-03-01", "place": "", "url": "https://www.ieee-ras.org/events/category/important-dates/", "ok": False},
    {"name": "ICLR 2027", "kind": "conf", "start": "2027-04-26", "end": "2027-04-28", "place": "장소 확인 필요", "url": "https://iclr.cc/Conferences/2027", "ok": False},
    {"name": "ICRA 2027", "kind": "conf", "start": "2027-05-24", "end": "2027-05-28", "place": "Seoul · COEX", "url": "https://2027.ieee-icra.org/", "ok": True},
    {"name": "CVPR 2027", "kind": "conf", "start": "2027-06-22", "end": "2027-06-25", "place": "", "url": "https://cvpr.thecvf.com/", "ok": False},
    {"name": "RSS 2027", "kind": "conf", "start": "2027-07-06", "end": "2027-07-11", "place": "Athens", "url": "https://roboticsconference.org/", "ok": True},
    {"name": "IROS 2027", "kind": "conf", "start": "2027-09-26", "end": "2027-10-01", "place": "Florence", "url": "https://www.ieee-ras.org/events/category/important-dates/", "ok": False},
]

# A draft line per pillar, written here from the pillar's own name; the real one is the owner's to write.
DESC = {
    "P0": "손 조작 정책을 배우고 재는 데 쓰는 데이터와 벤치마크입니다. 무엇을 모으는지, 촉각·힘 같은 신호가 들어 있는지, 무엇으로 성능을 재는지를 봅니다.",
    "P1": "몸과 손처럼 성격이 다른 행동을 하나의 정책이 어떻게 나눠 내는지 봅니다. 입력 양식과 제어 주기를 나누는 방식, 손 출력 공간을 무엇으로 두는지가 중심입니다.",
    "P2": "시각·촉각·고유수용 감각을 어떤 구조로 정책에 넣는지 봅니다. 좌표를 어떻게 부르고, 토큰과 위치 인코딩을 어떻게 짜는지가 중심입니다.",
    "P3": "다음 상태나 결과를 예측하는 모델을 정책 학습과 계획에 어떻게 쓰는지 봅니다. 무엇을 예측하고, 그 예측이 행동으로 어떻게 이어지는지가 중심입니다.",
    "P4": "큰 데이터로 미리 배운 표현을 적은 시연으로 새 과제와 새 손에 옮기는 방법을 봅니다. 무엇을 미리 배우고, 무엇을 얼려 두고 무엇을 다시 배우는지가 중심입니다.",
}

# ── shell: the landing's head and nav, our body, its scripts minus the list's ──
src = (BASE / "index.html").read_text()
head_nav = src[: src.index('<header class="mast">')]
scripts = "".join(s for s in re.findall(r'<script src="assets/[^"]+" defer></script>', src) if "filter.js" not in s and "shelf.js" not in s)
head_nav = head_nav.replace("</head>", '<link rel="stylesheet" href="assets/entry.css">\n<link rel="stylesheet" href="assets/scout-new.css">\n</head>', 1)


def shell(current, body):
    h = head_nav.replace(' aria-current="page"', "")
    if current:
        h = h.replace(f'<a href="{current}">', f'<a href="{current}" aria-current="page">')
    return h + body + scripts + "\n</body>\n</html>\n"


def chip(p, extra=""):
    return f'<span class="chip pillar" data-p="{p}">{p}{extra}</span>'


def md(d):
    return d[5:].replace("-", ".") if d else ""


# ── the scouting page ────────────────────────────────────────────────
scout_body = f'''<header class="mast"><div class="mast-inner"><div class="mast-text"><p class="mast-eyebrow">Across the research axes</p><div class="mast-line"><h1>탐색, 읽을 논문을 먼저 고릅니다</h1></div></div></div></header>
<main class="sn" id="main">
  <aside class="sn-side">
    <section class="sn-cal" aria-label="달력">
      <div class="sn-cal-h"><button type="button" class="sn-nav" data-cal="-1" aria-label="이전 달">‹</button><h2 id="sn-month"></h2><button type="button" class="sn-nav" data-cal="1" aria-label="다음 달">›</button></div>
      <div class="sn-grid" id="sn-grid" role="grid"></div>
      <p class="sn-legend"><span><i class="lg run"></i>탐색 회차 · 누르면 그 회차로</span></p>
    </section>
  </aside>
  <section class="sn-run" id="sn-run" aria-live="polite"></section>
</main>
<script>window.SN_RUNS = {json.dumps(RUNS, ensure_ascii=False)}; window.SN_EVENTS = []; window.SN_PILLARS = {json.dumps({k: v["label"] for k, v in PILL.items()}, ensure_ascii=False)};</script>
<script src="assets/scout-new.js"></script>
'''
(OUT / "scout-new.html").write_text(shell("s/index.html", scout_body))

# ── pillar pages ─────────────────────────────────────────────────────
recent_runs = runs[:4]
for code, meta in PILL.items():
    ps = [p for p in papers if code in p["pillars"]]
    cs = [c for c in comps if code in c["pillars"]]
    ds = sorted([(k, v) for k, v in DECS.items() if v.get("pillar") == code], key=lambda kv: -kv[1].get("rewrites", 0))
    sp = []
    for r in recent_runs:
        for p in r.papers:
            if code in p.pillars:
                k = next(k for k in p.picks if k.pillar == code)
                if k.full:
                    sp.append((r.date, p, RANK.get(k.kind, "")))
    sp.sort(key=lambda x: (x[0], -{"1위": 3, "2위": 2, "3위": 1}.get(x[2], 0)), reverse=True)
    others = "".join(f'<a class="pl-sw{" is-on" if k == code else ""}" href="pillar-{k}.html">{chip(k)}<span>{e(v["label"])}</span></a>' for k, v in PILL.items())
    prow = "".join(f'<li><a href="p/{p["id"]}/index.html"><span class="ent-d">{md(p["date"])}</span><b>{e(p.get("alias") or p["id"])}</b><span class="ent-t">{e(p["tagline"])}</span></a></li>' for p in ps[:5])
    crow = "".join(f'<li><a href="c/{c["slug"]}/index.html"><span class="ent-d">{md(c["date"])}</span><b>{e(c["title"])}</b></a></li>' for c in cs[:4]) or '<li class="pl-empty">아직 이 축의 비교가 없습니다.</li>'
    srow = "".join(f'<li><a href="scout-new.html"><span class="ent-d">{md(d)}</span><span class="pl-rk">{e(rk)}</span><b>{e(p.alias)}</b><span class="ent-t">{e(p.gist)}</span></a></li>' for d, p, rk in sp[:5])
    drow = "".join(f'<li><span class="pl-dcode">{e(k)}</span><span class="pl-dt">{e(v["title"])}</span><span class="pl-dn">분석 {v.get("rewrites", 0)}편</span></li>' for k, v in ds[:6])
    body = f'''<header class="pl-head" style="--pc:var(--{code.lower()});--pci:var(--{code.lower()}-ink)"><div class="pl-head-in">
  <p class="pl-crumb"><a href="pillar-index.html">연구 축</a> › {code}</p>
  <div class="pl-title">{chip(code)}<h1>{e(meta["label"])}</h1></div>
  <p class="pl-en">{e(meta["name"])}</p>
  <p class="pl-desc">{e(DESC[code])} <span class="pl-draft">설명 초안</span></p>
  <p class="pl-stats"><span><b>{len(ps)}</b>편 분석</span><span><b>{len(cs)}</b>개 비교</span><span>최근 4회차에서 <b>{len(sp)}</b>편 선정</span></p>
</div></header>
<main class="ent pl" id="main">
  <nav class="pl-switch" aria-label="다른 연구 축">{others}</nav>
  <div class="pl-cols">
    <section><h2 class="ent-h">최근 분석</h2><ul class="ent-rows">{prow}</ul><p class="ent-more-row"><a class="ent-more" href="index.html">이 축의 분석 {len(ps)}편 모두 보기<span aria-hidden="true">→</span></a></p></section>
    <section><h2 class="ent-h">최근 탐색에서 고른 논문</h2><ul class="ent-rows">{srow}</ul></section>
  </div>
  <div class="pl-cols">
    <section><h2 class="ent-h">이 축의 비교</h2><ul class="ent-rows">{crow}</ul></section>
    <section><h2 class="ent-h">이 축에서 내린 결정</h2><ul class="pl-decs">{drow}</ul></section>
  </div>
</main>'''
    (OUT / f"pillar-{code}.html").write_text(shell(None, body))

# ── the pillar overview: five cards, one per axis ────────────────────
cards = []
for code, meta in PILL.items():
    n_a = sum(1 for p in papers if code in p["pillars"])
    n_c = sum(1 for c in comps if code in c["pillars"])
    n_s = sum(1 for p in runs[0].papers if code in p.pillars)
    cards.append(f'''<a class="pi-card" href="pillar-{code}.html" style="--pc:var(--{code.lower()});--pci:var(--{code.lower()}-ink)">
<span class="pi-top">{chip(code)}<b>{e(meta["label"])}</b></span><span class="pi-en">{e(meta["name"])}</span>
<span class="pi-desc">{e(DESC[code])}</span>
<span class="pi-n"><span><b>{n_a}</b>편 분석</span><span><b>{n_c}</b>개 비교</span><span>이번 탐색 <b>{n_s}</b>편</span></span></a>''')
body = f'''<header class="mast"><div class="mast-inner"><div class="mast-text"><p class="mast-eyebrow">Research axes</p><div class="mast-line"><h1>연구 축, 다섯 갈래로 나눠 봅니다</h1></div></div></div></header>
<main class="ent pi" id="main"><div class="pi-grid">{"".join(cards)}</div><p class="pi-note">축 설명은 초안입니다.</p></main>'''
(OUT / "pillar-index.html").write_text(shell(None, body))
print("ok", len(RUNS), "runs", len(EVENTS), "events")


# ── pillar data for the playground's pop-over and filter banner ──────
def choices():
    """The bold phrase of each decision's current-choice bullet, read from context/ for the private mock only."""
    out = {}
    for f in sorted((REPO / "context").glob("P[0-9].md")):
        text = f.read_text()
        for m in re.finditer(r"^#### \[(D\w+)\] (.+?)\n- (.+)$", text, re.M):
            did, bullet = m.group(1), m.group(3)
            bold = re.findall(r"\*\*(.+?)\*\*", bullet)
            pick = next((b for b in bold if not b.startswith("Working") and not b.startswith("Boundary")), "")
            out[did] = {"choice": pick, "open": "OPEN" in m.group(2)}
    return out


CH = choices()
pdata = {}
for code, meta in PILL.items():
    ds = sorted([(k, v) for k, v in DECS.items() if v.get("pillar") == code], key=lambda kv: -kv[1].get("rewrites", 0))
    pdata[code] = {
        "label": meta["label"], "name": meta["name"], "desc": DESC[code],
        "papers": sum(1 for p in papers if code in p["pillars"]), "comps": sum(1 for c in comps if code in c["pillars"]),
        "scout": sum(1 for p in runs[0].papers if code in p.pillars),
        "decisions": [{"id": k, "title": v["title"], "rewrites": v.get("rewrites", 0), **CH.get(k, {"choice": "", "open": False})} for k, v in ds],
    }
(OUT / "assets" / "pillar-data.json").write_text(json.dumps(pdata, ensure_ascii=False))

# ── home: a short front page above the three tabs ────────────────────
import datetime as _dt
TODAY = "2026-11-15"
up = [ev for ev in EVENTS if ev["end"] >= TODAY][:4]


def dday(ev):
    d = (_dt.date.fromisoformat(ev["start"]) - _dt.date.fromisoformat(TODAY)).days
    return "진행 중" if d <= 0 else f"D-{d}"


r0 = runs[0]
first = [p for p in r0.papers if p.group == "shared" or (p.lead.full and p.lead.rank == 1)]
newest, cmp0 = papers[0], comps[0]
ev_html = "".join(f'''<a class="hm-ev {ev["kind"]}{"" if ev["ok"] else " unsure"}" href="{ev["url"]}" target="_blank" rel="noopener">
<span class="hm-dd">{dday(ev)}</span><b>{e(ev["name"])}</b><span>{md(ev["start"]) if ev["start"] == ev["end"] else md(ev["start"]) + "–" + md(ev["end"])}{(" · " + e(ev["place"])) if ev["place"] else ""}</span></a>''' for ev in up)
pl_html = "".join(f'''<li><span class="hm-pchip">{chip(code)}</span><b>{e(meta["label"])}</b><span class="hm-pn">분석 {pdata[code]["papers"]} · 이번 탐색 {pdata[code]["scout"]}</span></li>''' for code, meta in PILL.items())
home = f'''<main class="hm" id="main">
<section class="hm-top">
  <p class="hm-eyebrow">PROBE · Dexterous manipulation</p>
  <h1 class="hm-t">손 조작 연구, 이번 주에 볼 것</h1>
  <ul class="hm-now">
    <li><a href="scout-new.html"><span>탐색</span><b>{md(r0.date)} 회차 · {len(first)}편 먼저 권함</b></a></li>
    <li><a href="p/{newest["id"]}/index.html"><span>새 분석</span><b>{e(newest.get("alias") or newest["id"])}</b></a></li>
  </ul>
</section>
<section class="hm-blk"><h2 class="hm-h">다가오는 일정 <span class="hm-hs">학회 · 투고 마감</span></h2><div class="hm-evs">{ev_html}</div></section>
<div class="hm-two">
  <section class="hm-blk"><h2 class="hm-h">최근에 들어온 것</h2><ul class="hm-feed">
    <li><a href="p/{newest["id"]}/index.html"><span class="hm-k">분석<small>{md(newest["date"])}</small></span><b>{e(newest.get("alias") or newest["id"])}</b><span class="hm-s">{e(newest["tagline"])}</span></a></li>
    <li><a href="scout-new.html"><span class="hm-k">탐색<small>{md(r0.date)} 회차</small></span><b>{e(first[0].alias)}</b><span class="hm-s">{e(first[0].gist)}</span></a></li>
    <li><a href="c/{cmp0["slug"]}/index.html"><span class="hm-k">비교<small>{md(cmp0["date"])}</small></span><b>{e(cmp0["title"])}</b></a></li>
  </ul></section>
  <section class="hm-blk"><h2 class="hm-h">연구 축</h2><ul class="hm-pl">{pl_html}</ul></section>
</div>
</main>'''
(OUT / "home.html").write_text(shell(None, home))
print("home ok", len(pdata))


# ── home, second pass: room to fill a desktop, and headings the playground can rename ──
def first_sentence(t):
    return t.split("니다.")[0] + "니다." if "니다." in t else t


up6 = [ev for ev in EVENTS if ev["end"] >= TODAY][:6]
tops = [p for p in r0.papers if p.lead.full]
tops.sort(key=lambda p: (p.group != "shared", p.lead.rank))
feed = []
for p in papers[:3]:
    feed.append(("분석", p["date"], f'p/{p["id"]}/index.html', p.get("alias") or p["id"], p["tagline"]))
for p in tops[:2]:
    feed.append(("탐색", r0.date, "scout-new.html", p.alias, p.gist))
for c in comps[:1]:
    feed.append(("비교", c["date"], f'c/{c["slug"]}/index.html', c["title"], ""))
feed.sort(key=lambda x: x[1], reverse=True)


def feed_li(kind, d, href, t, sub, extra=False):
    when = md(d) + (" 회차" if kind == "탐색" else "")
    cls = ' class="hm-x"' if extra else ""
    subh = '<span class="hm-s">' + e(sub) + "</span>" if sub else ""
    return (f'<li{cls}><a href="{href}"><span class="hm-k">{kind}<small>{when}</small></span>'
            f'<b>{e(t)}</b>{subh}</a></li>')


lean = [next(x for x in feed if x[0] == k) for k in ("분석", "탐색", "비교")]
feed_html = "".join(feed_li(*x) for x in lean) + "".join(feed_li(*x, extra=True) for x in feed if x not in lean)


def col(kind, items):
    return f'<section class="hm-col"><h3>{kind}</h3><ul>{"".join(items)}</ul></section>'


cols_html = (col("분석", [f'<li><a href="p/{p["id"]}/index.html"><b>{e(p.get("alias") or p["id"])}</b><span>{e(p["tagline"])}</span></a></li>' for p in papers[:3]])
             + col(f"탐색 · {md(r0.date)} 회차", [f'<li><a href="scout-new.html"><b>{e(p.alias)}</b><span>{e(p.gist)}</span></a></li>' for p in tops[:3]])
             + col("비교", [f'<li><a href="c/{c["slug"]}/index.html"><b>{e(c["title"])}</b></a></li>' for c in comps[:3]]))
ev6 = "".join(f'''<a class="hm-ev {ev["kind"]}{"" if ev["ok"] else " unsure"}{" hm-x" if i >= 4 else ""}" href="{ev["url"]}" target="_blank" rel="noopener">
<span class="hm-dd">{dday(ev)}</span><b>{e(ev["name"])}</b><span>{md(ev["start"]) if ev["start"] == ev["end"] else md(ev["start"]) + "–" + md(ev["end"])}{(" · " + e(ev["place"])) if ev["place"] else ""}</span></a>''' for i, ev in enumerate(up6))
import datetime as _dt2
_newest = _dt2.date.fromisoformat(papers[0]["date"])
_mon = _newest - _dt2.timedelta(days=_newest.weekday())
WEEKS = [_mon - _dt2.timedelta(weeks=k) for k in range(7, -1, -1)]


def weekly(code):
    n = [0] * len(WEEKS)
    for p in papers:
        if code not in p["pillars"]:
            continue
        d = _dt2.date.fromisoformat(p["date"]); m = d - _dt2.timedelta(days=d.weekday())
        if m in WEEKS:
            n[WEEKS.index(m)] += 1
    return n


def spark(code):
    n = weekly(code); top = max(max(n), 1)
    bars = "".join(f'<i style="--h:{max(6, round(v / top * 100))}%;--d:{k * 60}ms" title="{WEEKS[k].strftime("%m.%d")} 주 {v}편"></i>' for k, v in enumerate(n))
    return f'<span class="hm-spark" aria-label="최근 8주 분석 편수 {sum(n)}편">{bars}</span>'


_mark = re.search(r'<svg class="probe-mark".*?</svg>', src, re.S).group(0).replace('width="19" height="19"', 'width="64" height="64"')
_week_new = sum(1 for p in papers if _dt2.date.fromisoformat(p["date"]) >= _mon)
def _thesis(pid):
    f = (REPO / "analysis") / f"{pid}.md"
    for line in f.read_text().splitlines() if f.exists() else []:
        if line.startswith("# "):
            return line[2:].strip()
    return ""


_np = papers[0]
_dl = next((ev for ev in EVENTS if ev["kind"] == "deadline" and ev["end"] >= TODAY), None)
_dd = (_dt2.date.fromisoformat(_dl["start"]) - _dt2.date.fromisoformat(TODAY)).days if _dl else 0
_left = "내일이에요" if _dd == 1 else ("오늘이에요" if _dd <= 0 else f"{_dd}일 남았어요")
LINES = {
    "pick": f'이번 주엔 <b>{e(_np.get("alias") or _np["id"])}</b>부터 읽어 보세요. “{e(_thesis(_np["id"]))}”',
    "scout": f'{md(r0.date)} 탐색에서 <b>{e(first[0].alias)}</b> 외 {len(first) - 1}편을 먼저 골라 뒀어요.',
    "deadline": (f'<b>{e(_dl["name"])}</b>이 {_left}. 마감 지나고 볼 글은 아래에 모아 둘게요.' if _dl else ""),
    "count": f'이번 주 새 분석 <b>{_week_new}편</b>, {md(r0.date)} 탐색은 <b>{len(first)}편</b>을 먼저 권해요.',
}
_kinds = "".join(f'<img class="hm-mki {tone}" data-kind="{k}" src="assets/mascots/probe-{k}{suf}.svg" alt="" width="72" height="72">'
                 for k in ("analysis", "scouting", "comparison", "ideation") for tone, suf in (("t-light", ""), ("t-dark", "-dark")))
MASCOT = (f'<div class="hm-mascot" aria-hidden="true"><span class="hm-mk"><span class="hm-mkb">{_mark}</span>{_kinds}</span><div class="hm-lines">'
          + "".join(f'<p class="hm-bubble" data-line="{k}">{v}</p>' for k, v in LINES.items() if v) + '</div></div>')


def pl_side(code):
    ps = [p for p in papers if code in p["pillars"]]
    new = sum(1 for p in ps if _dt2.date.fromisoformat(p["date"]) >= _mon)
    lat = ps[0] if ps else None
    late = f'<span class="hm-plat">최근 · <b>{e(lat.get("alias") or lat["id"])}</b> {md(lat["date"])}</span>' if lat else ""
    return late + (f'<span class="hm-pnew">이번 주 +{new}</span>' if new else '<span class="hm-pnew is-zero">이번 주 0</span>')

pl6 = "".join(f'''<li><span class="hm-pchip">{chip(code)}</span><span class="hm-pt"><b>{e(meta["label"])}</b><span class="hm-pd">{e(first_sentence(DESC[code]))}</span></span>{spark(code)}{pl_side(code)}<span class="hm-pn">분석 {pdata[code]["papers"]} · 이번 탐색 {pdata[code]["scout"]}</span></li>''' for code, meta in PILL.items())
home = f'''<main class="hm" id="main">
{MASCOT}
<section class="hm-top">
  <p class="hm-eyebrow">PROBE · Dexterous manipulation</p>
  <h1 class="hm-t">손 조작 연구, 이번 주에 볼 것</h1>
  <ul class="hm-now">
    <li><a href="scout-new.html"><span>탐색</span><b>{md(r0.date)} 회차 · {len(first)}편 먼저 권함</b></a></li>
    <li><a href="p/{newest["id"]}/index.html"><span>새 분석</span><b>{e(newest.get("alias") or newest["id"])}</b></a></li>
  </ul>
</section>
<section class="hm-blk hm-colsblk"><h2 class="hm-h" data-k="feed">최근에 들어온 것</h2><div class="hm-cols">{cols_html}</div></section>
<section class="hm-blk hm-evblk"><h2 class="hm-h" data-k="events">다가오는 일정</h2><div class="hm-evs">{ev6}</div></section>
<div class="hm-two">
  <section class="hm-blk hm-feedblk"><h2 class="hm-h" data-k="feed">최근에 들어온 것</h2><ul class="hm-feed">{feed_html}</ul></section>
  <section class="hm-blk"><h2 class="hm-h" data-k="pillars">연구 축</h2><ul class="hm-pl">{pl6}</ul></section>
</div>
</main>'''
(OUT / "home.html").write_text(shell(None, home))
print("home v2 ok")
