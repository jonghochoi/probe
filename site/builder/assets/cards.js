/* The axis line over a card list (비교): one axis at a time keeps the cards
 * filed under it, and pressing the axis that is on lets every card back.
 *
 * With no script the line leaves (`index.css` shows `.pline` only under
 * `html.js`) and every card stands, which is the whole list. No choice is
 * remembered: an axis is a question about this list, not a setting.
 */
(function () {
"use strict";

const bar = document.querySelector("[data-filters]");
const list = document.querySelector("[data-cards]");
if (!bar || !list) return;
const cards = [...list.children];
const count = bar.querySelector("[data-result-count]");
const empty = document.querySelector("[data-empty]");
let on = "";

function apply() {
  let n = 0;
  cards.forEach((card) => {
    const keep = !on || card.dataset.pillars.split(" ").includes(on);
    card.hidden = !keep;
    if (keep) n++;
  });
  bar.querySelectorAll("[data-facet-pillar]").forEach((b) => {
    b.setAttribute("aria-pressed", String(b.dataset.facetPillar === on));
  });
  if (count) count.textContent = `${n}편`;
  if (empty) empty.hidden = n > 0;
  // A filtered row of two is two wide, not two thirds of three.
  list.style.setProperty("--cols", String(Math.max(1, Math.ceil(n / Math.ceil(n / 3 || 1)))));
}

bar.addEventListener("click", (e) => {
  const b = e.target.closest("[data-facet-pillar]");
  if (!b) return;
  on = on === b.dataset.facetPillar ? "" : b.dataset.facetPillar;
  apply();
});

/* On a phone the line scrolls sideways; its fade says so until the end is in
 * view. */
const items = bar.querySelector("[data-pline]");
if (items) {
  const edge = () => bar.classList.toggle("at-end",
    items.scrollLeft + items.clientWidth >= items.scrollWidth - 4);
  items.addEventListener("scroll", edge, { passive: true });
  addEventListener("resize", edge);
  edge();
}
})();
