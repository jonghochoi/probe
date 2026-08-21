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
 * Three of the filters are not the corpus's but the reader's — New, Starred
 * and Unread — and they come off `window.ProbeShelf`, which reads this
 * browser's own localStorage. They behave like any other facet here; the only
 * difference is that their counts are computed rather than printed by the
 * build, and that they disappear when the shelf layer is missing.
 *
 * This page is also the only one that knows the whole corpus, so it is where
 * the 새 글 set is kept honest: it seeds the set on first sight (silently —
 * arriving to be told all 32 papers are new is not news) and prunes ids that
 * have left the site.
 *
 * The list is also paged, which is the same toggling seen from a different
 * angle: the rows outside the current page are `hidden` exactly like the rows
 * a facet dropped. A page is counted in papers rather than rows, so the lead
 * block — which is the first paper, printed rather than listed — is the first
 * paper of the first page, and its own row stands down while it is.
 *
 * Filter state lives in the URL hash (`#q=<query>&p=P<n>&t=<tag>&s=title`) so a
 * view can be bookmarked and shared, and `replaceState` keeps it out of the
 * back-button history — Back should leave the page, not undo a keystroke. The
 * two shelf filters ride there too (`&f=1`, `&u=1`) — a bookmark of "my
 * starred P2 papers" is a view worth keeping — even though what they select is
 * local to the browser that opens the link. So do the page and its size
 * (`&pg=3`, `&sz=5`), which is what makes a link land on the list the sender
 * was looking at.
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
const tabsEl = root.querySelector("[data-restabs]");
const tabBtns = tabsEl ? [...tabsEl.querySelectorAll("[data-restab]")] : [];
const countEl = bar.querySelector("[data-result-count]");
const whenEl = bar.querySelector("[data-corpus-when]");
const input = bar.querySelector("[data-q]");
const sortBtns = [...bar.querySelectorAll("[data-sort]")];
const resetBtns = [...document.querySelectorAll("[data-reset]")];

const pager = root.querySelector("[data-pager]");
const sizeBtns = [...bar.querySelectorAll("[data-size]")];
const pageBtns = pager ? [...pager.querySelectorAll("[data-page]")] : [];
const stepBtns = pager ? [...pager.querySelectorAll("[data-page-rel]")] : [];
const gapLo = pager && pager.querySelector('[data-gap="lo"]');
const gapHi = pager && pager.querySelector('[data-gap="hi"]');
const pageStat = pager && pager.querySelector("[data-page-stat]");

const SORTS = ["recent", "pillar", "title"];
const PILLARS = seps.map((s) => s.dataset.sep);
const shelf = window.ProbeShelf;
const flagBtns = [...document.querySelectorAll("[data-facet-flag]")];

// Which page sizes exist, and which one is the default, are the build's to
// decide (`pages.PAGE_SIZES`) — both are read back off the markup rather than
// restated here, so the bar and the script can never offer different numbers.
// `0` is 전체.
const SIZES = sizeBtns.map((b) => +b.dataset.size);
const SIZE_PRESSED = sizeBtns.find((b) => b.getAttribute("aria-pressed") === "true");
const SIZE_DEFAULT = SIZE_PRESSED ? +SIZE_PRESSED.dataset.size : 0;

/* How much of the list a page holds is the one thing here the reader sets and
 * the corpus has no opinion about. It is a view setting rather than a mark on
 * a paper, so it is not the shelf's to keep — it lives beside it under its own
 * key, and a browser that refuses storage just gets the default every time. */
const VIEW_KEY = "probe.view.v1";

function storedSize() {
  try {
    const v = JSON.parse(localStorage.getItem(VIEW_KEY) || "{}");
    return SIZES.includes(v.size) ? v.size : SIZE_DEFAULT;
  } catch (e) { return SIZE_DEFAULT; }
}

function keepSize(n) {
  try { localStorage.setItem(VIEW_KEY, JSON.stringify({ size: n })); } catch (e) { /* full or blocked */ }
}

const state = {
  q: "", pillars: new Set(), tags: new Set(), sort: "recent",
  fresh: false, star: false, unread: false,
  size: SIZE_DEFAULT, page: 1,
};
const freshNote = root.querySelector("[data-fresh-note]");

/* One question reaches the corpus two ways, and they are two answers rather
 * than one long one: 의미 is what the remote index found by meaning, 글자 is
 * what the matching below found letter for letter. So they are two tabs and
 * one is on screen at a time — reading the better answer should not mean
 * scrolling past the worse one. `semantic.js` says when there is an answer to
 * tab to (`probe:answer`) and how big it is; a build with no endpoint never
 * dispatches it, and then there is one answer and no strip.
 *
 * The list is the second tab, so `pane` is what decides whether this file
 * paints it at all. */
let answered = false;
let pane = "sem";
let semCount = { papers: 0, hits: 0 };

// The block above the list is `semantic.js`'s to show and hide; it is told
// which surface is on rather than reading the strip for itself.
function tellPane() {
  document.dispatchEvent(new CustomEvent("probe:pane", { detail: { pane: pane } }));
}

function setPane(next) {
  if (pane === next) return;
  pane = next;
  tellPane();
  apply();
}

// Without the shelf layer there is nothing to filter on, so the group leaves
// rather than offering two buttons that would select every paper or none.
if (!shelf) {
  flagBtns.forEach((b) => b.remove());
  document.querySelectorAll("[data-mine-h]").forEach((h) => h.remove());
}

/* ── State ↔ URL ──────────────────────────────────────────────────────── */
function readHash() {
  const h = new URLSearchParams(location.hash.replace(/^#/, ""));
  state.q = h.get("q") || "";
  state.pillars = new Set((h.get("p") || "").split(",").filter(Boolean));
  state.tags = new Set((h.get("t") || "").split(",").filter(Boolean));
  state.sort = SORTS.includes(h.get("s")) ? h.get("s") : "recent";
  state.fresh = !!shelf && h.get("n") === "1";
  state.star = !!shelf && h.get("f") === "1";
  state.unread = !!shelf && h.get("u") === "1";
  // A link that names a size means it — otherwise this browser's last choice,
  // and the build's default for a browser that has never made one.
  const sz = parseInt(h.get("sz"), 10);
  state.size = SIZES.includes(sz) ? sz : storedSize();
  state.page = Math.max(1, parseInt(h.get("pg"), 10) || 1);
}

function writeHash() {
  const h = new URLSearchParams();
  if (state.q) h.set("q", state.q);
  if (state.pillars.size) h.set("p", [...state.pillars].join(","));
  if (state.tags.size) h.set("t", [...state.tags].join(","));
  if (state.sort !== "recent") h.set("s", state.sort);
  if (state.fresh) h.set("n", "1");
  if (state.star) h.set("f", "1");
  if (state.unread) h.set("u", "1");
  if (state.size !== SIZE_DEFAULT) h.set("sz", state.size);
  if (state.page > 1) h.set("pg", state.page);
  const hash = h.toString();
  history.replaceState(null, "", hash ? `#${hash}` : location.pathname + location.search);
}

function syncControls() {
  if (input.value !== state.q) {
    input.value = state.q;
    // Setting `.value` fires no `input`, so Escape and 필터 초기화 change the
    // query without anything hearing it. Whatever else reads the box off the
    // page — `semantic.js` — is told here rather than made to watch each
    // control that can empty it.
    document.dispatchEvent(new CustomEvent("probe:query"));
  }
  document.querySelectorAll("[data-facet-pillar]").forEach((b) => {
    b.setAttribute("aria-pressed", state.pillars.has(b.dataset.facetPillar) ? "true" : "false");
  });
  document.querySelectorAll("[data-facet-tag]").forEach((b) => {
    b.setAttribute("aria-pressed", state.tags.has(b.dataset.facetTag) ? "true" : "false");
  });
  flagBtns.forEach((b) => b.setAttribute(
    "aria-pressed", state[b.dataset.facetFlag] ? "true" : "false"));
  sizeBtns.forEach((b) => b.setAttribute(
    "aria-pressed", +b.dataset.size === state.size ? "true" : "false"));
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
  // The reader's three come first: they are the cheapest tests and the ones
  // most likely to cut the pool to a handful.
  if (state.fresh && !shelf.Corpus.isNew(card.dataset.id)) return false;
  if (state.star && !shelf.Stars.has(card.dataset.id)) return false;
  // 아직 안 읽음 is "not finished", not "never opened" — a paper whose 요약 was
  // read is still a paper the reader has not got through.
  if (state.unread && shelf.Reads.isDone(card.dataset.id)) return false;
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
  // `data-order` is the build's own order key — the rank the rewrite landed
  // at, zero-padded so a string compare reproduces it, then the day it was
  // written — and the id breaks a tie the same way the build does: 최신순 has
  // to land on the list the page shipped with, not one row off it.
  const byOrder = (a, b) =>
    b.dataset.order.localeCompare(a.dataset.order) ||
    b.dataset.id.localeCompare(a.dataset.id);
  // A query asks a question, and "newest" is not an answer to it. While one is
  // typed the default sort ranks by how well a paper answers it; the three sort
  // buttons still override, so asking for 최신순 during a search still gets it.
  if (scored) return shown.slice().sort((a, b) => b._score - a._score || byOrder(a, b));
  if (state.sort === "title") {
    return shown.slice().sort((a, b) => a.dataset.title.localeCompare(b.dataset.title));
  }
  if (state.sort !== "pillar") return shown.slice().sort(byOrder);
  // Pillar order comes from the separators, which the build emitted in
  // `PILLAR_ORDER`: the JS never has to know the pillar taxonomy.
  const rank = (el) => {
    const i = PILLARS.indexOf(el.dataset.primary);
    return i === -1 ? PILLARS.length : i;
  };
  return shown.slice().sort((a, b) => rank(a) - rank(b) || byOrder(a, b));
}

/* ── Apply ────────────────────────────────────────────────────────────── */
function apply() {
  const terms = parse(state.q);
  const dirty = !!(state.q || state.pillars.size || state.tags.size
                   || state.fresh || state.star || state.unread);

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

  // On 의미 the list is not on screen at all: the other tab is.
  const listOff = answered && pane === "sem";
  if (freshNote) freshNote.hidden = listOff || !state.fresh;
  const scored = terms.length > 0 && state.sort === "recent";
  const rows = ordered(shown, scored);

  // ── One page of that ─────────────────────────────────────────────────
  // 전체 is the whole list as one page, which is also what an empty result and
  // a browser with no script get. The page is clamped rather than trusted: it
  // arrives from a hash anyone can edit, and a filter can shrink the list under
  // the reader's feet between one click and the next.
  const size = state.size || rows.length || 1;
  const pageCount = Math.max(1, Math.ceil(rows.length / size));
  state.page = Math.min(Math.max(state.page, 1), pageCount);
  const from = (state.page - 1) * size;
  const onPage = new Set(listOff ? [] : rows.slice(from, from + size));

  // The lead block stands in for the newest paper only while it *is* the top
  // of the list. Filter, re-sort or step to page 2 and it stops being that, so
  // it steps aside and its row takes over — the paper is never in both places,
  // and never in neither.
  const leadOn = !!lead && !dirty && state.sort === "recent" && state.page === 1;
  if (lead) lead.hidden = !leadOn;

  cards.forEach((card) => {
    card.hidden = !onPage.has(card) || (leadOn && card.hasAttribute("data-lead-dup"));
  });

  if (state.sort === "pillar") {
    seps.forEach((sep) => {
      const mine = rows.filter((r) => r.dataset.primary === sep.dataset.sep);
      // A separator belongs to the page its pillar has rows on; its count is
      // the pillar's whole share of what the filter left standing, the same
      // number the rail prints beside it, not the handful under it right now.
      sep.hidden = !mine.some((r) => onPage.has(r));
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
  paintTabs(visible);
  paintPager(visible, listOff ? 1 : pageCount, from, size);
  if (partialMsg) partialMsg.hidden = listOff || !partial;
  // An answer is on screen, so "조건에 맞는 논문이 없습니다" is not what the page
  // found — it is what the string match found, and saying it under a list of
  // passages would read as the corpus having nothing.
  if (emptyMsg) emptyMsg.hidden = answered || visible > 0;
  if (listhead) listhead.hidden = onPage.size - (leadOn ? 1 : 0) < 1;
  resetBtns.forEach((b) => { b.hidden = !dirty; });
  // The date describes the corpus, not the subset a filter leaves behind.
  if (whenEl) whenEl.hidden = dirty;
}

/* The strip, and the two counts on it. It stands only where there is a choice
 * to make: no answer is one answer and no strip, and so is an answer the
 * matching below found nothing to sit beside — a tab onto an empty list is a
 * control that leads nowhere. The count is what makes the tab worth pressing,
 * so each one carries its own: 의미 in papers and passages, 글자 in papers. */
function paintTabs(visible) {
  if (!tabsEl) return;
  tabsEl.hidden = !answered || visible < 1;
  if (tabsEl.hidden) return;
  const n = {
    sem: `${semCount.papers}편 · ${semCount.hits}대목`,
    lex: `${visible}편`,
  };
  tabBtns.forEach((b) => {
    b.setAttribute("aria-pressed", b.dataset.restab === pane ? "true" : "false");
    const slot = b.querySelector("[data-restab-n]");
    if (slot) slot.textContent = n[b.dataset.restab] || "";
  });
}

/* ── The page strip ───────────────────────────────────────────────────── */
/* The build printed one button per page the list could ever need — the whole
 * corpus at the smallest size — so this hides the ones this filter does not
 * reach and windows the rest down to `1 … 6 7 8 … 20`. Nothing is relabelled:
 * every button keeps the number it was printed with, and the two `…` are moved
 * or hidden around them.
 */
function paintPager(total, pageCount, from, size) {
  if (!pager) return;
  // Nothing to step through — 전체, a filter down to one page, or an empty
  // result. The strip leaves rather than standing there as a lone dead `1`.
  pager.hidden = pageCount < 2;
  if (pager.hidden) return;
  const cur = state.page;
  pageBtns.forEach((b) => {
    const n = +b.dataset.page;
    const inWindow = n === 1 || n === pageCount || Math.abs(n - cur) <= 1;
    b.hidden = n > pageCount || !inWindow;
    b.setAttribute("aria-current", n === cur ? "page" : "false");
  });
  if (gapLo) gapLo.hidden = cur - 1 <= 2;
  if (gapHi) {
    // Which button is last depends on the filter, so the trailing `…` is moved
    // in front of it rather than parked before the highest page the corpus
    // could ever reach — the same move the pillar separators make.
    const last = pageBtns[pageCount - 1];
    if (last) last.parentNode.insertBefore(gapHi, last);
    gapHi.hidden = cur + 1 >= pageCount - 1;
  }
  stepBtns.forEach((b) => {
    const next = cur + +b.dataset.pageRel;
    b.disabled = next < 1 || next > pageCount;
  });
  if (pageStat) pageStat.textContent = `${from + 1}–${Math.min(from + size, total)} / ${total}편`;
}

const SMOOTH = matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth";

function toPage(n) {
  state.page = n;
  refresh();
  // The new page is drawn above where the reader is standing — they clicked a
  // strip at the foot of the last one — so the list is brought back under the
  // bar rather than leaving them at the bottom of a page they have not read.
  root.scrollIntoView({ block: "start", behavior: SMOOTH });
}

/* The two shelf counts, over the corpus this page is showing — a star on a
 * paper that has since left the site is real but not selectable here, so
 * counting the store rather than the rows would promise rows that do not
 * exist. */
function countFlags() {
  if (!shelf) return;
  let fresh = 0, star = 0, unread = 0;
  cards.forEach((card) => {
    if (shelf.Corpus.isNew(card.dataset.id)) fresh++;
    if (shelf.Stars.has(card.dataset.id)) star++;
    if (!shelf.Reads.isDone(card.dataset.id)) unread++;
  });
  // Every copy: the three facets are printed once for the rail and once for
  // the filter bar, and only one of the two is on screen at any width.
  const set = (key, n) => {
    document.querySelectorAll(`[data-flag-count="${key}"]`)
      .forEach((el) => { el.textContent = n; });
  };
  set("fresh", fresh);
  set("star", star);
  set("unread", unread);
  // `New 0` is not a filter anyone would press, and on most visits that is
  // what it says — so the control is there only while there is something new.
  // It stays while the filter is on, or turning the last one off would take
  // the control away mid-click.
  const show = !(fresh === 0 && !state.fresh);
  document.querySelectorAll('[data-facet-flag="fresh"]')
    .forEach((el) => { el.hidden = !show; });
}

/* Every control that routes through here — a facet, a sort, a page, a page
 * size — is about the list, so using one is a request for the tab the list is
 * on. Typing does not: `apply()` is what a keystroke calls, and the strip
 * stays where the answer left it. */
function refresh() {
  // `apply()` runs at the end of this function either way, so the switch only
  // has to say so — going through `setPane()` would paint the page twice.
  if (answered && pane !== "lex") { pane = "lex"; tellPane(); }
  syncControls(); countFlags(); shelf && shelf.paint(); apply(); writeHash();
}

/* ── Wiring ───────────────────────────────────────────────────────────── */
let debounce = null;
input.addEventListener("input", () => {
  state.q = input.value;
  // Every keystroke asks a new question, and the answer starts at its top.
  state.page = 1;
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
  const flag = e.target.closest("[data-facet-flag]");
  const ack = e.target.closest("[data-fresh-ack]");
  const jump = e.target.closest("[data-tag-jump]");
  const sizeBtn = e.target.closest("[data-size]");
  const pageBtn = e.target.closest("[data-page]");
  const stepBtn = e.target.closest("[data-page-rel]");
  // Every control that changes which papers are in the list sends the reader
  // back to its first page: page 4 of one filter is not page 4 of the next,
  // and landing on an emptied page would read as a broken list.
  if (ack) {
    shelf.Corpus.markAll(cards.map((card) => card.dataset.id));
    state.fresh = false;
    state.page = 1;
    refresh();
  }
  else if (flag) {
    state[flag.dataset.facetFlag] = !state[flag.dataset.facetFlag];
    state.page = 1;
    refresh();
  }
  else if (p) { toggleSet(state.pillars, p.dataset.facetPillar); state.page = 1; refresh(); }
  else if (t) { toggleSet(state.tags, t.dataset.facetTag); state.page = 1; refresh(); }
  else if (s) { state.sort = s.dataset.sort; state.page = 1; refresh(); }
  else if (pageBtn) { toPage(+pageBtn.dataset.page); }
  else if (stepBtn) { toPage(state.page + +stepBtn.dataset.pageRel); }
  // Changing the page size keeps the reader where they are rather than
  // returning them to the top: the paper that was first on screen is still on
  // the page they land on.
  else if (sizeBtn) {
    const first = state.size ? (state.page - 1) * state.size : 0;
    state.size = +sizeBtn.dataset.size;
    state.page = state.size ? Math.floor(first / state.size) + 1 : 1;
    keepSize(state.size);
    refresh();
  }
  // A tag on the lead block is also a filter — that is how you find the
  // neighbours of the paper you are looking at.
  else if (jump) {
    toggleSet(state.tags, jump.dataset.tagJump);
    state.page = 1;
    refresh();
    bar.scrollIntoView({ block: "nearest", behavior: "smooth" });
  } else if (e.target.closest("[data-reset]")) {
    state.q = ""; state.pillars.clear(); state.tags.clear();
    state.fresh = false; state.star = false; state.unread = false;
    state.page = 1;
    refresh();
  }
});

// The remote block found something, or stopped having something to show. Every
// new answer lands on 의미: it answers a new question, and the reader who
// switched away from the last one did not ask about this one.
document.addEventListener("probe:answer", (e) => {
  const d = e.detail || {};
  answered = !!d.answered;
  semCount = { papers: d.papers || 0, hits: d.hits || 0 };
  pane = "sem";
  tellPane();
  apply();
});

tabBtns.forEach((b) => {
  b.addEventListener("click", () => setPane(b.dataset.restab));
});

// A star toggled on a row is a filter input like any other: the counts move,
// and a list that is currently showing 즐겨찾기 has to lose the row that just
// stopped being one.
document.addEventListener("probe:shelf-change", () => { countFlags(); apply(); });

addEventListener("hashchange", () => { readHash(); syncControls(); apply(); });

// `/` focuses search, the shortcut every list page has; Escape clears it.
addEventListener("keydown", (e) => {
  if (e.key === "/" && document.activeElement !== input && !e.metaKey && !e.ctrlKey) {
    e.preventDefault(); input.focus(); input.select();
  } else if (e.key === "Escape" && document.activeElement === input) {
    state.q = ""; state.page = 1; refresh(); input.blur();
  }
});

// Seed or prune before the first paint, so a first visit never flashes a
// badge it is about to withdraw.
if (shelf) shelf.Corpus.sync(cards.map((card) => card.dataset.id));

readHash();
refresh();
})();
