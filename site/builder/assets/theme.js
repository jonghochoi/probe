/* Theme toggle and the reader's colour. Every page has both nav buttons, so
   this is loaded everywhere.
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

  /* The reader's colour. The boot script in the head already set
     `data-accent` from `probe.accent`; this opens the menu, marks the pick and
     stores a new one. Indigo is the default and is stored as no key at all. */
  var open = document.querySelector("[data-accent-open]");
  var menu = open && open.parentNode.querySelector(".pal-menu");
  if (open && menu) {
    var picks = menu.querySelectorAll("[data-accent-pick]");
    var mark = function () {
      var on = root.getAttribute("data-accent") || "";
      for (var i = 0; i < picks.length; i++)
        picks[i].setAttribute("aria-checked", String(picks[i].getAttribute("data-accent-pick") === on));
    };
    var show = function (on) { menu.hidden = !on; open.setAttribute("aria-expanded", String(on)); };
    mark();
    open.addEventListener("click", function (e) { e.stopPropagation(); show(menu.hidden); });
    menu.addEventListener("click", function (e) {
      var b = e.target.closest("[data-accent-pick]");
      if (!b) return;
      var key = b.getAttribute("data-accent-pick");
      if (key) root.setAttribute("data-accent", key); else root.removeAttribute("data-accent");
      try { if (key) localStorage.setItem("probe.accent", key); else localStorage.removeItem("probe.accent"); } catch (err) {}
      mark();
    });
    document.addEventListener("click", function (e) { if (!menu.hidden && !open.parentNode.contains(e.target)) show(false); });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape" && !menu.hidden) { show(false); open.focus(); } });
  }
})();
