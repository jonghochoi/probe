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
 */

(function () {
"use strict";

const api = document.body.dataset.searchApi;
const box = document.querySelector("[data-sem]");
const input = document.querySelector("[data-q]");
if (!api || !box || !input) return;

const MIN = 2;
const WAIT = 350;          // after typing stops — one request per question, not per keystroke
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

let timer = null;
let inflight = null;
let shown = "";

function hide() {
  box.hidden = true;
  box.innerHTML = "";
  shown = "";
}

function esc(s) {
  return String(s == null ? "" : s).replace(/[&<>"]/g,
    (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
}

/* Every paper's title, off the list already on the page. A chunk carries the
 * arXiv id of the paper it came from and nothing more, so without this the
 * block can name a passage but not the work it belongs to — and an id is not
 * a name. Reading the landing rows keeps the two in step for free: no title
 * on any of the 1,502 rows in the index, and nothing to re-embed when one
 * changes. */
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
      `<span class="sem-snip">${esc(hit.snippet)}</span></span></a>`
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

/* The lexical list answers while the reader is still typing, so without this
 * the seconds the endpoint spends read as a page that has already finished.
 * It says only that the question is out — a failure takes the whole block
 * away with it, which is what the layer below is for. */
function pending(q) {
  box.innerHTML =
    `<p class="sem-head sem-wait">의미 검색 <span>· “${esc(q)}” 에 가까운 대목을 찾는 중</span></p>`;
  box.hidden = false;
  shown = "";
}

function render(q, data) {
  const hits = data.hits || [];
  if (!hits.length) return hide();
  const groups = byPaper(hits);
  const kept = groups.reduce((n, g) => n + g.hits.length, 0);
  box.innerHTML =
    `<p class="sem-head">의미 검색 <span>· “${esc(q)}” — 논문 ${groups.length}편에서 ` +
    `${kept} 대목</span></p>` +
    readAs(data.expanded) + groups.map(group).join("");
  box.hidden = false;
  shown = q;
}

function ask(q) {
  if (inflight) inflight.abort();
  const ctl = new AbortController();
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
      // The reader kept typing while this was in the air; answering the
      // question they have moved on from is worse than not answering.
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

function schedule() {
  const q = input.value.trim();
  if (timer) clearTimeout(timer);
  if (q.length < MIN) return hide();
  if (q === shown) return;
  timer = setTimeout(() => ask(q), WAIT);
}

input.addEventListener("input", schedule);
addEventListener("hashchange", schedule);
schedule();                                   // a shared `#q=` link asks on arrival
})();
