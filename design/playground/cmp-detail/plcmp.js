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

/* ── 읽기 전에 as act 0: in the contents, and optionally in the article ── */
var prim = q(".cmp-primers"), primHome = prim && prim.nextSibling;
var prim0 = null, primDiv = null;
if (prim) {
  prim.id = "act-0";
  var cards = qa(".primer", prim);
  prim0 = el("div", "ms-g pc-ms0");
  var a0 = el("a", "ms-act"); a0.href = "#act-0";
  a0.appendChild(el("span", "ms-node", "0"));
  var at0 = el("span", "ms-at"); at0.appendChild(el("b", "", "읽기 전에"));
  at0.appendChild(el("span", "", "먼저 알아 둘 것")); a0.appendChild(at0);
  a0.appendChild(el("span", "ms-cnt", String(cards.length)));
  prim0.appendChild(a0);
  var rows0 = el("div", "ms-rows");
  cards.forEach(function (f, i) {
    f.id = "pc-pr" + (i + 1);
    var r = el("div", "toc-row"), s = el("a", "ms-sec"); s.href = "#" + f.id;
    s.appendChild(el("span", "ms-num", "·"));
    var b = q("figcaption b", f);
    s.appendChild(el("span", "ms-t", b ? b.textContent : ""));
    r.appendChild(s); rows0.appendChild(r);
  });
  prim0.appendChild(rows0);
  ms.insertBefore(prim0, ms.firstChild);
  primDiv = el("div", "pdiv pc-pdiv0");
  primDiv.appendChild(el("span", "pn", "0"));
  primDiv.appendChild(el("span", "pc-noun", "읽기 전에"));
  primDiv.appendChild(el("span", "pt pc-q", "먼저 알아 둘 것"));
}
function placePrimers(mode) {
  if (!prim) return;
  if (mode === "act") {
    var after = q(".view > header.lead");
    var v = q(".view");
    var ref = after ? after.nextSibling : v.firstChild;
    v.insertBefore(primDiv, ref); v.insertBefore(prim, primDiv.nextSibling);
    primDiv.id = "act-0"; prim.removeAttribute("id");
  } else {
    if (primDiv.parentNode) primDiv.parentNode.removeChild(primDiv);
    primHome.parentNode.insertBefore(prim, primHome); prim.id = "act-0";
  }
}
var s0 = el("a", "as-link pc-as0"); s0.href = "#act-0";
s0.appendChild(el("i", "as-dot")); s0.appendChild(d.createTextNode("읽기 전에"));
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
if (prim) sin.insertBefore(s0, sin.firstChild);
// follow the scroll, quietly: the act being read and its piece
function follow() {
  if (H.getAttribute("data-pc-toc") !== "ms") return;
  var y = 140, cur = 0, has0 = prim && H.getAttribute("data-pc-primer") !== "none";
  groups.forEach(function (g, i) { if (g.host.getBoundingClientRect().top < y) cur = i + 1; });
  if (!has0 && cur === 0) cur = 1;
  qa(".ms-g", ms).forEach(function (b) { var k = b.classList.contains("pc-ms0") ? 0 : qa(".ms-g:not(.pc-ms0)", ms).indexOf(b) + 1; b.classList.toggle("on", k === cur); });
  qa(".as-link", sin).forEach(function (a) { var k = a.classList.contains("pc-as0") ? 0 : qa(".as-link:not(.pc-as0)", sin).indexOf(a) + 1; a.setAttribute("aria-current", k === cur ? "true" : "false"); });
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
  ["head", "thesis", "tldr", "toc", "fold", "act", "cards", "primer"].forEach(function (k) { H.removeAttribute("data-pc-" + k); });
  H.removeAttribute("data-pc");
  var f = q("details.act-fold");
  if (!s) { shell.classList.add("one"); if (f) f.open = false; placePrimers("toc"); return; }
  H.setAttribute("data-pc", "");
  Object.keys(s).forEach(function (k) { H.setAttribute("data-pc-" + k, s[k]); });
  shell.classList.toggle("one", s.toc !== "ms");
  if (f) f.open = s.fold === "open";
  placePrimers(s.primer);
  follow();
};
H.setAttribute("data-pc-ready", "");
void pHead;
})();
