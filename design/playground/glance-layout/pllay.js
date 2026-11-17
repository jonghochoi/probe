/* 요약 layout drafts. Moves the built cards into one frame once; the drafts
   are `data-gl-*` on <html>: right (rail | acts | both), rail (strip | hub),
   look (full | brief), stick (on | off). */
(function () {
"use strict";
var d = document, H = d.documentElement;
if (H.hasAttribute("data-gl-ready")) return;
function el(t, c) { var e = d.createElement(t); if (c) e.className = c; return e; }
var g = d.querySelector(".glance"), hub = g && g.querySelector(".g-hub"),
    narr = g && g.querySelector(".g-narr"), rail = narr && narr.querySelector(".g-rail"),
    acts = g && g.querySelector(".g-acts");
if (!g || !narr || !acts) return;
// the frame: the story on the left, a column on the right
var wrap = el("div", "gl-wrap"), side = el("div", "gl-side");
narr.parentNode.insertBefore(wrap, narr);
wrap.appendChild(narr); wrap.appendChild(side);
var home = { rail: rail, railParent: narr, acts: acts, actsAfter: wrap };
var strip = el("div", "gl-strip");   // the rail laid across, under the story
var hubRail = el("div", "gl-hubrail"); // the rail laid across, under the claim
if (hub) hub.parentNode.insertBefore(hubRail, hub.nextSibling);
narr.appendChild(strip);
// brief cards open on a click
[].forEach.call(acts.querySelectorAll(".g-act"), function (a) {
  a.addEventListener("click", function (e) {
    if (H.getAttribute("data-gl-look") !== "brief" || !H.hasAttribute("data-gl")) return;
    if (e.target.closest("a, button, .tref, .tbox")) return;
    a.classList.toggle("gl-open");
  });
});
window.glApply = function (s) {
  if (!s) {
    ["data-gl", "data-gl-right", "data-gl-rail", "data-gl-look", "data-gl-stick"].forEach(function (x) { H.removeAttribute(x); });
    narr.appendChild(rail); wrap.parentNode.insertBefore(acts, wrap.nextSibling); return;
  }
  H.setAttribute("data-gl", "");
  Object.keys(s).forEach(function (k) { H.setAttribute("data-gl-" + k, s[k]); });
  // the rail: right column, or laid across
  if (s.right === "rail" || s.right === "both") side.appendChild(rail);
  else (s.rail === "hub" ? hubRail : strip).appendChild(rail);
  // the cards: right column, or under the story
  if (s.right === "acts" || s.right === "both") side.appendChild(acts);
  else wrap.parentNode.insertBefore(acts, wrap.nextSibling);
};
H.setAttribute("data-gl-ready", "");
})();
