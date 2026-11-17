/* The theme and the reader's colour — the nav card's 화면 and 색 테마 rows,
   and the theme shortcut. Every page has the card, so this is loaded
   everywhere.
   The initial `data-theme` and `data-accent` are already set by the inline
   boot script in the document head; this marks which radio in each row is
   on, answers a pick and the shortcut, and stores the choice. `nav.js` moves
   each row's indicator when its mark changes, so this file never touches
   layout. Midnight is the default colour and is stored as no key at all, and
   a stored key that names no pick on the card falls back to it. */

(function () {
  "use strict";
  var root = document.documentElement;
  var themes = document.querySelectorAll("[data-theme-set]");
  var accents = document.querySelectorAll("[data-accent-pick]");

  // A key with no pick on the card is a colour the site does not draw, so
  // the page wears the default and the key is forgotten.
  var picked = root.getAttribute("data-accent");
  if (picked && !document.querySelector('[data-accent-pick="' + picked + '"]')) setAccent("");

  function mark() {
    var t = root.getAttribute("data-theme") || "light";
    var a = root.getAttribute("data-accent") || "";
    for (var i = 0; i < themes.length; i++)
      themes[i].setAttribute("aria-checked", String(themes[i].getAttribute("data-theme-set") === t));
    for (var j = 0; j < accents.length; j++)
      accents[j].setAttribute("aria-checked", String(accents[j].getAttribute("data-accent-pick") === a));
  }

  function setTheme(mode) {
    try { localStorage.setItem("probe.theme", mode); } catch (e) {}
    root.setAttribute("data-theme", mode);
    mark();
  }

  function setAccent(key) {
    if (key) root.setAttribute("data-accent", key); else root.removeAttribute("data-accent");
    try { if (key) localStorage.setItem("probe.accent", key); else localStorage.removeItem("probe.accent"); } catch (e) {}
    mark();
  }

  document.addEventListener("click", function (e) {
    var t = e.target.closest("[data-theme-set]");
    if (t) { setTheme(t.getAttribute("data-theme-set")); return; }
    var a = e.target.closest("[data-accent-pick]");
    if (a) setAccent(a.getAttribute("data-accent-pick"));
  });

  addEventListener("keydown", function (e) {
    if ((e.metaKey || e.ctrlKey) && e.shiftKey && (e.key === "l" || e.key === "L")) {
      e.preventDefault();
      setTheme(root.getAttribute("data-theme") === "dark" ? "light" : "dark");
    }
  });

  // Which key the 화면 row's tooltip names is the one thing about it the
  // build cannot know — the same reasoning `palette.js` swaps the search
  // shortcut by.
  if (/Mac|iPhone|iPad/.test(navigator.platform || navigator.userAgent)) {
    var tips = document.querySelectorAll('[title*="Ctrl+Shift+L"]');
    for (var k = 0; k < tips.length; k++) tips[k].title = tips[k].title.replace("Ctrl+Shift+L", "⌘⇧L");
  }

  mark();
})();
