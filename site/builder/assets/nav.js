/* The phone's nav menu, and the star count on 서재.
 *
 * One button, one panel under the nav, and the four destinations the row
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

/* How many papers this browser has starred, on 서재 in the row and in the
 * phone's menu — shown only when there is at least one. The count is read
 * straight from the shelf's store (`shelf.js`), because every page has the nav
 * and not every page loads the shelf; it follows a star toggled on this page
 * and one toggled in another tab. */
(function () {
  const slots = document.querySelectorAll("[data-star-count]");
  if (!slots.length) return;
  function paint() {
    let n = 0;
    try {
      const map = JSON.parse(localStorage.getItem("probe.stars.v1") || "{}");
      if (map && typeof map === "object" && !Array.isArray(map)) n = Object.keys(map).length;
    } catch (e) { /* blocked or unreadable storage: no count */ }
    slots.forEach((s) => {
      s.hidden = !n;
      s.textContent = n ? String(n) : "";
      if (n) s.setAttribute("aria-label", `즐겨찾기 ${n}편`); else s.removeAttribute("aria-label");
    });
  }
  document.addEventListener("probe:shelf-change", paint);
  addEventListener("storage", (e) => { if (!e.key || e.key === "probe.stars.v1") paint(); });
  paint();
})();
