/* Pillar-page drafts: apply the playground's choices and switch the tabs. */
(function () {
  "use strict";
  var KEY = "probe.pg.pillar.v1";
  var DEF = { head: "tint", desc: "ko", stats: "hide", crumb: "hide", nav: "none", layout: "tabs",
              alist: "table", acount: "5", dec: "choice", dcode: "show", decpos: "last" };
  function state() { var s = {}; try { s = JSON.parse(localStorage.getItem(KEY) || "{}") || {}; } catch (e) {} return s; }
  function apply() {
    var s = state(), root = document.documentElement;
    Object.keys(DEF).forEach(function (k) { root.setAttribute("data-pl-" + k, s[k] || DEF[k]); });
  }
  apply();
  window.plApply = apply;
  var secs = document.querySelectorAll(".pl-sec");
  function show(k) {
    document.querySelectorAll("[data-pl-tab]").forEach(function (b) { b.setAttribute("aria-selected", String(b.getAttribute("data-pl-tab") === k)); });
    secs.forEach(function (s) { s.classList.toggle("is-on", s.getAttribute("data-sec") === k); });
  }
  if (secs.length) show("s");
  document.addEventListener("click", function (e) {
    var b = e.target.closest("[data-pl-tab]");
    if (b) show(b.getAttribute("data-pl-tab"));
  });
})();
