/* ⌘K — the corpus, one keystroke from any page.
 *
 * Reaching a second paper from the one on screen otherwise means walking back
 * to the list, and that walk is the most repeated move on the site: it gets
 * longer every time a rewrite lands. This is the shortcut past it — open, type,
 * Enter, and the reader is on the paper they meant.
 *
 * Both kinds of document answer here. A comparison is otherwise reachable from
 * 같이 읽기 and from the papers it names, and a reader who wants one is rarely
 * standing on either.
 *
 * The whole dialog is built here rather than server-rendered, which is the same
 * rule the other JS-only controls follow from the other side: a browser with no
 * script gets no markup at all, instead of a search box that cannot search. The
 * one thing the build does print is the nav button that opens it, and
 * `site.css` keeps that off an unscripted page.
 *
 * What it searches is `window.ProbeIndex` (`assets/corpus-index.js`) — one file
 * for the whole site, so it is fetched once and cached across every page. How a
 * query is read is `match.js`, the same rule the landing's own filter box uses:
 * the two surfaces answer the same question the same way or one of them is
 * lying.
 *
 * Shelf state rides along where there is any — a starred paper and a read one
 * say so on their own row — but the palette works without `shelf.js`, since
 * finding a paper is not a thing the reader has to have kept anything to do.
 */

(function () {
"use strict";

const data = window.ProbeIndex;
const match = window.ProbeMatch;
if (!data || !match) return;

const PAPERS = Array.isArray(data.papers) ? data.papers : [];
const COMPARISONS = Array.isArray(data.comparisons) ? data.comparisons : [];
if (!PAPERS.length && !COMPARISONS.length) return;
const PILLAR_NAMES = data.pillars || {};

/* Where the site's root is, seen from whatever depth this page sits at. Read
 * off this script's own resolved `src` rather than printed into every page: it
 * is right on `file://`, under `--serve`'s `/probe/` prefix, on Pages, and on
 * `404.html`, which is served at whatever depth the bad URL had. */
const self = document.querySelector('script[src$="assets/palette.js"]');
const ROOT = self ? self.src.replace(/assets\/palette\.js(\?.*)?$/, "") : "";

/* ── The index, compacted once ────────────────────────────────────────── */
/* Fragments rather than one joined string: `match.compact` strips every
 * character that could have fenced them off, so a list is what keeps a query
 * from matching across the end of the title and the start of a tag.
 *
 * Where a word lands is a signal, as it is on the landing. The id and the title
 * are what the paper *is*; tags and 연구 축 are what it is filed under; the
 * tagline is what it does, in the reader's own language — and in this corpus it
 * is the only Korean any of these fields carry, so it is the field a Korean
 * query lands in rather than a nicety.
 */
const NAME = 3, FILED = 2, LINE = 1;

/* One row per document, of either kind. Three things differ between them —
 * where the row links, what the reader can have kept about it, and what the
 * right-hand column prints — so a row resolves all three when it is built and
 * everything downstream stays kind-blind.
 *
 * A comparison's compared ids are `filed`, not `name`: the paper itself is
 * what that id names, so typing one puts the paper above the comparisons that
 * hold it, which is the order a reader typing an id is asking for. */

/* How many comparisons hold each paper. The same count the landing list prints
 * beside a title, from the same payload — a paper row here would otherwise be
 * the one surface that names a paper without saying it has been argued
 * against something. */
const HELD_BY = {};
COMPARISONS.forEach((x) => {
  (x.of || []).forEach((id) => { HELD_BY[id] = (HELD_BY[id] || 0) + 1; });
});

function build(doc, kind) {
  const paper = kind === "paper";
  const key = paper ? doc.id : doc.slug;
  const of = doc.of || [];
  return {
    kind: kind,
    held: paper ? (HELD_BY[doc.id] || 0) : 0,
    /* Shelf records are kept per arXiv id, so a comparison has none to look
     * up — an empty key rather than a slug the store would never answer for. */
    id: paper ? doc.id : "",
    title: doc.title,
    tagline: doc.tagline,
    pillars: doc.pillars || [],
    date: doc.date || "",
    href: ROOT + (paper ? "p/" : "c/") + key + "/index.html",
    tail: paper ? doc.id : of.join(" · "),
    name: [key, doc.title].map(match.compact).filter(Boolean),
    filed: [...(doc.tags || []), ...(doc.pillars || []),
            ...(doc.pillars || []).map((p) => PILLAR_NAMES[p] || ""), ...of]
           .map(match.compact).filter(Boolean),
    line: [match.compact(doc.tagline)].filter(Boolean),
    head: match.compact(doc.title),
  };
}

/* Newest first across both kinds, so an empty box offers what actually landed
 * last rather than every paper before every comparison. Both arrays arrive
 * sorted, and the sort is stable, so a shared date keeps the build's order. */
const ROWS = [...PAPERS.map((d) => build(d, "paper")),
              ...COMPARISONS.map((d) => build(d, "comparison"))];
ROWS.sort((a, b) => (a.date < b.date ? 1 : a.date > b.date ? -1 : 0));
ROWS.forEach((row, i) => { row.order = i; });

const LIMIT = 20;      // more than a reader scans; the list scrolls past it
const RECENT = 8;      // what an empty box offers — the newest, which is why they came

function score(row, terms) {
  let total = 0, hit = 0;
  for (const term of terms) {
    let best = 0;
    if (match.inAny(row.name, term)) best = NAME;
    else if (match.inAny(row.filed, term)) best = FILED;
    else if (match.inAny(row.line, term)) best = LINE;
    if (!best) continue;
    hit += 1;
    total += best;
    // A title that *starts* with the word is the paper the reader is naming,
    // not one that mentions it in passing.
    if (row.head.startsWith(term.t) || row.head.startsWith(term.b)) total += 2;
  }
  return { total: total, hit: hit };
}

function search(q) {
  const terms = match.parse(q);
  if (!terms.length) return { rows: ROWS.slice(0, RECENT), partial: false, all: true };
  const scored = [];
  for (const row of ROWS) {
    const s = score(row, terms);
    if (s.hit) scored.push({ row: row, total: s.total, hit: s.hit });
  }
  // Every term must land — typing more narrows. But one wrong word should not
  // empty a corpus that answers the rest of the query, so when nothing matches
  // in full the bar drops to "any term" and the footer says so. Same fallback
  // the landing's filter makes, for the same reason.
  let kept = scored.filter((s) => s.hit === terms.length);
  const partial = !kept.length && scored.length > 0;
  if (partial) kept = scored;
  kept.sort((a, b) => b.total - a.total || a.row.order - b.row.order);
  return { rows: kept.map((s) => s.row), partial: partial, all: false };
}

/* ── The dialog ───────────────────────────────────────────────────────── */
function esc(s) {
  return String(s === undefined || s === null ? "" : s)
    .replace(/[&<>"]/g, (ch) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[ch]));
}

const root = document.createElement("div");
root.className = "cmdk";
root.hidden = true;
root.innerHTML =
  '<div class="cmdk-scrim" data-cmdk-dismiss></div>' +
  '<div class="cmdk-box" role="dialog" aria-modal="true" aria-label="논문·비교 찾기">' +
    '<div class="cmdk-head">' +
      '<svg class="cmdk-icon" viewBox="0 0 16 16" width="15" height="15" aria-hidden="true" focusable="false">' +
        '<circle cx="7" cy="7" r="4.6" fill="none" stroke="currentColor" stroke-width="1.6"/>' +
        '<path d="M10.4 10.4 14 14" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>' +
      '</svg>' +
      '<input class="cmdk-input" type="text" role="combobox" aria-expanded="true" ' +
        'aria-controls="cmdk-list" aria-autocomplete="list" autocomplete="off" ' +
        'spellcheck="false" placeholder="제목 · 태그 · 연구 축 · arXiv id">' +
      '<button type="button" class="cmdk-esc" data-cmdk-dismiss aria-label="닫기">' +
        '<span class="k">esc</span><span class="x">✕</span></button>' +
    '</div>' +
    '<ul class="cmdk-list" id="cmdk-list" role="listbox" aria-label="검색 결과"></ul>' +
    '<p class="cmdk-foot"><span data-cmdk-note></span>' +
      '<span class="cmdk-keys" aria-hidden="true">↑↓ 이동 · ↵ 열기 · esc 닫기</span></p>' +
  '</div>';

const box = root.querySelector(".cmdk-box");
const input = root.querySelector(".cmdk-input");
const list = root.querySelector(".cmdk-list");
const note = root.querySelector("[data-cmdk-note]");
document.body.appendChild(root);

let shown = [];
let active = 0;
let opener = null;

function shelfMarks(id) {
  const shelf = window.ProbeShelf;
  if (!shelf || !id) return "";
  const star = shelf.Stars.has(id)
    ? '<span class="cmdk-star" title="즐겨찾기" aria-label="즐겨찾기">★</span>' : "";
  const read = shelf.Reads.isDone(id)
    ? '<span class="cmdk-read" aria-label="읽음">읽음</span>' : "";
  return star + read;
}

function draw(result) {
  shown = result.rows;
  active = 0;
  if (!shown.length) {
    list.innerHTML = '<li class="cmdk-none" role="presentation">' +
      '찾는 글이 없습니다. 제목의 한 단어나 arXiv id 로 다시 해보세요.</li>';
  } else {
    list.innerHTML = shown.slice(0, LIMIT).map((row, i) => {
      const chips = row.pillars.slice(0, 2).map((k) =>
        '<span class="chip pillar" data-p="' + esc(k) + '">' + esc(k) + '</span>').join("");
      /* Which kind a row is rides on the left, beside the shelf marks, because
       * that is the column a narrow screen keeps — and where Enter lands is
       * the one thing about a row a reader has to know before pressing it. */
      const kind = row.kind === "comparison"
        ? '<span class="cmdk-kind">비교</span>'
        : (row.held ? '<span class="cmdk-held" title="같이 읽은 글 ' + row.held +
            '편" aria-label="같이 읽은 글 ' + row.held + '편">' +
            '<span aria-hidden="true">↔</span>' + row.held + '</span>' : "");
      return '<li role="presentation"><a class="cmdk-row" role="option" ' +
        'id="cmdk-o-' + i + '" data-i="' + i + '" ' +
        'aria-selected="' + (i === 0 ? "true" : "false") + '" ' +
        'href="' + esc(row.href) + '">' +
        '<span class="cmdk-marks">' + kind + shelfMarks(row.id) + '</span>' +
        '<span class="cmdk-main"><span class="cmdk-title">' + esc(row.title) + '</span>' +
        '<span class="cmdk-line">' + esc(row.tagline) + '</span></span>' +
        '<span class="cmdk-meta">' + chips +
        '<span class="cmdk-id">' + esc(row.tail) + '</span></span></a></li>';
    }).join("");
  }
  note.textContent = result.all
    ? "최근 " + shown.length + "편"
    : result.partial
      ? "일부만 일치 · " + shown.length + "편"
      : shown.length + "편";
  paintActive();
}

function rows() { return [...list.querySelectorAll(".cmdk-row")]; }

function paintActive() {
  const all = rows();
  if (!all.length) { input.removeAttribute("aria-activedescendant"); return; }
  active = Math.min(Math.max(active, 0), all.length - 1);
  all.forEach((el, i) => el.setAttribute("aria-selected", i === active ? "true" : "false"));
  input.setAttribute("aria-activedescendant", all[active].id);
  all[active].scrollIntoView({ block: "nearest" });
}

function move(step) {
  const n = rows().length;
  if (!n) return;
  // Wrapping is what makes ↑ from the top reach the last result, which is the
  // fastest way to the bottom of a short list.
  active = (active + step + n) % n;
  paintActive();
}

function open() {
  if (!root.hidden) return;
  opener = document.activeElement;
  root.hidden = false;
  document.documentElement.classList.add("cmdk-on");
  input.value = "";
  draw(search(""));
  input.focus();
}

function close() {
  if (root.hidden) return;
  root.hidden = true;
  document.documentElement.classList.remove("cmdk-on");
  // Back to whatever the reader was on before they reached for the shortcut —
  // a dialog that drops focus on `<body>` costs a keyboard reader their place.
  if (opener && opener.isConnected) opener.focus();
  opener = null;
}

/* ── Wiring ───────────────────────────────────────────────────────────── */
input.addEventListener("input", () => draw(search(input.value)));

root.addEventListener("click", (e) => {
  if (e.target.closest("[data-cmdk-dismiss]")) { close(); return; }
  if (e.target.closest(".cmdk-row")) close();       // the link navigates on its own
});

list.addEventListener("pointermove", (e) => {
  // A finger dragging the list is scrolling it, not choosing — following that
  // would walk the selection down the list under the reader's own thumb.
  if (e.pointerType !== "mouse") return;
  const row = e.target.closest(".cmdk-row");
  if (!row) return;
  const i = +row.dataset.i;
  if (i !== active) { active = i; paintActive(); }
});

box.addEventListener("keydown", (e) => {
  if (e.key === "ArrowDown") { e.preventDefault(); move(1); }
  else if (e.key === "ArrowUp") { e.preventDefault(); move(-1); }
  else if (e.key === "Enter") {
    const row = rows()[active];
    if (row) { e.preventDefault(); close(); row.click(); }
  } else if (e.key === "Escape") { e.preventDefault(); close(); }
  // Nothing inside is focusable but the box itself, so Tab has nowhere to go
  // that is not out of an open dialog.
  else if (e.key === "Tab") { e.preventDefault(); input.focus(); }
});

addEventListener("keydown", (e) => {
  if ((e.metaKey || e.ctrlKey) && !e.altKey && (e.key === "k" || e.key === "K")) {
    e.preventDefault();
    root.hidden ? open() : close();
  }
});

document.addEventListener("click", (e) => {
  if (e.target.closest("[data-cmdk-open]")) { e.preventDefault(); open(); }
});

// Which key the button's tooltip advertises is the one thing about it the
// build cannot know, so it prints the majority platform's and this corrects
// it for a Mac.
if (/Mac|iPhone|iPad/.test(navigator.platform || navigator.userAgent)) {
  document.querySelectorAll(".nav-cmdk").forEach((btn) => {
    btn.title = btn.title.replace("Ctrl K", "⌘K");
  });
}

// A star or a 읽음 mark set on the page behind changes what a row should say.
document.addEventListener("probe:shelf-change", () => {
  if (!root.hidden) draw(search(input.value));
});
})();
