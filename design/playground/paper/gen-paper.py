"""Data for the paper-page drafts: per paper, the metric line from the
rewrite's front matter and the size line the related cards print, written as
assets/plpaper-data.js.

usage: PROBE_REPO=<checkout> python3 gen-paper.py <built-site-dir> <id>...
"""
import json, os, re, sys
from pathlib import Path

REPO = Path(os.environ.get("PROBE_REPO", "/home/user/probe"))
OUT = Path(sys.argv[1])
data = {}
for pid in sys.argv[2:]:
    fm = (REPO / "analysis" / f"{pid}.md").read_text().split("\n---\n", 1)[0]
    m = re.search(r"^metric: (.*)$", fm, re.M)
    size = ""
    for page in (OUT / "p").glob("*/index.html"):
        h = page.read_text()
        r = re.search(r'href="\.\./' + re.escape(pid) + r'/index\.html">.*?<span class="rel-size">(.*?)</span>', h, re.S)
        if r:
            size = r.group(1); break
    data[pid] = {"metric": m.group(1).strip() if m else "", "size": size}
(OUT / "assets" / "plpaper-data.js").write_text(
    "window.PL_PAPER = " + json.dumps(data, ensure_ascii=False) + ";\n", encoding="utf-8")
print(data)
