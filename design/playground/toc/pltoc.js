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
      s.title = r.text;
      list.appendChild(s);
    });
    grp.appendChild(list);
    root.appendChild(grp);
  });
  return root;
}
var rail = milestones(); rail.classList.add("ms-rail");
toc.appendChild(rail);
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
  [rail, sheetMs].forEach(function (ms) {
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
addEventListener("resize", follow);
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
