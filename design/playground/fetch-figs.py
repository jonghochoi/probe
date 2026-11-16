"""Pick each paper's main figure and fetch a small copy for the playground's figure previews.

usage: python3 design/playground/fetch-figs.py <playground-site-dir>

Two sources, one rule — prefer an overview or architecture figure in the method sections over a
results chart:
- the analysis list: the `probe-figure` fences of `analysis/<id>.md`, written to
  `assets/figs.json` with thumbnails `assets/figs/<id>.webp`
- the new scouting page's recommended papers: the figures of each paper's arXiv HTML edition,
  written to `assets/scout-figs.json` with thumbnails `assets/figs/s-<id>.webp`

Thumbnails are up to 1100 px wide WebP (SVG figures are kept as they are). Needs network access to
arxiv.org and Pillow; a figure that cannot be fetched is left out and its row shows no preview.
"""
import html
import json
import os
import re
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import urljoin

from PIL import Image

SITE = Path(sys.argv[1])
REPO = Path(__file__).resolve().parents[2]
FIGS = SITE / "assets" / "figs"
FIGS.mkdir(parents=True, exist_ok=True)
TMP = Path(tempfile.mkdtemp(prefix="probe-figs-"))
WIDTH = 1100  # sharp at the 640 px preview on a 2x screen

KO_POS = ["개요", "구조", "아키텍처", "파이프라인", "프레임워크", "전체 구성", "전체 흐름", "모듈",
          "overview", "architecture", "pipeline", "framework"]
KO_NEG = ["성공률", "그래프", "곡선", "결과", "비교", "ablation", "절제", "분포", "표준편차", "오차", "정확도",
          "실험", "scaling", "스케일링", "시각화", "예시", "사례", "실패", "실기 구성", "롤아웃", "분석"]
EN_POS = ["overview", "architecture", "pipeline", "framework", "illustration of our", "our method", "our approach", "system"]
EN_NEG = ["success rate", "result", "comparison", "ablation", "performance", "plot", "curve", "qualitative",
          "example", "scaling", "distribution", "vs.", "accuracy"]


def curl(url, dst):
    subprocess.run(["curl", "-s", "-L", "--max-time", "40", "-o", str(dst), url], check=False)
    return dst.exists() and dst.stat().st_size > 200


def thumb(url, stem):
    """Fetch `url` into `assets/figs/<stem>.webp` (or `.svg`) and return its site path, or None."""
    ext = url.rsplit(".", 1)[-1].lower()[:4]
    raw = TMP / f"{stem}.{ext}"
    if not curl(url, raw):
        return None
    if ext == "svg":
        os.replace(raw, FIGS / f"{stem}.svg")
        return f"assets/figs/{stem}.svg"
    try:
        im = Image.open(raw)
        im.load()
        if im.mode in ("P", "LA", "RGBA"):
            im = im.convert("RGBA")
            bg = Image.new("RGB", im.size, (255, 255, 255))
            bg.paste(im, mask=im.split()[-1])
            im = bg
        else:
            im = im.convert("RGB")
        w, h = im.size
        if w > WIDTH:
            im = im.resize((WIDTH, round(h * WIDTH / w)), Image.LANCZOS)
        im.save(FIGS / f"{stem}.webp", "WEBP", quality=80)
        return f"assets/figs/{stem}.webp"
    except Exception:
        return None


def score(i, caption, source, ident, pos, neg):
    low = caption.lower()
    s = sum(3 for k in pos if k in low[:90]) + sum(1 for k in pos if k in low) - sum(2 for k in neg if k in low[:90])
    m = re.search(r"figure\s*(\d+)", source, re.I)
    s += {1: 1, 2: 2, 3: 1}.get(int(m.group(1)) if m else i + 1, 0)
    sec = re.search(r"§\s*(\d+)", source)
    if sec and sec.group(1) in ("2", "3", "4"):
        s += 1
    if re.search(r"부록|appendix", source, re.I) or re.search(r"\.A\d|^A\d|Pt0\.A", ident):
        s -= 4
    return (s, -i)


# ── the analysis list: the rewrite's own figures ──
def analysis_fig(path):
    pid, figs = path.stem, []
    for block in re.findall(r"```probe-figure\n(.*?)```", path.read_text(), re.S):
        try:
            figs.append(json.loads(block))
        except ValueError:
            continue
    if not figs:
        return pid, None
    best = max(enumerate(figs), key=lambda t: score(t[0], t[1].get("caption", ""), t[1].get("source", ""), t[1].get("id", ""), KO_POS, KO_NEG))[1]
    src = thumb(best["url"], pid)
    return pid, src and {"src": src, "caption": best.get("caption", "").strip(), "source": best.get("source", "")}


with ThreadPoolExecutor(6) as ex:
    listed = dict(ex.map(analysis_fig, sorted((REPO / "analysis").glob("2*.md"))))
(SITE / "assets" / "figs.json").write_text(json.dumps({k: v for k, v in listed.items() if v}, ensure_ascii=False))


# ── the scouting page: the arXiv HTML edition of each recommended paper ──
runs = json.loads(re.search(r"window\.SN_RUNS = (\[.*?\]);", (SITE / "scout-new.html").read_text(), re.S).group(1))
picks = []
for run in runs:
    for it in run["items"]:
        if (it.get("group") == "shared" or (it.get("full") and it.get("rank") == 1)) and it["id"] not in picks:
            picks.append(it["id"])


def scout_fig(pid):
    page = TMP / f"{pid}.html"
    if not curl(f"https://arxiv.org/html/{pid}", page):
        return pid, None
    figs = []
    for m in re.finditer(r'<figure[^>]*class="[^"]*ltx_figure[^"]*"[^>]*>(.*?)</figure>', page.read_text(errors="ignore"), re.S):
        img = re.search(r'<img[^>]*src="([^"]+)"', m.group(1))
        if not img or "/icons/" in img.group(1):
            continue
        cap = re.search(r"<figcaption[^>]*>(.*?)</figcaption>", m.group(1), re.S)
        figs.append((img.group(1), html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", cap.group(1) if cap else ""))).strip()))
    if not figs:
        return pid, None

    def rank(t):
        i, (_, cap) = t
        body = re.sub(r"^(figure|fig\.?)\s*\d+\s*[:.]?\s*", "", cap.lower())
        n = re.match(r"(?:figure|fig\.?)\s*(\d+)", cap, re.I)
        return score(i, body, f"Figure {n.group(1) if n else i + 1}", "", EN_POS, EN_NEG)

    src, cap = max(enumerate(figs), key=rank)[1]
    out = thumb(urljoin(f"https://arxiv.org/html/{pid}", src), f"s-{pid}")
    num = re.match(r"((?:Figure|Fig\.?)\s*\d+)", cap)
    return pid, out and {"src": out, "caption": re.sub(r"^(Figure|Fig\.?)\s*\d+\s*[:.]?\s*", "", cap)[:400],
                         "source": (num.group(1).replace("Fig.", "Figure") if num else "Figure") + ", arXiv 원문"}


with ThreadPoolExecutor(6) as ex:
    scouted = dict(ex.map(scout_fig, picks))
(SITE / "assets" / "scout-figs.json").write_text(json.dumps({k: v for k, v in scouted.items() if v}, ensure_ascii=False))
print(f"figures: list {sum(1 for v in listed.values() if v)}/{len(listed)}, scouting {sum(1 for v in scouted.values() if v)}/{len(picks)}")
