/* Landing-page filter, sort and deep-link state.
 *
 * The cards are already in the DOM — this only toggles `hidden` and, for the
 * flat sorts, moves nodes between the pillar groups and a single flat grid.
 * Nothing is fetched and nothing is templated, so the page works from
 * `file://` and degrades to "every paper, grouped by pillar" with JS off.
 *
 * Filter state lives in the URL hash (`#q=<query>&p=P<n>&t=<tag>&s=recent`) so a
 * view can be bookmarked and shared, and `replaceState` keeps it out of the
 * back-button history — Back should leave the page, not undo a keystroke.
 */

(function () {
"use strict";

const root = document.querySelector("[data-corpus]");
const bar = document.querySelector("[data-filters]");
if (!root || !bar) return;

const cards = [...root.querySelectorAll("[data-card]")];
const groups = [...root.querySelectorAll("[data-pgroup]")];
const flat = root.querySelector("[data-flat]");
const emptyMsg = root.querySelector("[data-empty]");
const countEl = bar.querySelector("[data-result-count]");
const input = bar.querySelector("[data-q]");
const sortBtns = [...bar.querySelectorAll("[data-sort]")];
const resetBtns = [...document.querySelectorAll("[data-reset]")];

// Where each card started, so a flat sort can be undone exactly.
const home = new Map(cards.map((el) => [el, el.parentNode]));

const state = { q: "", pillars: new Set(), tags: new Set(), sort: "pillar" };

/* ── State ↔ URL ──────────────────────────────────────────────────────── */
function readHash() {
  const h = new URLSearchParams(location.hash.replace(/^#/, ""));
  state.q = h.get("q") || "";
  state.pillars = new Set((h.get("p") || "").split(",").filter(Boolean));
  state.tags = new Set((h.get("t") || "").split(",").filter(Boolean));
  state.sort = ["pillar", "recent", "title"].includes(h.get("s")) ? h.get("s") : "pillar";
}

function writeHash() {
  const h = new URLSearchParams();
  if (state.q) h.set("q", state.q);
  if (state.pillars.size) h.set("p", [...state.pillars].join(","));
  if (state.tags.size) h.set("t", [...state.tags].join(","));
  if (state.sort !== "pillar") h.set("s", state.sort);
  const hash = h.toString();
  history.replaceState(null, "", hash ? `#${hash}` : location.pathname + location.search);
}

function syncControls() {
  if (input.value !== state.q) input.value = state.q;
  bar.querySelectorAll("[data-facet-pillar]").forEach((b) => {
    b.setAttribute("aria-pressed", state.pillars.has(b.dataset.facetPillar) ? "true" : "false");
  });
  bar.querySelectorAll("[data-facet-tag]").forEach((b) => {
    b.setAttribute("aria-pressed", state.tags.has(b.dataset.facetTag) ? "true" : "false");
  });
  sortBtns.forEach((b) => b.setAttribute("aria-pressed", b.dataset.sort === state.sort ? "true" : "false"));
}

/* ── Matching ─────────────────────────────────────────────────────────── */
function matches(card) {
  if (state.pillars.size) {
    const own = card.dataset.pillars.split(" ");
    // A paper is kept if it touches ANY selected pillar — the pillars are
    // facets of one paper, so intersecting them would return almost nothing.
    if (!own.some((p) => state.pillars.has(p))) return false;
  }
  if (state.tags.size) {
    const own = card.dataset.tags.split(" ");
    if (![...state.tags].every((t) => own.includes(t))) return false;
  }
  if (state.q) {
    const hay = card.dataset.hay;
    // Every whitespace-separated term must appear: typing more narrows.
    if (!state.q.toLowerCase().split(/\s+/).filter(Boolean).every((t) => hay.includes(t))) {
      return false;
    }
  }
  return true;
}

/* ── Apply ────────────────────────────────────────────────────────────── */
function apply() {
  let visible = 0;
  cards.forEach((card) => {
    const ok = matches(card);
    card.hidden = !ok;
    if (ok) visible++;
  });

  if (state.sort === "pillar") {
    cards.forEach((card) => {
      const parent = home.get(card);
      if (card.parentNode !== parent) parent.appendChild(card);
    });
    groups.forEach((g) => {
      const shown = [...g.querySelectorAll("[data-card]")].filter((c) => !c.hidden);
      g.hidden = shown.length === 0;
      const n = g.querySelector("[data-group-count]");
      if (n) n.textContent = shown.length;
    });
    flat.hidden = true;
  } else {
    const key = state.sort === "title" ? "title" : "date";
    const dir = state.sort === "title" ? 1 : -1;
    cards
      .slice()
      .sort((a, b) => dir * a.dataset[key].localeCompare(b.dataset[key]))
      .forEach((card) => flat.appendChild(card));
    groups.forEach((g) => { g.hidden = true; });
    flat.hidden = false;
  }

  countEl.textContent = visible === cards.length ? `${visible}편` : `${visible} / ${cards.length}편`;
  if (emptyMsg) emptyMsg.hidden = visible > 0;
  const dirty = !!(state.q || state.pillars.size || state.tags.size);
  resetBtns.forEach((b) => { b.hidden = !dirty; });
}

function refresh() { syncControls(); apply(); writeHash(); }

/* ── Wiring ───────────────────────────────────────────────────────────── */
let debounce = null;
input.addEventListener("input", () => {
  state.q = input.value;
  if (debounce) clearTimeout(debounce);
  // Filtering 92 nodes is instant; the delay is only so the hash does not get
  // rewritten on every keystroke.
  apply();
  debounce = setTimeout(writeHash, 250);
});

function toggleSet(set, value) {
  if (set.has(value)) set.delete(value); else set.add(value);
}

bar.addEventListener("click", (e) => {
  const p = e.target.closest("[data-facet-pillar]");
  const t = e.target.closest("[data-facet-tag]");
  const s = e.target.closest("[data-sort]");
  if (p) { toggleSet(state.pillars, p.dataset.facetPillar); refresh(); }
  else if (t) { toggleSet(state.tags, t.dataset.facetTag); refresh(); }
  else if (s) { state.sort = s.dataset.sort; refresh(); }
});

// A tag on a card is also a filter — that is how you find the neighbours of
// the paper you are looking at.
root.addEventListener("click", (e) => {
  const chip = e.target.closest("[data-tag-jump]");
  if (!chip) return;
  toggleSet(state.tags, chip.dataset.tagJump);
  refresh();
  bar.scrollIntoView({ block: "nearest", behavior: "smooth" });
});

document.addEventListener("click", (e) => {
  if (!e.target.closest("[data-reset]")) return;
  state.q = ""; state.pillars.clear(); state.tags.clear();
  refresh();
});

addEventListener("hashchange", () => { readHash(); syncControls(); apply(); });

// `/` focuses search, the shortcut every list page has; Escape clears it.
addEventListener("keydown", (e) => {
  if (e.key === "/" && document.activeElement !== input && !e.metaKey && !e.ctrlKey) {
    e.preventDefault(); input.focus(); input.select();
  } else if (e.key === "Escape" && document.activeElement === input) {
    state.q = ""; refresh(); input.blur();
  }
});

readHash();
refresh();
})();
