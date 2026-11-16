/* Paper-page drafts, laid over a built `p/<id>/index.html`.
 * Builds every variant's markup once, then `ppApply(state)` switches between
 * them with `data-pp-*` on <html>. The panel (index.html) calls ppApply. */
(function () {
"use strict";
var KEY = "probe.pg.paper.v1";
var doc = document, html = doc.documentElement;
var IX = window.ProbeIndex || {}, DATA = window.PL_PAPER || {};
var head = doc.querySelector(".paper-head-inner");
var acts = doc.querySelector("[data-paper-acts]");
var pid = acts ? acts.getAttribute("data-paper-id") : "";
var paper = (IX.papers || []).filter(function (p) { return p.id === pid; })[0] || {};
var extra = DATA[pid] || {};
var lead = doc.querySelector("header.lead");
var thesis = lead && lead.querySelector(".thesis");
var tagline = lead && lead.querySelector(".thesis-sub");
var tldr = lead && lead.querySelector(".tldr p");
function el(tag, cls, text) { var e = doc.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; return e; }

/* ── 머리 ─────────────────────────────────────────────── */
var crumbRow = head.querySelector(".crumb-row");
var title = head.querySelector(".paper-title");
var authors = head.querySelector(".paper-authors");
var actbar = head.querySelector(".actbar");
var srcGroup = actbar.querySelector(".src-group");
var date = (crumbRow.querySelector(".crumb-date") || {}).textContent || "";

// chip line: the pillar chips (the popup opens from them), the arXiv number
var chips = el("div", "pp-chips");
(paper.pillars || []).forEach(function (p) {
  var c = el("span", "chip pillar", p); c.setAttribute("data-p", p); c.setAttribute("tabindex", "0");
  c.setAttribute("role", "button"); chips.appendChild(c);
});
var num = el("a", "pp-num", pid); num.href = "https://arxiv.org/abs/" + pid; num.target = "_blank";
chips.appendChild(num);
var metric = el("span", "pp-metric", extra.metric || ""); chips.appendChild(metric);
var dateTop = el("span", "pp-date pp-date-top", date.replace("재작성 ", "작성 ")); chips.appendChild(dateTop);
head.insertBefore(chips, crumbRow.nextSibling);

// a crumb chip slot: chips beside the breadcrumb
var crumbChips = el("span", "pp-crumbchips");
(paper.pillars || []).forEach(function (p) {
  var c = el("span", "chip pillar", p); c.setAttribute("data-p", p); c.setAttribute("tabindex", "0"); crumbChips.appendChild(c);
});
crumbRow.querySelector(".crumb").appendChild(crumbChips);

// the Korean thesis, above or below the English title
var ko = el("p", "pp-ko", thesis ? thesis.textContent : "");
head.insertBefore(ko, title);
var koBelow = el("p", "pp-ko pp-ko-below", thesis ? thesis.textContent : "");
title.parentNode.insertBefore(koBelow, title.nextSibling);
var tag = el("p", "pp-tag", tagline ? tagline.textContent : (paper.tagline || ""));
authors.parentNode.insertBefore(tag, authors);

// the one-paragraph summary, folded or open
var td = el("details", "pp-tldr");
var sm = el("summary", "", "한 문단 요약"); td.appendChild(sm);
var tdBody = el("div", "pp-tldr-b"); if (tldr) tdBody.innerHTML = tldr.innerHTML; td.appendChild(tdBody);
authors.parentNode.insertBefore(td, authors.nextSibling);

// date + size at the end of the byline
var meta = el("p", "pp-meta");
var sz = el("span", "pp-size", extra.size || ""); meta.appendChild(sz);
var dateMeta = el("span", "pp-date pp-date-meta", date.replace("재작성 ", "작성 ")); meta.appendChild(dateMeta);
authors.appendChild(meta);

/* ── 탭 ───────────────────────────────────────────────── */
var tabs = doc.querySelector(".tabs");
[].forEach.call(tabs.querySelectorAll(".tab .en"), function (e) { e.remove(); });
var tFull = doc.getElementById("t-full");
var tabMin = el("span", "pp-tabmin", (extra.size || "").split(" · ")[0].replace("본문 ", "")); tFull.appendChild(tabMin);
var tools = el("div", "pp-tabtools"); tabs.appendChild(tools);

/* ── 상세: 막 ─────────────────────────────────────────── */
var NOUN = [["문제", "무엇이 막혔나"], ["방법", "무엇을 바꿨나"], ["검증", "정말 되는가"], ["시사점", "연구 축에 걸리는 것"]];
var pdivs = [].slice.call(doc.querySelectorAll("#main .pdiv"));
pdivs.forEach(function (d, i) {
  d.id = "pp-act-" + (i + 1);
  var n = NOUN[i] || ["", ""];
  var nn = el("span", "pp-noun"); nn.appendChild(el("b", "", n[0])); nn.appendChild(el("span", "", n[1]));
  d.insertBefore(nn, d.querySelector(".pt").nextSibling);
});
var tocEl = doc.querySelector(".toc");
var grps = tocEl ? [].slice.call(tocEl.querySelectorAll(".toc-grp")) : [];
grps.forEach(function (g, i) {
  var gl = g.querySelector(".toc-gl"); var n = NOUN[i] || ["", ""];
  var nn = el("span", "pp-noun"); nn.appendChild(el("b", "", n[0])); nn.appendChild(el("span", "", n[1]));
  gl.parentNode.insertBefore(nn, gl.nextSibling);
});

// the act strip: four acts, the current one underlined, and a 목차 button
var bar = el("div", "pp-actbar"); var barIn = el("div", "pp-actbar-in"); bar.appendChild(barIn);
var actLinks = pdivs.map(function (d, i) {
  var a = el("a", "pp-actlink"); a.href = "#" + d.id;
  a.appendChild(el("span", "pp-al-n", String(i + 1)));
  a.appendChild(el("span", "pp-al-q", d.querySelector(".pt").textContent));
  a.appendChild(el("span", "pp-al-noun", (NOUN[i] || [""])[0]));
  barIn.appendChild(a); return a;
});
var tocBtn = el("button", "pp-tocbtn"); tocBtn.type = "button";
tocBtn.innerHTML = '<svg viewBox="0 0 16 16" width="15" height="15" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"><path d="M3 4h10M3 8h10M3 12h6"/></svg><span>목차</span>';
barIn.appendChild(tocBtn);
var full = doc.getElementById("p-full");
full.insertBefore(bar, full.firstChild);

// the 목차 sheet (phone): the same contents, from below
var sheet = el("div", "pp-sheet"); sheet.hidden = true;
var sheetIn = el("div", "pp-sheet-in");
var sh = el("div", "pp-sheet-h"); sh.appendChild(el("b", "", "목차"));
var x = el("button", "pp-sheet-x", "×"); x.type = "button"; sh.appendChild(x);
sheetIn.appendChild(sh);
if (tocEl) { var cl = tocEl.cloneNode(true); cl.classList.add("pp-toc-clone"); var tt = cl.querySelector(".toc-title"); if (tt) tt.remove(); sheetIn.appendChild(cl); }
sheet.appendChild(sheetIn); doc.body.appendChild(sheet);
function closeSheet() { sheet.hidden = true; }
tocBtn.addEventListener("click", function () { sheet.hidden = false; });
x.addEventListener("click", closeSheet);
sheet.addEventListener("click", function (e) { if (e.target === sheet || e.target.closest("a")) closeSheet(); });
doc.addEventListener("keydown", function (e) { if (e.key === "Escape") closeSheet(); });

// reading progress under the nav
var prog = el("div", "pp-prog"); prog.appendChild(el("i")); doc.body.appendChild(prog);

// current act — for the strip, the 'current act only' contents and progress
var article = doc.getElementById("main");
function spy() {
  var y = Math.max(doc.querySelector(".site-nav").getBoundingClientRect().bottom, bar.getBoundingClientRect().bottom) + 40, cur = 0;
  pdivs.forEach(function (d, i) { if (d.getBoundingClientRect().top < y) cur = i; });
  actLinks.forEach(function (a, i) { a.classList.toggle("on", i === cur); });
  grps.forEach(function (g, i) { g.classList.toggle("pp-cur", i === cur); });
  var r = article.getBoundingClientRect();
  var f = Math.min(1, Math.max(0, (-r.top + 120) / Math.max(1, r.height - innerHeight + 120)));
  prog.firstChild.style.transform = "scaleX(" + (full.hidden ? 0 : f) + ")";
}
addEventListener("scroll", spy, { passive: true }); addEventListener("resize", spy);

/* ── 상세: 확인 문제 접기 ─────────────────────────────── */
[].forEach.call(doc.querySelectorAll("#main .quiz"), function (q) {
  var lab = q.querySelector(".q-label"); if (!lab) return;
  var t = el("button", "pp-qtoggle"); t.type = "button";
  t.innerHTML = '<span class="pp-q-l">확인</span><span class="pp-q-t"></span><span class="pp-q-c">›</span>';
  t.querySelector(".pp-q-t").textContent = (q.querySelector(".qq") || {}).textContent || "";
  q.insertBefore(t, q.firstChild);
  t.addEventListener("click", function () { q.classList.toggle("pp-open"); });
});

/* ── 상태 ─────────────────────────────────────────────── */
var homeOfLinks = srcGroup.parentNode, acNext = acts.nextSibling;
function apply(s) {
  Object.keys(s).forEach(function (k) { html.setAttribute("data-pp-" + k, s[k]); });
  // links and library buttons: in the head, or at the right end of the tab strip
  if (s.bar === "tabs") { tools.appendChild(srcGroup); tools.appendChild(acts); }
  else { homeOfLinks.insertBefore(srcGroup, homeOfLinks.firstChild); homeOfLinks.appendChild(acts); }
  td.open = s.tldr === "open";
  // the strip's top: under the nav, and under the tab strip when that sticks
  var tw = doc.querySelector(".tabs-wrap");
  html.style.setProperty("--pp-tabs-h", s.stick === "stick" ? tw.offsetHeight + "px" : "0px");
  spy();
}
window.ppApply = apply;
var saved = {}; try { saved = JSON.parse(localStorage.getItem(KEY) || "{}") || {}; } catch (e) {}
apply(saved);
html.setAttribute("data-pp", "");
// the panel asks for a tab
window.ppTab = function (t) { var b = doc.getElementById(t === "full" ? "t-full" : "t-glance"); if (b) b.click(); setTimeout(spy, 50); };
[].forEach.call(doc.querySelectorAll(".tab"), function (b) { b.addEventListener("click", function () { setTimeout(spy, 30); }); });
})();
