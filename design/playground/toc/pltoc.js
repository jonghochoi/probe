/* Contents drafts, laid over a built `p/<id>/index.html` (after the paper-page
 * port). Builds a milestone list from the server-rendered `.toc`, and the
 * phone-strip variants, then `ppApply(state)` switches with `data-pt-*`. */
(function () {
"use strict";
var KEY = "probe.pg.toc.v1";
var doc = document, html = doc.documentElement;
function el(tag, cls, text) { var e = doc.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; return e; }
var toc = doc.querySelector(".shell > .toc");
if (!toc) return;

/* ── the contents as data ── */
var groups = [].map.call(toc.querySelectorAll(".toc-grp"), function (g) {
  return {
    n: (g.querySelector(".toc-n") || {}).textContent || "",
    label: (g.querySelector(".toc-gl") || {}).textContent || "",
    sub: (g.querySelector(".toc-gs") || {}).textContent || "",
    rows: [].map.call(g.querySelectorAll(".toc-row a"), function (a) {
      return { href: a.getAttribute("href"), text: a.querySelector(".toc-k").textContent };
    })
  };
});
var num = 0;
groups.forEach(function (g) { g.rows.forEach(function (r) { r.num = ++num; }); });

var FLAG = '<svg viewBox="0 0 16 16" width="11" height="11" aria-hidden="true"><path d="M3.6 1.7h8.8v12.6L8 11.1l-4.4 3.2z"/></svg>';

/* ── milestone list (desktop rail and the sheet) ── */
function milestones() {
  var root = el("div", "ms");
  groups.forEach(function (g, gi) {
    var grp = el("div", "ms-g"); grp.setAttribute("data-g", gi);
    var a = el("a", "ms-act"); a.href = "#act-" + g.n;
    a.appendChild(el("span", "ms-node", g.n));
    var t = el("span", "ms-at"); t.appendChild(el("b", "", g.label)); t.appendChild(el("span", "", g.sub));
    a.appendChild(t);
    var cnt = el("span", "ms-cnt", String(g.rows.length)); a.appendChild(cnt);
    grp.appendChild(a);
    var list = el("div", "ms-rows");
    g.rows.forEach(function (r) {
      var s = el("a", "ms-sec"); s.href = r.href; s.setAttribute("data-id", r.href.slice(1));
      s.appendChild(el("span", "ms-dot"));
      s.appendChild(el("span", "ms-num", String(r.num)));
      s.appendChild(el("span", "ms-t", r.text));
      var f = el("button", "ms-flag"); f.type = "button";
      f.setAttribute("aria-label", r.text + " 에 책갈피");
      f.innerHTML = FLAG;
      f.addEventListener("click", function (e) {
        e.preventDefault(); e.stopPropagation();
        var o = toc.querySelector('.toc-mark[data-mark-at="' + r.href.slice(1) + '"]');
        if (o) o.click();
      });
      s.appendChild(f);
      list.appendChild(s);
    });
    grp.appendChild(list);
    root.appendChild(grp);
  });
  return root;
}
var rail = milestones(); rail.classList.add("ms-rail");
toc.appendChild(rail);
// the whole list, opened over the article when the reader reaches for the rail
var fly = milestones(); fly.classList.add("ms-fly");
toc.appendChild(fly);

/* ── a rail scaled to the article's length ── */
var scale = el("div", "sc-rail");
scale.appendChild(el("i", "sc-line"));
var scMarks = [];
groups.forEach(function (g) {
  var a = el("a", "sc-act"); a.href = "#act-" + g.n;
  a.appendChild(el("span", "sc-node", g.n)); a.appendChild(el("span", "sc-name", g.label));
  scale.appendChild(a); scMarks.push({ el: a, id: "act-" + g.n });
  g.rows.forEach(function (r) {
    var t = el("a", "sc-tick"); t.href = r.href; t.setAttribute("data-id", r.href.slice(1));
    t.innerHTML = FLAG;
    scale.appendChild(t); scMarks.push({ el: t, id: r.href.slice(1) });
  });
});
toc.appendChild(scale);
var laidOut = false;
function layoutScale() {
  var art = doc.querySelector("#p-full .article");
  if (!art || full.hidden) return;
  var r = art.getBoundingClientRect(); if (!r.height) return;
  scMarks.forEach(function (m) {
    var h = doc.getElementById(m.id); if (!h) return;
    var f = (h.getBoundingClientRect().top - r.top) / r.height;
    m.el.style.top = (Math.max(0, Math.min(1, f)) * 100).toFixed(2) + "%";
  });
  laidOut = true;
}
// the sheet is built by paper.js from a clone; give it its own list
var sheetToc = doc.querySelector(".toc-sheet .toc");
var sheetMs = null;
if (sheetToc) { sheetMs = milestones(); sheetMs.classList.add("ms-sheet"); sheetToc.appendChild(sheetMs); }

/* ── phone strip variants ── */
var strip = doc.querySelector(".actstrip");
var stripIn = strip && strip.querySelector(".actstrip-in");
var openBtn = strip && strip.querySelector("[data-toc-open]");
var where = el("button", "pt-where"); where.type = "button";
where.innerHTML = '<span class="pt-w-n"></span><span class="pt-w-a"></span><span class="pt-w-s"></span><span class="pt-w-c">⌄</span>';
var segs = el("div", "pt-segs");
groups.forEach(function (g, i) {
  var s = el("a", "pt-seg"); s.href = "#act-" + g.n;
  s.appendChild(el("i")); s.appendChild(el("span", "", g.label));
  segs.appendChild(s);
});
var dots = el("div", "pt-dots");
groups.forEach(function (g, i) {
  var d = el("a", "pt-dot"); d.href = "#act-" + g.n;
  d.appendChild(el("i")); d.appendChild(el("span", "", g.label));
  dots.appendChild(d);
});
if (stripIn) { strip.appendChild(where); strip.appendChild(segs); stripIn.insertBefore(dots, stripIn.firstChild); }
var fab = el("button", "pt-fab"); fab.type = "button";
fab.innerHTML = '<svg viewBox="0 0 16 16" width="15" height="15" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"><path d="M2.6 4h10.8M2.6 8h10.8M2.6 12h6.4"/></svg><span class="pt-fab-a"></span>';
doc.body.appendChild(fab);
function openSheet() { if (openBtn) openBtn.click(); }
where.addEventListener("click", openSheet); fab.addEventListener("click", openSheet);

/* ── where the reader is ── */
var full = doc.getElementById("p-full");
var heads = [];
groups.forEach(function (g, gi) { g.rows.forEach(function (r) { var h = doc.getElementById(r.href.slice(1)); if (h) heads.push({ h: h, g: gi, r: r }); }); });
var actEls = groups.map(function (g) { return doc.getElementById("act-" + g.n); });
function top() {
  return [".site-nav", ".tabs-wrap", ".actstrip"].reduce(function (y, s) {
    var e = doc.querySelector(s); return e && e.offsetHeight ? Math.max(y, e.getBoundingClientRect().bottom) : y;
  }, 0) + 30;
}
function follow() {
  fab.hidden = full.hidden;
  if (full.hidden) return;
  var t = top(), cur = null, g = 0;
  actEls.forEach(function (a, i) { if (a && a.getBoundingClientRect().top < t) g = i; });
  heads.forEach(function (x) { if (x.h.getBoundingClientRect().top < t) cur = x; });
  if (cur && cur.g !== g) cur = null;
  var id = cur ? cur.r.href.slice(1) : "";
  if (!laidOut) layoutScale();
  [].forEach.call(scale.querySelectorAll(".sc-tick"), function (e) { e.classList.toggle("on", e.getAttribute("data-id") === id); });
  [].forEach.call(scale.querySelectorAll(".sc-act"), function (e, i) { e.classList.toggle("on", i === g); });
  [rail, sheetMs, fly].forEach(function (ms) {
    if (!ms) return;
    [].forEach.call(ms.querySelectorAll(".ms-g"), function (e, i) { e.classList.toggle("on", i === g); e.classList.toggle("past", i < g); });
    [].forEach.call(ms.querySelectorAll(".ms-sec"), function (e) {
      var on = e.getAttribute("data-id") === id; e.classList.toggle("on", on);
    });
  });
  // past sections within the current act
  var seen = true;
  [].forEach.call(rail.querySelectorAll(".ms-sec"), function (e) { if (e.classList.contains("on")) seen = false; e.classList.toggle("past", seen && !!id); });
  // strip pieces
  var grp = groups[g] || { n: "", label: "", sub: "" };
  where.querySelector(".pt-w-n").textContent = grp.n;
  where.querySelector(".pt-w-a").textContent = grp.label;
  where.querySelector(".pt-w-s").textContent = cur ? cur.r.text : grp.sub;
  fab.querySelector(".pt-fab-a").textContent = grp.label;
  // per-act fill
  [].forEach.call(segs.children, function (s, i) {
    var a = actEls[i], b = actEls[i + 1];
    var f = 0;
    if (a) {
      var y0 = a.getBoundingClientRect().top, y1 = b ? b.getBoundingClientRect().top : doc.querySelector("#p-full .article").getBoundingClientRect().bottom;
      f = Math.min(1, Math.max(0, (t - y0) / Math.max(1, y1 - y0)));
    }
    s.firstChild.style.transform = "scaleX(" + f + ")";
    s.classList.toggle("on", i === g);
  });
  [].forEach.call(dots.children, function (d, i) { d.classList.toggle("on", i === g); d.classList.toggle("past", i < g); });
}
addEventListener("scroll", function () { requestAnimationFrame(follow); }, { passive: true });
addEventListener("resize", function () { laidOut = false; follow(); });

/* ── the reader's 책갈피, mirrored from the contents' own buttons ── */
function syncMarks() {
  var on = toc.querySelector('.toc-mark[aria-pressed="true"]');
  var id = on ? on.getAttribute("data-mark-at") : "";
  [].forEach.call(doc.querySelectorAll(".ms-sec, .sc-tick"), function (e) {
    e.classList.toggle("marked", e.getAttribute("data-id") === id);
  });
}
new MutationObserver(syncMarks).observe(toc, { subtree: true, attributes: true, attributeFilter: ["aria-pressed"] });
syncMarks();
[].forEach.call(doc.querySelectorAll(".tab"), function (b) { b.addEventListener("click", function () { setTimeout(follow, 30); }); });

function apply(s) {
  Object.keys(s).forEach(function (k) { html.setAttribute("data-pt-" + k, s[k]); });
  follow();
}
window.ppApply = apply;
window.ppTab = function (t) { var b = doc.getElementById(t === "full" ? "t-full" : "t-glance"); if (b) b.click(); setTimeout(follow, 50); };
var saved = {}; try { saved = JSON.parse(localStorage.getItem(KEY) || "{}") || {}; } catch (e) {}
apply(saved);
html.setAttribute("data-pt", "");
})();
