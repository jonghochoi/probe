/* 탐색 — the pillar filter, the one switch that opens every row, and the
 * run picker's closing.
 *
 * The page is complete without this: every row is a `<details>` the browser
 * opens on its own, and `scout.css` keeps these controls off an unscripted
 * page. What the script adds is narrowing — show the papers any of the chosen
 * pillars flagged — and opening the whole list at once for a reader who
 * wants to read rather than scan. No choice is remembered: a filter is a
 * question about this run, not a setting.
 */

(function () {
"use strict";

const root = document.querySelector("[data-scout]");
if (!root) return;

const pills = Array.from(root.querySelectorAll("[data-scout-p]"));
const openBtn = root.querySelector("[data-scout-open]");
const shown = root.querySelector("[data-scout-shown]");
const groups = Array.from(root.querySelectorAll("[data-scout-group]"));
const items = Array.from(root.querySelectorAll(".sc-item"));

function apply() {
  const on = pills.filter(b => b.getAttribute("aria-pressed") === "true")
                  .map(b => b.dataset.scoutP);
  let visible = 0;
  for (const item of items) {
    const ps = item.dataset.pillars.split(" ");
    const hit = !on.length || ps.some(p => on.includes(p));
    item.hidden = !hit;
    if (hit) visible += 1;
  }
  for (const g of groups) {
    const n = g.querySelectorAll(".sc-item:not([hidden])").length;
    g.hidden = n === 0;
  }
  shown.textContent = on.length ? `${visible}편 표시` : "";
}

for (const b of pills) {
  b.addEventListener("click", () => {
    b.setAttribute("aria-pressed", b.getAttribute("aria-pressed") === "true" ? "false" : "true");
    apply();
  });
}

openBtn.addEventListener("click", () => {
  const open = openBtn.getAttribute("aria-pressed") !== "true";
  openBtn.setAttribute("aria-pressed", open ? "true" : "false");
  openBtn.textContent = open ? "모두 접기" : "모두 펼치기";
  for (const item of items) item.open = open;
  // Opening everything opens the folded groups too; closing closes the rows
  // and leaves each group as it stands, so the heads stay a table of contents.
  if (open) for (const g of groups) g.open = true;
});

// The run picker is a native `<details>` and opens without this; a reader who
// clicks elsewhere or presses Escape expects it to close, as a menu does.
const pick = root.querySelector("[data-scout-pick]");
if (pick) {
  document.addEventListener("click", e => {
    if (pick.open && !pick.contains(e.target)) pick.open = false;
  });
  document.addEventListener("keydown", e => {
    if (e.key === "Escape" && pick.open) {
      pick.open = false;
      pick.querySelector("summary").focus();
    }
  });
}

// A link to `#p-<id>` lands on that paper open, filter or no filter.
function reveal() {
  const id = decodeURIComponent(location.hash.slice(1));
  const item = id && document.getElementById(id);
  if (item && item.classList.contains("sc-item")) {
    item.hidden = false;
    const group = item.closest("[data-scout-group]");
    group.hidden = false;
    if (group.tagName === "DETAILS") group.open = true;
    item.open = true;
  }
}
window.addEventListener("hashchange", reveal);
reveal();
})();
