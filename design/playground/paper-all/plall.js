/* Paper page, everything decided so far — laid over the site that already
 * implements it. Each option's decided value is the page as built; the other
 * values are drafts switched with `data-pa-*` on <html>. */
(function () {
"use strict";
var KEY = "probe.pg.all.v1";
var doc = document, html = doc.documentElement;
var DATA = window.PL_PAPER || {};
function el(tag, cls, text) { var e = doc.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; return e; }
var head = doc.querySelector(".paper-head-inner");
var acts = doc.querySelector("[data-paper-acts]");
var pid = acts ? acts.getAttribute("data-paper-id") : "";
var extra = DATA[pid] || {};

/* ── 머리 drafts ── */
var title = head.querySelector(".paper-title");
var authors = head.querySelector(".paper-authors");
var thesis = (doc.querySelector(".gh-thesis") || {}).textContent || "";
var koTop = el("p", "pa-ko", thesis); head.insertBefore(koTop, title);
var koBelow = el("p", "pa-ko pa-ko-below", thesis); title.parentNode.insertBefore(koBelow, title.nextSibling);
var desc = (doc.querySelector('meta[name="description"]') || {}).content || "";
var td = el("details", "pa-tldr"); td.appendChild(el("summary", "", "한 문단 요약"));
td.appendChild(el("div", "pa-tldr-b", desc));
authors.parentNode.insertBefore(td, authors.nextSibling);
var size = el("p", "pa-size", extra.size || ""); authors.appendChild(size);
// a line of its own under the byline, for the links and the 서재 pair
var bar = el("div", "pa-bar"); head.appendChild(bar);
var tools = doc.querySelector(".tab-tools");
var src = tools && tools.querySelector(".src-group");
var pair = tools && tools.querySelector(".paper-acts");

/* ── 상세 drafts ── */
var Q = ["무엇이 문제인가", "무엇을 바꿨나", "정말 되는가", "연구축에 무엇이 걸리나"];
[].forEach.call(doc.querySelectorAll("#main .pdiv-named"), function (d, i) {
  d.appendChild(el("span", "pa-q", Q[i] || ""));
});

function apply(s) {
  Object.keys(s).forEach(function (k) { html.setAttribute("data-pa-" + k, s[k]); });
  if (s.bar === "head") { if (src) bar.appendChild(src); if (pair) bar.appendChild(pair); }
  else if (tools) { if (src) tools.appendChild(src); if (pair) tools.appendChild(pair); }
  td.open = false;
  [].forEach.call(doc.querySelectorAll("#main details.quiz"), function (q) { q.open = s.quiz === "open"; });
}
window.ppApply = apply;
window.ppTab = function (t) { var b = doc.getElementById(t === "full" ? "t-full" : "t-glance"); if (b) b.click(); };
var saved = {}; try { saved = JSON.parse(localStorage.getItem(KEY) || "{}") || {}; } catch (e) {}
apply(saved);
html.setAttribute("data-pa", "");
})();
