/* Glossary search.
 *
 * The definitions are all server-rendered and all open — this only hides the
 * ones that do not match. Deliberately not `filter.js`: that script owns sort
 * modes, facet rails and a lead block, none of which exist here, and the two
 * pages share a URL grammar (`#q=`) rather than an implementation.
 */

(function () {
"use strict";

const root = document.querySelector("[data-glossary]");
const bar = document.querySelector("[data-filters]");
if (!root || !bar) return;

const cards = [...root.querySelectorAll("[data-term-card]")];
const emptyMsg = root.querySelector("[data-empty]");
const countEl = bar.querySelector("[data-result-count]");
const input = bar.querySelector("[data-q]");

function apply(q) {
  const terms = q.toLowerCase().split(/\s+/).filter(Boolean);
  let visible = 0;
  cards.forEach((card) => {
    const ok = terms.every((t) => card.dataset.hay.includes(t));
    card.hidden = !ok;
    if (ok) visible++;
  });
  countEl.textContent = visible === cards.length ? `${visible}개` : `${visible} / ${cards.length}개`;
  if (emptyMsg) emptyMsg.hidden = visible > 0;
}

function readHash() {
  return new URLSearchParams(location.hash.replace(/^#/, "")).get("q") || "";
}

let debounce = null;
input.addEventListener("input", () => {
  apply(input.value);
  if (debounce) clearTimeout(debounce);
  debounce = setTimeout(() => {
    const q = input.value;
    history.replaceState(null, "", q ? `#q=${encodeURIComponent(q)}` : location.pathname);
  }, 250);
});

addEventListener("keydown", (e) => {
  if (e.key === "/" && document.activeElement !== input && !e.metaKey && !e.ctrlKey) {
    e.preventDefault(); input.focus(); input.select();
  } else if (e.key === "Escape" && document.activeElement === input) {
    input.value = ""; apply(""); input.blur();
  }
});

// A `#t-<id>` link from a paper page must land on the term, not on a search:
// only a `#q=` hash is read as a query.
const initial = readHash();
if (initial) input.value = initial;
apply(initial);
})();
