/* The phone's nav menu.
 *
 * One button, one panel under the nav, and the three destinations the row
 * hands over below 640px so the site's name can stay on the line. The panel
 * is markup the build printed — the script only opens and closes it, so a
 * browser that never runs this file still has every link, in the row.
 *
 * It closes on Escape, on a click outside it, on following one of its own
 * links, and the moment the viewport is wide enough for the row to carry the
 * destinations again: a panel left open behind a nav that no longer has a
 * button to close it is a panel nothing can dismiss.
 */
(function () {
  const btn = document.querySelector("[data-nav-menu]");
  const sheet = document.getElementById("nav-sheet");
  if (!btn || !sheet) return;

  const wide = matchMedia("(min-width: 641px)");

  function open(on) {
    if (on === !sheet.hidden) return;
    sheet.hidden = !on;
    btn.setAttribute("aria-expanded", String(on));
    btn.setAttribute("aria-label", on ? "메뉴 닫기" : "메뉴 열기");
    if (on) sheet.querySelector("a").focus();
  }

  btn.addEventListener("click", () => open(sheet.hidden));

  // A link inside the panel navigates, which is a close of its own — except
  // the one that leaves for a new tab, where the page under it stays put.
  sheet.addEventListener("click", (e) => {
    if (e.target.closest("a")) open(false);
  });

  document.addEventListener("click", (e) => {
    if (!sheet.hidden && !e.target.closest("#nav-sheet, [data-nav-menu]")) open(false);
  });

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && !sheet.hidden) {
      open(false);
      btn.focus();
    }
  });

  wide.addEventListener("change", (e) => { if (e.matches) open(false); });
})();
