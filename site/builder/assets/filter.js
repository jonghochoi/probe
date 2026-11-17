/* Analysis-list filter, pager and deep-link state.
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
const tabsEl = root.querySelector("[data-restabs]");
const tabBtns = tabsEl ? [...tabsEl.querySelectorAll("[data-restab]")] : [];
// The two readouts close the axis line: what the filter leaves behind is a
// fact about the list, said where the list is filtered from.
const countEl = document.querySelector("[data-result-count]");
const whenEl = document.querySelector("[data-corpus-when]");
// The analysis list has no search box — a word search is ⌘K's — so a query arrives
// only through the address (`#q=`), and the box is read when a page has one.
const input = document.querySelector("[data-q]");
const resetBtns = [...document.querySelectorAll("[data-reset]")];

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
  if (input && input.value !== state.q) {
    input.value = state.q;
    // Setting `.value` fires no `input`, so Escape and 필터 초기화 change the
    // query without anything hearing it. Whatever else reads the box off the
    // page — `semantic.js` — is told here rather than made to watch each
    // control that can empty it.
    document.dispatchEvent(new CustomEvent("probe:query"));
  }
  document.querySelectorAll("[data-facet-pillar]").forEach((b) => {
    b.setAttribute("aria-pressed", b.dataset.facetPillar === state.pillar ? "true" : "false");
  });
  sizeBtns.forEach((b) => b.setAttribute(
    "aria-pressed", +b.dataset.size === state.size ? "true" : "false"));
  if (sizeLabel) sizeLabel.textContent = String(state.size);
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

  // On 의미 the list is not on screen at all: the other tab is.
  const listOff = answered && pane === "sem";
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
  const onPage = new Set(listOff ? [] : rows.slice(from, from + size));

  cards.forEach((card) => {
    card.hidden = !onPage.has(card);
  });

  rows.forEach((row) => list.appendChild(row));
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
  if (listhead) listhead.hidden = onPage.size < 1;
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

const SMOOTH = matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth";

function toPage(n) {
  state.page = n;
  refresh();
  // The new page is drawn above where the reader is standing — they clicked a
  // strip at the foot of the last one — so the list is brought back under the
  // bar rather than leaving them at the bottom of a page they have not read.
  root.scrollIntoView({ block: "start", behavior: SMOOTH });
}

/* Every control that routes through here — an axis, a page, a page size — is about the list, so using one is a request for the tab the list is
 * on. Typing does not: `apply()` is what a keystroke calls, and the strip
 * stays where the answer left it. */
function refresh() {
  // `apply()` runs at the end of this function either way, so the switch only
  // has to say so — going through `setPane()` would paint the page twice.
  if (answered && pane !== "lex") { pane = "lex"; tellPane(); }
  syncControls(); shelf && shelf.paint(); apply(); writeHash();
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
    refresh();
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

addEventListener("hashchange", () => {
  readHash(); syncControls(); apply();
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

/* On a phone the axis line scrolls sideways; its fade says so until the end
 * is in view. */
const plineItems = document.querySelector("[data-pline]");
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
