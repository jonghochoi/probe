/* Theme toggle. Every page has the nav button, so this is loaded everywhere.
   The initial `data-theme` is already set by the inline boot script in the
   document head — this only handles the click and keeps the icon in sync. */

(function () {
  "use strict";
  var root = document.documentElement;
  var toggle = document.querySelector("[data-theme-toggle]");
  if (!toggle) return;

  function apply(mode) {
    root.setAttribute("data-theme", mode);
    toggle.textContent = mode === "dark" ? "☀" : "☾";
    toggle.setAttribute("aria-label", mode === "dark" ? "라이트 모드로" : "다크 모드로");
  }

  toggle.addEventListener("click", function () {
    var next = root.getAttribute("data-theme") === "dark" ? "light" : "dark";
    try { localStorage.setItem("probe.theme", next); } catch (e) {}
    apply(next);
  });

  apply(root.getAttribute("data-theme") || "light");
})();
