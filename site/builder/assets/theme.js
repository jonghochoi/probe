/* The reader's ground, accent and contrast — the nav card's 바탕 and 강조 rows,
   its 고대비 switch, and the theme shortcut. Every page has the card, so this
   is loaded everywhere.
   The initial `data-theme`, `data-ground`, `data-contrast` and `data-accent`
   are already set by the inline boot script in the document head; this marks
   which pick in each row is on, answers a pick, the switch and the shortcut,
   and stores the choice. A ground is stored as its key (`probe.theme`:
   light, paper, dark, dim) and worn as `data-theme` light or dark plus
   `data-ground` for 종이 and 딤, so every dark rule in the sheets holds for 딤
   too. `nav.js` moves each row's indicator when its mark changes, so this
   file never touches layout. 인디고 is the default accent and is stored as no
   key at all, and a stored key that names no pick on the card falls back to
   it. */

(function () {
  "use strict";
  var root = document.documentElement;
  var themes = document.querySelectorAll("[data-theme-set]");
  var accents = document.querySelectorAll("[data-accent-pick]");
  var contrast = document.querySelector("[data-contrast-toggle]");
  var DARK = { dark: 1, dim: 1 };

  // A key with no pick on the card is a colour the site does not draw, so
  // the page wears the default and the key is forgotten.
  var picked = root.getAttribute("data-accent");
  if (picked && !document.querySelector('[data-accent-pick="' + picked + '"]')) setAccent("");

  function ground() {
    return root.getAttribute("data-ground") || root.getAttribute("data-theme") || "light";
  }

  function mark() {
    var t = ground();
    var a = root.getAttribute("data-accent") || "";
    for (var i = 0; i < themes.length; i++)
      themes[i].setAttribute("aria-checked", String(themes[i].getAttribute("data-theme-set") === t));
    for (var j = 0; j < accents.length; j++)
      accents[j].setAttribute("aria-checked", String(accents[j].getAttribute("data-accent-pick") === a));
    if (contrast) contrast.setAttribute("aria-checked", String(root.getAttribute("data-contrast") === "high"));
  }

  // Every token changes at once, so every transition that names a colour
  // would start at once too and finish a beat after the page. The class
  // (`site.css`) holds them off for the frame the change lands in.
  function still() {
    root.classList.add("theme-switching");
    requestAnimationFrame(function () {
      requestAnimationFrame(function () { root.classList.remove("theme-switching"); });
    });
  }

  function setTheme(key) {
    try { localStorage.setItem("probe.theme", key); } catch (e) {}
    still();
    root.setAttribute("data-theme", DARK[key] ? "dark" : "light");
    if (key === "paper" || key === "dim") root.setAttribute("data-ground", key);
    else root.removeAttribute("data-ground");
    mark();
  }

  function setContrast(on) {
    try { if (on) localStorage.setItem("probe.contrast", "high"); else localStorage.removeItem("probe.contrast"); } catch (e) {}
    still();
    if (on) root.setAttribute("data-contrast", "high"); else root.removeAttribute("data-contrast");
    mark();
  }

  function setAccent(key) {
    still();
    if (key) root.setAttribute("data-accent", key); else root.removeAttribute("data-accent");
    try { if (key) localStorage.setItem("probe.accent", key); else localStorage.removeItem("probe.accent"); } catch (e) {}
    mark();
  }

  document.addEventListener("click", function (e) {
    var t = e.target.closest("[data-theme-set]");
    if (t) { setTheme(t.getAttribute("data-theme-set")); return; }
    var a = e.target.closest("[data-accent-pick]");
    if (a) { setAccent(a.getAttribute("data-accent-pick")); return; }
    if (e.target.closest("[data-contrast-toggle]")) setContrast(root.getAttribute("data-contrast") !== "high");
  });

  addEventListener("keydown", function (e) {
    if ((e.metaKey || e.ctrlKey) && e.shiftKey && (e.key === "l" || e.key === "L")) {
      e.preventDefault();
      // Between the two families: any dark ground goes to 라이트, any light
      // one to 다크.
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
