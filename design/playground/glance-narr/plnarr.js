/* 이야기 구분 drafts. Rebuilds the narrative's stanzas into moves; the drafts
   are `data-gn-*` on <html>: split (auto | marked), mark (side | kicker | line),
   limit (box | rule | plain), rhythm (num | lead | none), acts (off | on). */
(function () {
"use strict";
var d = document, H = d.documentElement;
if (H.hasAttribute("data-gn-ready")) return;
// the moves, hand-marked: [first stanza, name, question]
var MARKS = {
  "2607.10655": [[1, "문제"], [4, "방법"], [7, "결과"], [9, "한계"]],
  "2610.16308": [[1, "문제"], [4, "방법"], [5, "결과"], [8, "한계"]],
  "2606.15768": [[1, "문제"], [4, "방법"], [7, "결과"], [9, "한계"]]
};
var COLOUR = { "문제": "var(--act1)", "방법": "var(--act2)", "결과": "var(--act3)", "한계": "var(--text-muted)" };
function el(t, c, x) { var e = d.createElement(t); if (c) e.className = c; if (x != null) e.textContent = x; return e; }
var body = d.querySelector(".g-narr-body");
var acts = d.querySelector(".glance .g-acts");
var pid = (d.querySelector("[data-paper-acts]") || { getAttribute: function () { return ""; } }).getAttribute("data-paper-id");
if (!body) return;
var stanzas = [].slice.call(body.querySelectorAll(":scope > p"));
// the first sentence of each stanza, for the 첫 문장 rhythm
stanzas.forEach(function (p) {
  var w = d.createTreeWalker(p, NodeFilter.SHOW_TEXT), n, done = false, nodes = [];
  while ((n = w.nextNode())) nodes.push(n);
  var lead = el("span", "gn-lead"), first = p.firstChild;
  p.insertBefore(lead, first);
  for (var i = 0; i < nodes.length && !done; i++) {
    var t = nodes[i], m = /[.?!](?=\s)/.exec(t.nodeValue);
    if (m) { var rest = t.splitText(m.index + 1); lead.appendChild(t); done = true; void rest; }
    else lead.appendChild(t.parentNode === p ? t : t.parentNode);
  }
});
var marks = MARKS[pid] || [[1, ""], [stanzas.length, "한계"]];
function rebuild(split) {
  body.innerHTML = "";
  var groups;
  if (split === "marked") groups = marks;
  else groups = [[1, ""], [stanzas.length, "한계"]];
  groups.forEach(function (g, gi) {
    var from = g[0] - 1, to = gi + 1 < groups.length ? groups[gi + 1][0] - 1 : stanzas.length;
    var mv = el("section", "gn-move"); mv.setAttribute("data-m", g[1] || "본문");
    if (g[1]) mv.style.setProperty("--gn-c", COLOUR[g[1]] || "var(--text-muted)");
    if (g[1] && (split === "marked" || g[1] === "한계")) mv.appendChild(el("span", "gn-mark", g[1]));
    var box = el("div", "gn-st");
    stanzas.slice(from, to).forEach(function (p, k) { p.setAttribute("data-i", String(from + k + 1)); box.appendChild(p); });
    mv.appendChild(box); body.appendChild(mv);
  });
}
window.gnApply = function (s) {
  ["data-gn", "data-gn-split", "data-gn-mark", "data-gn-limit", "data-gn-rhythm", "data-gn-acts"].forEach(function (x) { H.removeAttribute(x); });
  if (!s) { body.innerHTML = ""; stanzas.forEach(function (p) { body.appendChild(p); }); return; }
  H.setAttribute("data-gn", "");
  Object.keys(s).forEach(function (k) { H.setAttribute("data-gn-" + k, s[k]); });
  rebuild(s.split);
};
H.setAttribute("data-gn-ready", "");
void acts;
})();
