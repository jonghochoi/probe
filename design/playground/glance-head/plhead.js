/* 요약 card-head drafts. Adds the markup every draft needs once; the drafts
   are `data-gh` (head style), `data-gm` (card ground) and `data-gc` (act
   colour) on <html>, set by the panel. */
(function () {
"use strict";
var d = document;
if (d.documentElement.hasAttribute("data-gh-ready")) return;
function el(t, c, x) { var e = d.createElement(t); if (c) e.className = c; if (x != null) e.textContent = x; return e; }
function pair(cls, noun, sub) { var h = el("div", cls); h.appendChild(el("b", "", noun)); if (sub) h.appendChild(el("span", "", sub)); return h; }
var NAMES = { "1": ["문제", "무엇이 막혔나"], "2": ["방법", "무엇을 바꿨나"], "3": ["검증", "정말 되는가"], "4": ["시사점", "연구 축에 걸리는 것"] };
var hub = d.querySelector(".g-hub"), narr = d.querySelector(".g-narr"), acts = d.querySelector(".g-acts");
// a head inside each card: the short noun and its grey line
// the claim card is two columns; its head runs across both
if (hub) { hub.insertBefore(pair("pg-head", "주장", "이 논문이 말하는 것"), hub.firstChild); }
if (narr) { var nh = narr.querySelector(".g-narr-h"); nh.appendChild(pair("pg-head", "이야기", "한 번에 읽기")); }
[].forEach.call(d.querySelectorAll(".g-act"), function (a) {
  var n = a.getAttribute("data-n"), nm = NAMES[n] || ["", ""];
  var h = pair("pg-head", nm[0], nm[1]);
  h.insertBefore(el("i", "pg-num", n), h.firstChild);
  a.insertBefore(h, a.firstChild);
});
// group titles above the cards, as on the first screen
function sec(before, noun, sub) { if (before) before.parentNode.insertBefore(pair("pg-sec", noun, sub), before); }
sec(hub, "주장", "이 논문이 말하는 것");
sec(narr, "이야기", "한 번에 읽기 · 조건");
sec(acts, "근거", "막마다 하나");
d.documentElement.setAttribute("data-gh-ready", "");
})();
