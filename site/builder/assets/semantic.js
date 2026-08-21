/* Semantic search — the one thing on this site that talks to a server.
 *
 * It is an enhancement and never a dependency. The page ships and works without
 * it: `filter.js` matches the haystacks the build put on every row, and this
 * script adds a block above them when a remote index has something better. Any
 * failure — no endpoint configured, offline, `file://`, a 502, a slow answer —
 * removes the block and leaves the page exactly as it was.
 *
 * The endpoint is emitted onto `<body data-search-api>` only when the build was
 * given one, so a default build never loads this file and never makes a request.
 *
 * It answers a question the reader submitted with Enter, not the one they are
 * in the middle of typing. `filter.js` is the layer that keeps up with a
 * keystroke; a round trip and a model call are not, and a half-typed word is
 * not yet a question — so the block offers before it asks.
 */

(function () {
"use strict";

const api = document.body.dataset.searchApi;
const box = document.querySelector("[data-sem]");
const input = document.querySelector("[data-q]");
if (!api || !box || !input) return;
// The build ships this beside the box wherever it shipped an endpoint. It
// starts disabled and is the same submit Enter is, for a reader who is on a
// touch keyboard or has never been told about the key.
const go = document.querySelector("[data-ask]");

const MIN = 2;
/* What the remote block gets before the lexical list below it is the better
 * answer. The endpoint reads a query into search terms with one model and
 * embeds the result with another, in series, so an uncached question spends a
 * median of about 2 s inside the function before a reader's round trip is even
 * counted. The block is additive — the lexical list is already on screen — so
 * the cost of waiting is a late arrival, not a blank page. */
const TIMEOUT = 5000;
/* What kind of passage matched. A term panel and a section are both hits and
 * they are not the same offer: one is a definition, one is an argument. */
const KINDS = { paper: "논문", section: "섹션", term: "용어", figure: "그림" };

let inflight = null;
/* Whether the block is answering, and how much of an answer it is. `filter.js`
 * owns the strip that names the two surfaces and the list on the other one, so
 * it needs both facts: that there is something to tab to, and the count to
 * print on the tab. This only reports them. */
let answered = false;
function announce(on, papers, hits) {
  if (!on && !answered) return;
  answered = on;
  document.dispatchEvent(new CustomEvent("probe:answer", {
    detail: { answered: on, papers: papers || 0, hits: hits || 0 },
  }));
}

/* The question the block currently answers, and `null` whenever it does not —
 * offering, waiting, or gone. An empty box is a question like any other here,
 * so "nothing on screen" cannot be spelled the same way as "". */
let shown = null;

function hide() {
  box.hidden = true;
  box.innerHTML = "";
  shown = null;
  announce(false);
}

/* The block belongs to one question at a time. Dropping the reference before
 * aborting is what hands it over: the abort lands in the `catch` below, and a
 * request that no longer owns the block must not clear what replaced it. */
function cancel() {
  if (!inflight) return;
  const ctl = inflight;
  inflight = null;
  ctl.abort();
}

function esc(s) {
  return String(s == null ? "" : s).replace(/[&<>"]/g,
    (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
}

/* Every paper's title, off the list already on the page. A chunk carries the
 * arXiv id of the paper it came from and nothing more, so without this the
 * block can name a passage but not the work it belongs to — and an id is not
 * a name. Reading the landing rows keeps the two in step for free: no title
 * on any row in the index, and nothing to re-embed when one changes. */
const TITLES = new Map(
  [...document.querySelectorAll("[data-star][data-star-title]")]
    .map((el) => [el.dataset.star, el.dataset.starTitle]));

/* Papers, ordered by their best hit. One question is usually answered in
 * several places at once — the same term glossed in five papers is five hits
 * that read almost identically — and a flat list spends the whole block on
 * that repetition while never saying how many works are behind it. */
function byPaper(hits) {
  const order = [];
  const groups = new Map();
  for (const hit of hits) {
    const id = hit.paperId || "";
    if (!groups.has(id)) { groups.set(id, []); order.push(id); }
    const kept = groups.get(id);
    // Two chunks of one passage are one place to go, not two.
    if (!kept.some((h) => h.kind === hit.kind && h.title === hit.title
                       && h.anchor === hit.anchor)) kept.push(hit);
  }
  return order.map((id) => ({ id, hits: groups.get(id) }));
}

/* A hit lands on the section it matched, not on the paper: the corpus is
 * written in 60 KB documents and "the paper is somewhere in here" is the answer
 * the reader already had. The heading above it is the one link that does go to
 * the paper, for a reader who recognises the work and wants the whole of it. */
function group(g) {
  const first = g.hits[0];
  const pillars = (first.pillars || []).slice(0, 3).map(
    (p) => `<span class="chip pillar" data-p="${esc(p)}">${esc(p)}</span>`).join("");
  const passages = g.hits.map((hit) => {
    const href = `${hit.path}${hit.anchor ? "#" + hit.anchor : ""}`;
    return (
      `<a class="sem-sub" href="${esc(href)}">` +
      `<span class="sem-kind k-${esc(hit.kind)}">${esc(KINDS[hit.kind] || hit.kind)}</span>` +
      `<span class="sem-body"><b>${esc(hit.title)}</b>` +
      // A caption is its own chunk, so its excerpt trims to nothing: the line
      // is left out rather than drawn empty under a title that says it all.
      (hit.snippet ? `<span class="sem-snip">${esc(hit.snippet)}</span>` : "") +
      `</span></a>`
    );
  }).join("");
  return (
    `<div class="sem-group">` +
    `<a class="sem-ghead" href="${esc(first.path)}">` +
    `<span class="sem-gt">${esc(TITLES.get(g.id) || g.id)}</span>` +
    `<span class="sem-gid">${esc(g.id)}</span>${pillars}` +
    `<span class="sem-gn">${g.hits.length} 대목</span></a>` +
    passages + `</div>`
  );
}

/* What the query was read as. A search that silently rewrites itself cannot be
 * trusted, and a reader who sees "느려터진 → inference latency" can tell a good
 * answer from a misread one at a glance. */
function readAs(terms) {
  if (!terms || !terms.length) return "";
  return `<p class="sem-read">읽은 뜻 ${terms.slice(0, 6).map(
    (t) => `<span class="sem-term">${esc(t)}</span>`).join("")}</p>`;
}

/* Before the question is asked. The reader is typing and the list below is
 * already narrowing, so this line is the whole of the remote layer's presence:
 * it names what Enter would ask, and nothing has been spent yet. */
function offer(q) {
  box.innerHTML =
    `<p class="sem-head sem-ask">의미 검색 <span>· <kbd class="sem-key">Enter</kbd> ` +
    `를 누르면 “${esc(q)}” 에 가까운 대목을 찾습니다</span></p>`;
  box.hidden = false;
  shown = null;
  announce(false);
}

/* The lexical list answers while the reader is still typing, so without this
 * the seconds the endpoint spends read as a page that has already finished.
 * It says only that the question is out — a failure takes the whole block
 * away with it, which is what the layer below is for. */
function pending(q) {
  box.innerHTML =
    `<p class="sem-head sem-wait">의미 검색 <span>· “${esc(q)}” 에 가까운 대목을 찾는 중</span></p>`;
  box.hidden = false;
  shown = null;
  announce(false);
}

function render(q, data) {
  const hits = data.hits || [];
  if (!hits.length) return hide();
  const groups = byPaper(hits);
  const kept = groups.reduce((n, g) => n + g.hits.length, 0);
  // No heading of its own: the strip above names this surface and counts it,
  // and the box the reader typed in is still on screen with the question in
  // it. A line repeating both would be the third time the page says it.
  box.innerHTML = readAs(data.expanded) + groups.map(group).join("");
  box.hidden = false;
  shown = q;
  announce(true, groups.length, kept);
}

function ask(q) {
  cancel();
  const ctl = new AbortController();
  ctl.q = q;                            // what the block is waiting on, while it waits
  inflight = ctl;
  pending(q);
  const bail = setTimeout(() => ctl.abort(), TIMEOUT);
  fetch(api, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ q, limit: 8 }),
    signal: ctl.signal,
  })
    .then((r) => (r.ok ? r.json() : Promise.reject(r.status)))
    .then((data) => {
      // The block belongs to the question in the box; a late answer to any
      // other one is worse than no answer at all.
      if (input.value.trim() === q) render(q, data);
    })
    // Superseded by a later question rather than failed: that request owns the
    // block now, and aborting this one must not take its waiting line down.
    .catch(() => { if (inflight === ctl) hide(); })
    .finally(() => {
      clearTimeout(bail);
      if (inflight === ctl) inflight = null;
    });
}

/* One path in, from every route the query moves by. `submit` is the whole
 * difference between the two of them: a submitted question is asked, a typed
 * one is offered. */
function follow(submit) {
  const q = input.value.trim();
  // Nothing to ask until there is a question: the button says so rather than
  // taking a press and doing nothing with it.
  if (go) go.disabled = q.length < MIN;
  // Already answered, or already out: pressing Enter twice is one question,
  // and editing back to the question in the air keeps the answer coming.
  if (q === shown || (inflight && inflight.q === q)) return;
  cancel();
  if (q.length < MIN) return hide();
  if (submit) ask(q); else offer(q);
}

/* Enter submits. Not while an IME is composing it: on a Korean keyboard the
 * first Enter commits the syllable under the cursor, and taking that one would
 * ask the half-written question this layer exists to stop asking. */
input.addEventListener("keydown", (e) => {
  if (e.key !== "Enter" || e.isComposing || e.keyCode === 229) return;
  e.preventDefault();
  follow(true);
});

if (go) go.addEventListener("click", () => follow(true));
input.addEventListener("input", () => follow(false));
// The box is emptied by things that are not typing — Escape, 필터 초기화 — and
// none of them fire `input`; `filter.js` says so here instead.
document.addEventListener("probe:query", () => follow(false));
/* Which surface the reader is looking at. The strip is `filter.js`'s — it is
 * the one that knows what is on the other tab — so the block does not choose,
 * it is told. An answer is left in place while it is off screen: the reader is
 * one press from it, and asking the endpoint again for what is already here
 * would be paying twice for one question. */
document.addEventListener("probe:pane", (e) => {
  if (shown === null) return;
  box.hidden = e.detail.pane !== "sem";
});

// A `#q=` link carries a question somebody already asked, and arriving at one
// is not typing it — both the shared link and the reader's own history ask.
addEventListener("hashchange", () => follow(true));
follow(true);
})();
