/* Theme toggle. Every page has the nav button, so this is loaded everywhere.
   The initial `data-theme` is already set by the inline boot script in the
   document head — this only handles the click, the shortcut, and keeps the
   tooltip in sync. Which of the button's two icons is on screen is
   `site.css`'s answer to `data-theme`, so the swap needs no script and a
   theme set before this file arrives is already drawn correctly. */

(function () {
  "use strict";
  var root = document.documentElement;
  var toggle = document.querySelector("[data-theme-toggle]");
  if (!toggle) return;

  // Which key the tooltip names is the one thing about this button the build
  // cannot know — the same reasoning `palette.js` swaps the search shortcut
  // by, for the same reason.
  var isMac = /Mac|iPhone|iPad/.test(navigator.platform || navigator.userAgent);
  var key = isMac ? "⌘⇧L" : "Ctrl+Shift+L";

  function apply(mode) {
    root.setAttribute("data-theme", mode);
    var label = (mode === "dark" ? "라이트 모드로" : "다크 모드로") + " (" + key + ")";
    toggle.setAttribute("aria-label", label);
    toggle.title = label;
  }

  function flip() {
    var next = root.getAttribute("data-theme") === "dark" ? "light" : "dark";
    try { localStorage.setItem("probe.theme", next); } catch (e) {}
    apply(next);
  }

  toggle.addEventListener("click", flip);

  addEventListener("keydown", function (e) {
    if ((e.metaKey || e.ctrlKey) && e.shiftKey && (e.key === "l" || e.key === "L")) {
      e.preventDefault();
      flip();
    }
  });

  apply(root.getAttribute("data-theme") || "light");
})();
