/* Landing-page filter, sort and deep-link state.
 *
 * The rows are already in the DOM — this only toggles `hidden` and reorders
 * nodes inside the one list container. Nothing is fetched and nothing is
 * templated, so the page works from `file://` and degrades to "every paper,
 * newest first" with JS off.
 *
 * Filter state lives in the URL hash (`#q=<query>&p=P<n>&t=<tag>&s=title`) so a
 * view can be bookmarked and shared, and `replaceState` keeps it out of the
 * back-button history — Back should leave the page, not undo a keystroke.
 */

(function () {
"use strict";

const root = document.querySelector("[data-corpus]");
const bar = document.querySelector("[data-filters]");
if (!root || !bar) return;

const list = root.querySelector("[data-rows]");
const cards = [...root.querySelectorAll("[data-card]")];
const seps = [...root.querySelectorAll("[data-sep]")];
const lead = root.querySelector("[data-lead]");
const listhead = root.querySelector("[data-listhead]");
const emptyMsg = root.querySelector("[data-empty]");
const countEl = bar.querySelector("[data-result-count]");
const input = bar.querySelector("[data-q]");
const sortBtns = [...bar.querySelectorAll("[data-sort]")];
const resetBtns = [...document.querySelectorAll("[data-reset]")];

const SORTS = ["recent", "pillar", "title"];
const PILLARS = seps.map((s) => s.dataset.sep);

const state = { q: "", pillars: new Set(), tags: new Set(), sort: "recent" };

/* ── State ↔ URL ──────────────────────────────────────────────────────── */
function readHash() {
  const h = new URLSearchParams(location.hash.replace(/^#/, ""));
  state.q = h.get("q") || "";
  state.pillars = new Set((h.get("p") || "").split(",").filter(Boolean));
  state.tags = new Set((h.get("t") || "").split(",").filter(Boolean));
  state.sort = SORTS.includes(h.get("s")) ? h.get("s") : "recent";
}

function writeHash() {
  const h = new URLSearchParams();
  if (state.q) h.set("q", state.q);
  if (state.pillars.size) h.set("p", [...state.pillars].join(","));
  if (state.tags.size) h.set("t", [...state.tags].join(","));
  if (state.sort !== "recent") h.set("s", state.sort);
  const hash = h.toString();
  history.replaceState(null, "", hash ? `#${hash}` : location.pathname + location.search);
}

function syncControls() {
  if (input.value !== state.q) input.value = state.q;
  document.querySelectorAll("[data-facet-pillar]").forEach((b) => {
    b.setAttribute("aria-pressed", state.pillars.has(b.dataset.facetPillar) ? "true" : "false");
  });
  document.querySelectorAll("[data-facet-tag]").forEach((b) => {
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

/* ── Order ────────────────────────────────────────────────────────────── */
function ordered(shown) {
  const byDate = (a, b) => b.dataset.date.localeCompare(a.dataset.date);
  if (state.sort === "title") {
    return shown.slice().sort((a, b) => a.dataset.title.localeCompare(b.dataset.title));
  }
  if (state.sort !== "pillar") return shown.slice().sort(byDate);
  // Pillar order comes from the separators, which the build emitted in
  // `PILLAR_ORDER`: the JS never has to know the pillar taxonomy.
  const rank = (el) => {
    const i = PILLARS.indexOf(el.dataset.primary);
    return i === -1 ? PILLARS.length : i;
  };
  return shown.slice().sort((a, b) => rank(a) - rank(b) || byDate(a, b));
}

/* ── Apply ────────────────────────────────────────────────────────────── */
function apply() {
  const dirty = !!(state.q || state.pillars.size || state.tags.size);
  // The lead block stands in for the newest paper only while it *is* the top
  // of the list. Filter or re-sort and it stops being that, so it steps aside
  // and its row takes over — the paper is never in both places, and never in
  // neither.
  const leadOn = !!lead && !dirty && state.sort === "recent";
  if (lead) lead.hidden = !leadOn;

  const shown = [];
  cards.forEach((card) => {
    const ok = matches(card);
    if (ok) shown.push(card);
    card.hidden = !ok || (leadOn && card.hasAttribute("data-lead-dup"));
  });

  const rows = ordered(shown);
  if (state.sort === "pillar") {
    seps.forEach((sep) => {
      const mine = rows.filter((r) => r.dataset.primary === sep.dataset.sep);
      sep.hidden = mine.length === 0;
      const n = sep.querySelector("[data-sep-count]");
      if (n) n.textContent = mine.length;
    });
    // Each separator is moved into place by the row loop below, at the moment
    // its pillar first appears — so it lands above its own rows and nowhere
    // else, whatever the filter left standing.
    let current = null;
    rows.forEach((row) => {
      if (row.dataset.primary !== current) {
        current = row.dataset.primary;
        const sep = seps.find((s) => s.dataset.sep === current);
        if (sep) list.appendChild(sep);
      }
      list.appendChild(row);
    });
  } else {
    seps.forEach((sep) => { sep.hidden = true; });
    rows.forEach((row) => list.appendChild(row));
  }
  // Rows filtered out keep their DOM position; only the visible ones are
  // reordered, which is enough because nothing hidden is ever painted.

  const visible = shown.length;
  countEl.textContent = visible === cards.length ? `${visible}편` : `${visible} / ${cards.length}편`;
  if (emptyMsg) emptyMsg.hidden = visible > 0;
  if (listhead) listhead.hidden = visible - (leadOn ? 1 : 0) < 1;
  resetBtns.forEach((b) => { b.hidden = !dirty; });
}

function refresh() { syncControls(); apply(); writeHash(); }

/* ── Wiring ───────────────────────────────────────────────────────────── */
let debounce = null;
input.addEventListener("input", () => {
  state.q = input.value;
  if (debounce) clearTimeout(debounce);
  // Filtering is instant; the delay is only so the hash does not get
  // rewritten on every keystroke.
  apply();
  debounce = setTimeout(writeHash, 250);
});

function toggleSet(set, value) {
  if (set.has(value)) set.delete(value); else set.add(value);
}

// One handler for the sort group in the bar and the facet rail beside the
// list — they set the same state and differ only in where they sit.
document.addEventListener("click", (e) => {
  const p = e.target.closest("[data-facet-pillar]");
  const t = e.target.closest("[data-facet-tag]");
  const s = e.target.closest("[data-sort]");
  const jump = e.target.closest("[data-tag-jump]");
  if (p) { toggleSet(state.pillars, p.dataset.facetPillar); refresh(); }
  else if (t) { toggleSet(state.tags, t.dataset.facetTag); refresh(); }
  else if (s) { state.sort = s.dataset.sort; refresh(); }
  // A tag on the lead block is also a filter — that is how you find the
  // neighbours of the paper you are looking at.
  else if (jump) {
    toggleSet(state.tags, jump.dataset.tagJump);
    refresh();
    bar.scrollIntoView({ block: "nearest", behavior: "smooth" });
  } else if (e.target.closest("[data-reset]")) {
    state.q = ""; state.pillars.clear(); state.tags.clear();
    refresh();
  }
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
