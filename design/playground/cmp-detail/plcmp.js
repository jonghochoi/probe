/* 비교 상세 drafts, laid over the built comparison page. Built once; the
   drafts are `data-pc-*` on <html>: head (now | paper), thesis (both | head |
   drop), tldr (fold | none), toc (none | ms), fold (fold | open), act (now |
   named), cards (now | glow). pcApply(null) is the page as built. */
(function () {
"use strict";
var d = document, H = d.documentElement;
if (H.hasAttribute("data-pc-ready")) return;
function el(t, c, x) { var e = d.createElement(t); if (c) e.className = c; if (x != null) e.textContent = x; return e; }
function q(s, r) { return (r || d).querySelector(s); }
function qa(s, r) { return [].slice.call((r || d).querySelectorAll(s)); }

/* ── 머리 ── */
var inner = q(".paper-head-inner"), title = q(".paper-title", inner);
var chips = qa(".chip-row .chip", inner), metas = qa(".metaline .mi", inner);
var line = el("div", "ph-line pc-line");
chips.forEach(function (c) { line.appendChild(c.cloneNode(true)); });
if (metas[1]) line.appendChild(el("span", "ph-metric", metas[1].textContent));
if (metas[0]) line.appendChild(el("span", "ph-date", "작성 " + metas[0].textContent));
inner.insertBefore(line, inner.firstChild);

/* ── 테제 ── */
var lead = q(".view > header.lead"), thesis = lead && q(".thesis", lead);
var headThesis = el("p", "paper-tagline pc-thesis");
if (thesis) headThesis.innerHTML = thesis.innerHTML;
title.parentNode.insertBefore(headThesis, title.nextSibling);

/* ── 막 ── */
var NOUN = ["질문", "공통", "갈림", "시사점"];
var acts = qa(".view .pdiv");
acts.forEach(function (p, i) {
  var g = p.closest("details.act-fold") || p;
  g.id = "act-" + (i + 1);
  var pt = q(".pt", p);
  var noun = el("span", "pc-noun", NOUN[i] || "");
  p.insertBefore(noun, pt);
  pt.classList.add("pc-q");
});

/* ── 목차: the four acts, each with the drawn pieces it carries ── */
var view = q(".view");
var KEYS = ".figs-q, .flow-title, .box-head, .tl-title";
var groups = acts.map(function (p, i) {
  var host = p.closest("details.act-fold") || p;
  var stop = acts[i + 1] ? (acts[i + 1].closest("details.act-fold") || acts[i + 1]) : null;
  var rows = [];
  var all = qa(KEYS, view);
  all.forEach(function (k) {
    var inAct = host.tagName === "DETAILS" ? host.contains(k)
      : (host.compareDocumentPosition(k) & 4) && (!stop || (stop.compareDocumentPosition(k) & 2));
    if (inAct) rows.push(k);
  });
  return { p: p, host: host, rows: rows };
});
var n = 0;
var toc = el("aside", "toc pc-toc");
toc.appendChild(el("div", "toc-title", "목차"));
var ms = el("nav", "ms"); ms.setAttribute("aria-label", "목차"); toc.appendChild(ms);
groups.forEach(function (g, i) {
  var box = el("div", "ms-g");
  var a = el("a", "ms-act"); a.href = "#act-" + (i + 1);
  a.appendChild(el("span", "ms-node", String(i + 1)));
  var at = el("span", "ms-at"); at.appendChild(el("b", "", NOUN[i]));
  at.appendChild(el("span", "", q(".pc-q", g.p).firstChild.textContent));
  a.appendChild(at);
  if (g.rows.length) a.appendChild(el("span", "ms-cnt", String(g.rows.length)));
  box.appendChild(a);
  var rows = el("div", "ms-rows");
  g.rows.forEach(function (k) {
    n += 1;
    var id = "pc-k" + n; (k.closest(".figs, .timeline, .matrix") || k).id = id;
    var r = el("div", "toc-row"), s = el("a", "ms-sec"); s.href = "#" + id;
    s.appendChild(el("span", "ms-num", String(n)));
    s.appendChild(el("span", "ms-t", k.textContent.trim()));
    r.appendChild(s); rows.appendChild(r);
  });
  box.appendChild(rows); ms.appendChild(box);
});
var shell = q(".shell");
shell.insertBefore(toc, shell.firstChild);
// opening a folded act from the contents
toc.addEventListener("click", function (e) {
  var a = e.target.closest("a"); if (!a) return;
  var t = d.getElementById(a.getAttribute("href").slice(1));
  var f = t && (t.tagName === "DETAILS" ? t : t.closest("details.act-fold"));
  if (f) f.open = true;
});
// the strip under the nav, where the rail has no room
var strip = el("nav", "actstrip pc-strip"); strip.setAttribute("aria-label", "막");
var sin = el("div", "actstrip-in"); strip.appendChild(sin);
NOUN.slice(0, groups.length).forEach(function (w, i) {
  var a = el("a", "as-link"); a.href = "#act-" + (i + 1);
  var dot = el("i", "as-dot"); a.appendChild(dot); a.appendChild(d.createTextNode(w));
  sin.appendChild(a);
});
shell.parentNode.insertBefore(strip, shell);
// follow the scroll, quietly: the act being read and its piece
function follow() {
  if (H.getAttribute("data-pc-toc") !== "ms") return;
  var y = 140, cur = 0;
  groups.forEach(function (g, i) { if (g.host.getBoundingClientRect().top < y) cur = i; });
  qa(".ms-g", ms).forEach(function (b, i) { b.classList.toggle("on", i === cur); });
  qa(".as-link", sin).forEach(function (a, i) { a.setAttribute("aria-current", i === cur ? "true" : "false"); });
  var secs = qa(".ms-sec", ms), last = null;
  secs.forEach(function (s) { var t = d.getElementById(s.getAttribute("href").slice(1)); if (t && t.getBoundingClientRect().top < y + 60 && t.offsetParent) last = s; });
  secs.forEach(function (s) { s.setAttribute("aria-current", s === last ? "true" : "false"); });
}
addEventListener("scroll", follow, { passive: true });
var tOpen, tShut;
toc.addEventListener("mouseenter", function () { clearTimeout(tShut); tOpen = setTimeout(function () { toc.classList.add("is-open"); }, 200); });
toc.addEventListener("mouseleave", function () { clearTimeout(tOpen); tShut = setTimeout(function () { toc.classList.remove("is-open"); }, 400); });

/* ── 카드: the fork cards and the primers take the summary cards' head ── */
var pHead = q(".cmp-primers-h");

window.pcApply = function (s) {
  ["head", "thesis", "tldr", "toc", "fold", "act", "cards"].forEach(function (k) { H.removeAttribute("data-pc-" + k); });
  H.removeAttribute("data-pc");
  var f = q("details.act-fold");
  if (!s) { shell.classList.add("one"); if (f) f.open = false; return; }
  H.setAttribute("data-pc", "");
  Object.keys(s).forEach(function (k) { H.setAttribute("data-pc-" + k, s[k]); });
  shell.classList.toggle("one", s.toc !== "ms");
  if (f) f.open = s.fold === "open";
  follow();
};
H.setAttribute("data-pc-ready", "");
void pHead;
})();
