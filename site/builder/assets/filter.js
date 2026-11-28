/* The analysis list's behaviour: the filter, the pager and the deep-link
 * state; a row's figure on a resting pointer; and 빈자리's folded name line
 * (its own block at the end).
 *
 * The rows are already in the DOM — this only toggles `hidden` and reorders
 * nodes inside the one list container. Nothing is fetched and nothing is
 * templated, so the page works from `file://` and degrades to "every paper,
 * newest first" with JS off.
 *
 * Matching runs over two compacted haystacks the build put on every row —
 * the paper's identity and everything the rewrite names — so a term the
 * rewrite defines is findable even though the card only prints a summary. How
 * a query is read before it meets them is `match.js`, which the ⌘K palette
 * reads the same query with.
 *
 * This page is also the only one that knows the whole corpus, so it is where
 * the 새 글 set (`window.ProbeShelf`, the dot before a row's date) is kept
 * honest: it seeds the set on first sight (silently — arriving to be told
 * every paper is new is not news) and prunes ids that have left the site.
 *
 * The list is also paged, which is the same toggling seen from a different
 * angle: the rows outside the current page are `hidden` exactly like the rows
 * a facet dropped.
 *
 * Only one 연구 축 is on at a time: an axis is where a paper is filed, so
 * two of them at once is not a narrower question but a vaguer one, and the
 * union it returns reads as no filter at all. Pressing the axis that is
 * already on turns it off.
 *
 * A change of filter is played rather than swapped (see "What a filter did"):
 * the rows on screen slide to where the new order puts them, and the count
 * rolls over. A query the address carries stands in the axis line as a token
 * whose × drops it.
 *
 * Filter state lives in the URL hash (`#q=<query>&p=P<n>`) so a view can be
 * bookmarked and shared, and `replaceState` keeps it out of the back-button
 * history — Back should leave the page, not undo a keystroke. So do the page
 * and its size (`&pg=3`, `&sz=20`), which is what makes a link land on the
 * list the sender was looking at. The list has no search box — a word search
 * is ⌘K's — so a query reaches it only through the address.
 */

(function () {
"use strict";

const root = document.querySelector("[data-corpus]");
const bar = document.querySelector("[data-filters]");
if (!root || !bar) return;

const list = root.querySelector("[data-rows]");
const cards = [...root.querySelectorAll("[data-card]")];
const listhead = root.querySelector("[data-listhead]");
const emptyMsg = root.querySelector("[data-empty]");
const partialMsg = root.querySelector("[data-partial]");
// The two readouts close the axis line: what the filter leaves behind is a
// fact about the list, said where the list is filtered from.
const countEl = document.querySelector("[data-result-count]");
const whenEl = document.querySelector("[data-corpus-when]");
// The analysis list has no search box — a word search is ⌘K's — so a query arrives
// only through the address (`#q=`), and the box is read when a page has one.
const input = document.querySelector("[data-q]");
const resetBtns = [...document.querySelectorAll("[data-reset]")];
const plineItems = document.querySelector("[data-pline]");
const statEl = countEl && countEl.parentNode;

/* The query an address carries filters the list as much as an axis does, so it
 * is said where the axes are: the first item of the axis line, with the × that
 * drops it. The build prints nothing for it — with no script there is no query
 * to show — so the script makes the one button it needs. */
const qtok = document.createElement("button");
qtok.type = "button"; qtok.className = "rail-item pline-q"; qtok.hidden = true;
qtok.setAttribute("data-q-clear", "");
qtok.innerHTML = '<b></b><span class="pline-x" aria-hidden="true">×</span>';
if (plineItems) plineItems.prepend(qtok);

const pager = root.querySelector("[data-pager]");
const sizeBtns = [...document.querySelectorAll("[data-size]")];
const sizeLabel = document.querySelector("[data-psize-label]");
const sizeMenu = document.querySelector(".psize-menu");
const sizeOpen = document.querySelector("[data-psize-open]");
const pageBtns = pager ? [...pager.querySelectorAll("[data-page]")] : [];
const stepBtns = pager ? [...pager.querySelectorAll("[data-page-rel]")] : [];
const gapLo = pager && pager.querySelector('[data-gap="lo"]');
const gapHi = pager && pager.querySelector('[data-gap="hi"]');

const shelf = window.ProbeShelf;

// Which page sizes exist, and which one is the default, are the build's to
// decide (`pages.PAGE_SIZES`) — both are read back off the markup rather than
// restated here, so the menu and the script can never offer different numbers.
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

const state = { q: "", pillar: "", size: SIZE_DEFAULT, page: 1 };

/* ── State ↔ URL ──────────────────────────────────────────────────────── */
function readHash() {
  const h = new URLSearchParams(location.hash.replace(/^#/, ""));
  // `t=` in a link names words to narrow by. The list has one text filter, so
  // they join the query — `#t=tactile,flow-matching` lands as the search
  // `tactile flow-matching` — and the first repaint writes the hash back
  // without them.
  const words = (h.get("t") || "").split(",").filter(Boolean);
  state.q = [h.get("q") || "", ...words].filter(Boolean).join(" ");
  // One axis, and a link that names several is read for the first of them.
  state.pillar = (h.get("p") || "").split(",").filter(Boolean)[0] || "";
  // A link that names a size means it — otherwise this browser's last choice,
  // and the build's default for a browser that has never made one.
  const sz = parseInt(h.get("sz"), 10);
  state.size = SIZES.includes(sz) ? sz : storedSize();
  state.page = Math.max(1, parseInt(h.get("pg"), 10) || 1);
}

function writeHash() {
  const h = new URLSearchParams();
  if (state.q) h.set("q", state.q);
  if (state.pillar) h.set("p", state.pillar);
  if (state.size !== SIZE_DEFAULT) h.set("sz", state.size);
  if (state.page > 1) h.set("pg", state.page);
  const hash = h.toString();
  history.replaceState(null, "", hash ? `#${hash}` : location.pathname + location.search);
}

function syncControls() {
  if (input && input.value !== state.q) input.value = state.q;
  document.querySelectorAll("[data-facet-pillar]").forEach((b) => {
    const pressed = b.dataset.facetPillar === state.pillar ? "true" : "false";
    if (b.getAttribute("aria-pressed") === pressed) return;
    // The fill changes in the same frame as the label (index.css `is-snap`).
    b.classList.add("is-snap");
    b.setAttribute("aria-pressed", pressed);
    requestAnimationFrame(() => requestAnimationFrame(() => b.classList.remove("is-snap")));
  });
  sizeBtns.forEach((b) => b.setAttribute(
    "aria-pressed", +b.dataset.size === state.size ? "true" : "false"));
  if (sizeLabel) sizeLabel.textContent = String(state.size);
  qtok.hidden = !state.q;
  qtok.querySelector("b").textContent = `‘${state.q}’`;
  qtok.title = state.q;
  qtok.setAttribute("aria-label", `검색어 ‘${state.q}’ 지우기`);
}

/* ── Query normalisation ──────────────────────────────────────────────── */
/* The compaction and the particle strip are `match.js` — the palette asks the
 * same question of the same corpus, and one rule is what keeps the two
 * surfaces from answering it differently.
 */
const { parse, inFragment } = window.ProbeMatch;

/* ── Matching ─────────────────────────────────────────────────────────── */
/* Where a word lands is itself a signal: `data-key` is the paper's identity
 * (title, tagline, authors, metric, id, axes) and `data-hay` is everything the
 * rewrite names — headings, term panels, figure captions. A title hit and a
 * footnote hit are not the same claim, so they do not score the same.
 */
const KEY_HIT = 3, HAY_HIT = 1;

function facetOk(card) {
  // `data-pillars` is `Paper.filed` — the two axes the row's own chips print
  // and the axis line counted — so the list a click opens is as long as the number
  // that was clicked.
  if (state.pillar && !card.dataset.pillars.split(" ").includes(state.pillar)) return false;
  return true;
}

function score(card, terms) {
  const key = card.dataset.key || "", hay = card.dataset.hay || "";
  let total = 0, hit = 0;
  for (const term of terms) {
    const inKey = inFragment(key, term);
    if (inKey || inFragment(hay, term)) { hit += 1; total += inKey ? KEY_HIT : HAY_HIT; }
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
  // A query asks a question, and "newest" is not an answer to it: while one
  // stands, the list ranks by how well a paper answers it.
  if (scored) return shown.slice().sort((a, b) => b._score - a._score || byOrder(a, b));
  return shown.slice().sort(byOrder);
}

/* ── Apply ────────────────────────────────────────────────────────────── */
function apply() {
  const terms = parse(state.q);
  const dirty = !!(state.q || state.pillar);

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

  const scored = terms.length > 0;
  const rows = ordered(shown, scored);

  // ── One page of that ─────────────────────────────────────────────────
  // The page is clamped rather than trusted: it
  // arrives from a hash anyone can edit, and a filter can shrink the list under
  // the reader's feet between one click and the next.
  const size = state.size || rows.length || 1;
  const pageCount = Math.max(1, Math.ceil(rows.length / size));
  state.page = Math.min(Math.max(state.page, 1), pageCount);
  const from = (state.page - 1) * size;
  const onPage = new Set(rows.slice(from, from + size));

  cards.forEach((card) => {
    card.hidden = !onPage.has(card);
  });

  rows.forEach((row) => list.appendChild(row));
  // Rows filtered out keep their DOM position; only the visible ones are
  // reordered, which is enough because nothing hidden is ever painted.

  const visible = shown.length;
  const count = visible === cards.length ? `${visible}편` : `${visible} / ${cards.length}편`;
  countEl.textContent = scored ? `${count} · 관련도순` : count;
  paintPager(visible, pageCount, from, size);
  if (partialMsg) partialMsg.hidden = !partial;
  if (emptyMsg) emptyMsg.hidden = visible > 0;
  if (listhead) listhead.hidden = onPage.size < 1;
  resetBtns.forEach((b) => { b.hidden = !dirty; });
  // The date describes the corpus, not the subset a filter leaves behind.
  if (whenEl) whenEl.hidden = dirty;
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
  // Nothing to step through — a filter down to one page, or an empty
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
    // could ever reach.
    const last = pageBtns[pageCount - 1];
    if (last) last.parentNode.insertBefore(gapHi, last);
    gapHi.hidden = cur + 1 >= pageCount - 1;
  }
  stepBtns.forEach((b) => {
    const next = cur + +b.dataset.pageRel;
    b.disabled = next < 1 || next > pageCount;
  });
}

/* ── What a filter did ────────────────────────────────────────────────── */
/* A filter re-sorts the list in one frame, and a list that is simply different
 * reads as a page that reloaded rather than an answer to the click. So around
 * a change the rows on screen are measured, the change is applied, and each is
 * played from where it stood: a row that stays slides to its new place, one
 * that leaves fades where it was, one that arrives rises into its slot, and the
 * count at the line's end rolls over to the new number with a moment of the
 * accent. Leaving is quicker than arriving — what goes is already understood.
 *
 * Only what was or is on screen plays: a row below the fold has no place the
 * reader saw. Paging and the page size are not filter changes — the whole page
 * is replaced, and paging scrolls to it — so those swap. Every timing is a
 * token from `site.css`, read back here so the two cannot drift.
 *
 * Reduced motion keeps the news and drops the travel: nothing slides, arrivals
 * and the count fade in quickly, the count still takes the accent, and the
 * query token still comes and goes. A browser without `el.animate` swaps. */
const still = matchMedia("(prefers-reduced-motion: reduce)");
const canPlay = typeof Element.prototype.animate === "function";
const tok = getComputedStyle(document.documentElement);
const ms = (name, fallback) => parseFloat(tok.getPropertyValue(name)) || fallback;
const EASE = tok.getPropertyValue("--ease-out").trim() || "cubic-bezier(.16,1,.3,1)";
const T_MOVE = ms("--dur-long", 280), T_IN = ms("--dur-mid", 200), T_OUT = ms("--dur-micro", 120);
// Arrivals wait until what leaves is half gone from their slot, then follow
// one another down the list — but the last starts no more than a beat after
// the first: a longer stagger is a wait.
const STEP = 24, STAGGER_CAP = 96;

let playing = [], ghosts = [];

function play(el, frames, opts) {
  const a = el.animate(frames, Object.assign({ easing: EASE }, opts));
  playing.push(a);
  return a;
}

/* What left is gone from the layout the moment the change lands, so it fades
 * as a stand-in: a copy that holds nothing a script or a reader can reach,
 * laid over the spot the original held. */
function ghost(copy, rect, host) {
  const box = host.getBoundingClientRect();
  copy.removeAttribute("id"); copy.hidden = false;
  [copy, ...copy.querySelectorAll("*")].forEach((el) => {
    [...el.attributes].forEach((at) => { if (at.name.startsWith("data-")) el.removeAttribute(at.name); });
  });
  copy.classList.add("is-leaving");
  copy.setAttribute("aria-hidden", "true");
  copy.inert = true;
  Object.assign(copy.style, {
    left: `${rect.left - box.left}px`, top: `${rect.top - box.top}px`,
    width: `${rect.width}px`, height: `${rect.height}px`,
  });
  host.appendChild(copy);
  ghosts.push(copy);
  return copy;
}

function played(change) {
  if (!canPlay) { change(); return; }
  const reduce = still.matches;
  const vh = innerHeight;
  const seen = (r) => r.height > 0 && r.bottom > 0 && r.top < vh;

  // Before: measured mid-flight if a previous change is still playing, so a
  // second click carries each row on from where it is, not from where it was
  // headed.
  const was = new Map();
  cards.forEach((card) => {
    if (card.hidden) return;
    const r = card.getBoundingClientRect();
    if (seen(r)) was.set(card, r);
  });
  const statWas = statEl && { text: statEl.textContent, when: whenEl && whenEl.hidden,
                              rect: statEl.getBoundingClientRect(), copy: statEl.cloneNode(true) };
  const tokWas = !qtok.hidden && { rect: qtok.getBoundingClientRect(), copy: qtok.cloneNode(true) };
  // What stands under the list — the pager, 빈자리 — rides on its length, so
  // it travels with the rows instead of jumping to where a shorter list ends.
  const below = [];
  for (let el = list.nextElementSibling; el; el = el.nextElementSibling) below.push(el);
  const belowWas = below.map((el) => el.getBoundingClientRect().top);
  const pills = plineItems ? [...plineItems.children].filter((el) => el !== qtok) : [];
  const pillsWas = pills.map((el) => el.getBoundingClientRect().left);

  playing.forEach((a) => a.cancel()); playing = [];
  ghosts.forEach((g) => g.remove()); ghosts = [];

  change();

  // The rows, in the order they now stand.
  let arriving = 0;
  [...list.children].forEach((card) => {
    if (card.hidden || !card.hasAttribute("data-card")) return;
    const r = card.getBoundingClientRect();
    const from = was.get(card);
    if (from) {
      was.delete(card);
      const dy = from.top - r.top;
      if (!reduce && Math.abs(dy) > 1) {
        play(card, [{ transform: `translateY(${dy}px)` }, { transform: "none" }], { duration: T_MOVE });
      }
    } else if (seen(r)) {
      // Without the leavers' fade there is nothing to cover, so the arrivals
      // start part-way in rather than leave the list blank for a frame.
      if (reduce) play(card, [{ opacity: .4 }, { opacity: 1 }], { duration: T_OUT });
      else play(card, [{ opacity: 0, transform: "translateY(6px)" }, { opacity: 1, transform: "none" }],
                { duration: T_IN, delay: T_OUT / 2 + Math.min(arriving++ * STEP, STAGGER_CAP), fill: "backwards" });
    }
  });
  if (!reduce) below.forEach((el, i) => {
    const r = el.getBoundingClientRect(), dy = belowWas[i] - r.top;
    if (Math.abs(dy) > 1 && (seen(r) || (belowWas[i] < vh && belowWas[i] + r.height > 0))) {
      play(el, [{ transform: `translateY(${dy}px)` }, { transform: "none" }], { duration: T_MOVE });
    }
  });
  // What is left in `was` was on screen and is now off the page.
  if (!reduce) was.forEach((r, card) => {
    const g = ghost(card.cloneNode(true), r, list);
    play(g, [{ opacity: 1 }, { opacity: 0 }], { duration: T_OUT, fill: "forwards" })
      .onfinish = () => g.remove();
  });

  // The count rolls: the old reading lifts away where it stood while the new
  // one rises into place, tinted with the accent for a moment.
  if (statWas && (statWas.text !== statEl.textContent || statWas.when !== (whenEl && whenEl.hidden))) {
    if (!reduce) {
      const g = ghost(statWas.copy, statWas.rect, bar);
      play(g, [{ opacity: 1, transform: "none" }, { opacity: 0, transform: "translateY(-6px)" }],
           { duration: T_OUT, fill: "forwards" }).onfinish = () => g.remove();
      play(statEl, [{ opacity: 0, transform: "translateY(6px)" }, { opacity: 1, transform: "none" }],
           { duration: T_IN, delay: T_OUT / 2, fill: "backwards" });
    } else {
      play(statEl, [{ opacity: 0 }, { opacity: 1 }], { duration: T_OUT });
    }
    const ink = getComputedStyle(document.documentElement).getPropertyValue("--accent-ink").trim();
    const rest = getComputedStyle(countEl).color;
    if (ink) play(countEl, [{ color: ink }, { color: rest }], { duration: T_MOVE });
  }

  // The query token: it arrives in its slot and the axes make room for it, or
  // it fades where it was and the axes close the gap.
  const tokNow = !qtok.hidden;
  if (!!tokWas !== tokNow) {
    if (tokNow) {
      play(qtok, reduce ? [{ opacity: 0 }, { opacity: 1 }]
                        : [{ opacity: 0, transform: "scale(.9)" }, { opacity: 1, transform: "none" }],
           { duration: reduce ? T_OUT : T_IN });
    } else if (!reduce) {
      const g = ghost(tokWas.copy, tokWas.rect, bar);
      play(g, [{ opacity: 1, transform: "none" }, { opacity: 0, transform: "scale(.9)" }],
           { duration: T_OUT, fill: "forwards" }).onfinish = () => g.remove();
    }
    // Closing the gap waits until the token is half gone, so the two do not
    // cross.
    const wait = tokNow ? 0 : T_OUT / 2;
    if (!reduce) pills.forEach((el, i) => {
      const dx = pillsWas[i] - el.getBoundingClientRect().left;
      if (Math.abs(dx) > 1) play(el, [{ transform: `translateX(${dx}px)` }, { transform: "none" }],
                                 { duration: T_IN, delay: wait, fill: "backwards" });
    });
  }
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

/* Every control that routes through here — an axis, a page, a page size —
 * changes the state the address carries, so it is written back. A change of
 * filter is played; the rest swap. */
function refresh(filtered) {
  const paint = () => { syncControls(); shelf && shelf.paint(); apply(); };
  if (filtered) played(paint); else paint();
  writeHash();
}

/* ── Wiring ───────────────────────────────────────────────────────────── */
let debounce = null;
if (input) input.addEventListener("input", () => {
  state.q = input.value;
  // Every keystroke asks a new question, and the answer starts at its top.
  state.page = 1;
  if (debounce) clearTimeout(debounce);
  // Filtering is instant; the delay is only so the hash does not get
  // rewritten on every keystroke.
  apply();
  debounce = setTimeout(writeHash, 250);
});

/* 한 쪽에 몇 편 — only the current count shows at the strip's end; the three
 * choices open above it and close on a pick, a click elsewhere or Escape. */
function openSizes(on) {
  if (!sizeMenu) return;
  sizeMenu.hidden = !on;
  if (sizeOpen) sizeOpen.setAttribute("aria-expanded", on ? "true" : "false");
}
document.addEventListener("click", (e) => {
  if (sizeOpen && e.target.closest("[data-psize-open]")) { openSizes(sizeMenu.hidden); return; }
  if (sizeMenu && !sizeMenu.hidden && !e.target.closest("[data-psize]")) openSizes(false);
});

document.addEventListener("click", (e) => {
  const p = e.target.closest("[data-facet-pillar]");
  const sizeBtn = e.target.closest("[data-size]");
  const pageBtn = e.target.closest("[data-page]");
  const stepBtn = e.target.closest("[data-page-rel]");
  // Every control that changes which papers are in the list sends the reader
  // back to its first page: page 4 of one filter is not page 4 of the next,
  // and landing on an emptied page would read as a broken list.
  // The axis is a radio the reader can also switch off: pressing the one
  // that is on clears it, pressing another moves to it.
  if (p) {
    const k = p.dataset.facetPillar;
    state.pillar = state.pillar === k ? "" : k;
    state.page = 1;
    refresh(true);
  }
  else if (pageBtn) { toPage(+pageBtn.dataset.page); }
  else if (stepBtn) { toPage(state.page + +stepBtn.dataset.pageRel); }
  // Changing the page size keeps the reader where they are rather than
  // returning them to the top: the paper that was first on screen is still on
  // the page they land on.
  else if (sizeBtn) {
    const first = (state.page - 1) * state.size;
    state.size = +sizeBtn.dataset.size;
    state.page = Math.floor(first / state.size) + 1;
    keepSize(state.size);
    openSizes(false);
    refresh();
  }
  else if (e.target.closest("[data-reset]")) {
    state.q = ""; state.pillar = ""; state.page = 1;
    refresh(true);
  }
  // The query token's ×: the query goes, the axis stays.
  else if (e.target.closest("[data-q-clear]")) {
    state.q = ""; state.page = 1;
    refresh(true);
  }
});

addEventListener("hashchange", () => {
  played(() => { readHash(); syncControls(); apply(); });
  // A `t=` that `readHash` folded into the query leaves the address with it.
  if (new URLSearchParams(location.hash.replace(/^#/, "")).has("t")) writeHash();
});

// Escape closes the page-size menu. Where a page has a search box, `/`
// focuses it and Escape clears it.
addEventListener("keydown", (e) => {
  if (e.key === "Escape" && sizeMenu && !sizeMenu.hidden) { openSizes(false); return; }
  if (!input) return;
  if (e.key === "/" && document.activeElement !== input && !e.metaKey && !e.ctrlKey) {
    e.preventDefault(); input.focus(); input.select();
  } else if (e.key === "Escape" && document.activeElement === input) {
    state.q = ""; state.page = 1; refresh(); input.blur();
  }
});

/* ── A row's figure, on a resting pointer ─────────────────────────────── */
/* A pointer that rests on a row for a moment brings up the paper's overview
 * figure under it, with its whole caption — the architecture a title only
 * names. Desktop only: a phone has no pointer to rest, and its tap opens the
 * paper. The card is one element, moved and refilled, and it never takes the
 * pointer, so the row under it stays clickable. */
(function () {
  const can = matchMedia("(hover: hover) and (min-width: 721px)");
  const card = document.createElement("div");
  card.className = "figpeek"; card.hidden = true; card.setAttribute("aria-hidden", "true");
  card.innerHTML = '<img alt=""><p class="figpeek-c"></p><p class="figpeek-s"></p>';
  document.body.appendChild(card);
  const img = card.querySelector("img");
  let cur = null, timer = 0;
  function place(row) {
    const r = row.getBoundingClientRect(), m = (row.querySelector(".row-main") || row).getBoundingClientRect();
    const cw = card.offsetWidth, ch = card.offsetHeight, vw = innerWidth, vh = innerHeight;
    let top = r.bottom + 6;
    if (top + ch > vh - 12) top = r.top - ch - 6;
    top = Math.max(12, Math.min(top, vh - ch - 12));
    card.style.left = `${Math.min(m.left, vw - cw - 16) + scrollX}px`;
    card.style.top = `${top + scrollY}px`;
  }
  root.addEventListener("mouseover", (e) => {
    if (!can.matches) return;
    const row = e.target.closest(".row[data-fig]");
    if (!row || row === cur) return;
    cur = row; clearTimeout(timer);
    timer = setTimeout(() => {
      if (cur !== row) return;
      if (img.getAttribute("src") !== row.dataset.fig) img.src = row.dataset.fig;
      card.querySelector(".figpeek-c").textContent = row.dataset.figCap || "";
      card.querySelector(".figpeek-s").textContent = row.dataset.figSrc || "";
      card.hidden = false; place(row);
    }, 160);
  });
  root.addEventListener("mouseout", (e) => {
    const row = e.target.closest(".row[data-fig]");
    if (!row || row.contains(e.relatedTarget)) return;
    cur = null; clearTimeout(timer); card.hidden = true;
  });
  // Once the figure has its real size the card is taller than it was laid out.
  img.addEventListener("load", () => { if (cur && !card.hidden) place(cur); });
})();

/* The axis line scrolls sideways once its axes outrun it; its fade says so
 * until the end is in view. */
if (plineItems) {
  const edge = () => bar.classList.toggle("at-end",
    plineItems.scrollLeft + plineItems.clientWidth >= plineItems.scrollWidth - 4);
  plineItems.addEventListener("scroll", edge, { passive: true });
  addEventListener("resize", edge);
  edge();
}

// Seed or prune before the first paint, so a first visit never flashes a
// badge it is about to withdraw.
if (shelf) shelf.Corpus.sync(cards.map((card) => card.dataset.id));

readHash();
refresh();
})();

/* 빈자리 names its stood-on papers' rewrites in one folded line. What fits on
 * the line shows; the chip counts the rest, names them in its tooltip, and
 * opens or closes the row. Which names fit depends on the width, so it is
 * measured again on resize. */
(function () {
"use strict";
const rows = [...document.querySelectorAll("[data-gapnames]")];
if (!rows.length) return;
function fit(row) {
  const btn = row.querySelector(".gap-more");
  const names = [...row.querySelectorAll(".gap-n")];
  const top = names[0].offsetTop;
  const folded = names.filter((n) => n.offsetTop > top + 2);
  const open = row.classList.contains("is-open");
  btn.hidden = !folded.length && !open;
  btn.textContent = open ? "접기" : `+${folded.length}`;
  btn.title = open ? "" : folded.map((n) => n.textContent).join(" · ");
  btn.setAttribute("aria-label", open ? "접기" : `${folded.length}편 더 보기`);
}
rows.forEach((row) => {
  const btn = row.querySelector(".gap-more");
  btn.addEventListener("click", () => {
    const open = row.classList.toggle("is-open");
    btn.setAttribute("aria-expanded", String(open));
    fit(row);
  });
  fit(row);
});
const refit = () => rows.forEach((row) => { if (!row.classList.contains("is-open")) fit(row); });
// A web font that lands after the first measure moves the line's end.
if (document.fonts) document.fonts.ready.then(refit);
let t;
addEventListener("resize", () => { clearTimeout(t); t = setTimeout(refit, 120); });
})();
