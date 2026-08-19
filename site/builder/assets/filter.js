/* Landing-page filter, sort and deep-link state.
 *
 * The rows are already in the DOM — this only toggles `hidden` and reorders
 * nodes inside the one list container. Nothing is fetched and nothing is
 * templated, so the page works from `file://` and degrades to "every paper,
 * newest first" with JS off.
 *
 * Matching runs over two compacted haystacks the build put on every row —
 * the paper's identity and everything the rewrite names — so a term the
 * rewrite defines is findable even though the card only prints a summary.
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
const partialMsg = root.querySelector("[data-partial]");
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
  // While a query ranks the list, none of the three is what the rows are in —
  // pressing 최신순 during a relevance sort would be the control lying about
  // the order. Clicking one still takes the list back.
  const ranked = !!state.q.trim() && state.sort === "recent";
  sortBtns.forEach((b) => b.setAttribute(
    "aria-pressed", !ranked && b.dataset.sort === state.sort ? "true" : "false"));
}

/* ── Query normalisation ──────────────────────────────────────────────── */
/* The build compacts both haystacks with one rule (`corpus.compact`): lowercase,
 * then drop everything that is not a letter, a digit, or the `·` that fences one
 * fragment off from the next. The query goes through the same mill — minus the
 * `·`, which is the haystack's barrier and never a reader's word — so "힘 제어"
 * finds text that spells it "힘제어" and the other way round. Korean spacing is
 * not stable enough to match on, and neither is ours.
 */
const DROP = /[^0-9a-z가-힣ㄱ-ㅎㅏ-ㅣ]+/g;
function compact(s) { return s.toLowerCase().normalize("NFC").replace(DROP, ""); }

/* A query is typed as speech — "액션청킹은", "지연을", "그리퍼로" — while the text
 * spells the word bare. Strip one trailing particle and try both forms; longest
 * first, so "으로" never loses to "로". The guard keeps a short word whole: "은" is
 * a particle, "가치" is not.
 */
const PARTICLES = [
  "으로부터", "로부터", "에서는", "에게서", "이라는", "으로는", "까지", "부터",
  "처럼", "보다", "에서", "에게", "한테", "이나", "으로", "라는", "라고", "이란",
  "은", "는", "이", "가", "을", "를", "의", "에", "와", "과", "로", "도", "만", "랑",
].sort((a, b) => b.length - a.length);

function bare(term) {
  for (const p of PARTICLES) {
    if (term.length > p.length + 1 && term.endsWith(p)) return term.slice(0, -p.length);
  }
  return term;
}

function parse(q) {
  return q.split(/\s+/).map(compact).filter(Boolean).map((t) => ({ t, b: bare(t) }));
}

/* ── Matching ─────────────────────────────────────────────────────────── */
/* Where a word lands is itself a signal: `data-key` is the paper's identity
 * (title, tagline, tags, authors, metric, id) and `data-hay` is everything the
 * rewrite names — headings, term panels, figure captions. A title hit and a
 * footnote hit are not the same claim, so they do not score the same.
 */
const KEY_HIT = 3, HAY_HIT = 1;

function facetOk(card) {
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
  return true;
}

function score(card, terms) {
  const key = card.dataset.key || "", hay = card.dataset.hay || "";
  let total = 0, hit = 0;
  for (const { t, b } of terms) {
    const inKey = key.includes(t) || (b !== t && key.includes(b));
    const inHay = inKey || hay.includes(t) || (b !== t && hay.includes(b));
    if (inHay) { hit += 1; total += inKey ? KEY_HIT : HAY_HIT; }
  }
  return { total, hit };
}

/* ── Order ────────────────────────────────────────────────────────────── */
function ordered(shown, scored) {
  const byDate = (a, b) => b.dataset.date.localeCompare(a.dataset.date);
  // A query asks a question, and "newest" is not an answer to it. While one is
  // typed the default sort ranks by how well a paper answers it; the three sort
  // buttons still override, so asking for 최신순 during a search still gets it.
  if (scored) return shown.slice().sort((a, b) => b._score - a._score || byDate(a, b));
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
  const terms = parse(state.q);
  const dirty = !!(state.q || state.pillars.size || state.tags.size);
  // The lead block stands in for the newest paper only while it *is* the top
  // of the list. Filter or re-sort and it stops being that, so it steps aside
  // and its row takes over — the paper is never in both places, and never in
  // neither.
  const leadOn = !!lead && !dirty && state.sort === "recent";
  if (lead) lead.hidden = !leadOn;

  const pool = cards.filter(facetOk);
  let shown = pool, partial = false;
  if (terms.length) {
    pool.forEach((card) => {
      const { total, hit } = score(card, terms);
      card._score = total;
      card._hit = hit;
    });
    // Every term must land — typing more narrows, which is what a reader
    // expects. But a query nobody wrote for is the normal case here: one wrong
    // word ("액션청킹 촉각") should not empty a corpus that answers most of it.
    // So when nothing matches in full, the bar drops to "any term" and the page
    // says so, rather than showing 0편 and letting the reader conclude we have
    // never read anything on the subject.
    shown = pool.filter((card) => card._hit === terms.length);
    if (!shown.length) {
      shown = pool.filter((card) => card._hit > 0);
      partial = shown.length > 0;
    }
  }

  const scored = terms.length > 0 && state.sort === "recent";
  const keep = new Set(shown);
  cards.forEach((card) => {
    card.hidden = !keep.has(card) || (leadOn && card.hasAttribute("data-lead-dup"));
  });

  const rows = ordered(shown, scored);
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
  const count = visible === cards.length ? `${visible}편` : `${visible} / ${cards.length}편`;
  countEl.textContent = scored ? `${count} · 관련도순` : count;
  if (partialMsg) partialMsg.hidden = !partial;
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
