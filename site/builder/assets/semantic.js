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

/* A hit lands on the section it matched, not on the paper: the corpus is
 * written in 60 KB documents and "the paper is somewhere in here" is the answer
 * the reader already had. */
function card(hit) {
  const href = `${hit.path}${hit.anchor ? "#" + hit.anchor : ""}`;
  const pillars = (hit.pillars || []).map(
    (p) => `<span class="chip pillar" data-p="${esc(p)}">${esc(p)}</span>`).join("");
  return (
    `<a class="sem-hit" href="${esc(href)}">` +
    `<span class="sem-kind k-${esc(hit.kind)}">${esc(KINDS[hit.kind] || hit.kind)}</span>` +
    `<span class="sem-body"><b>${esc(hit.title)}</b>` +
    `<span class="sem-ctx">${esc(hit.context)}</span>` +
    `<span class="sem-snip">${esc(hit.snippet)}</span></span>` +
    `<span class="sem-facets">${pillars}</span></a>`
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

function render(q, data) {
  const hits = data.hits || [];
  if (!hits.length) return hide();
  box.innerHTML =
    `<p class="sem-head">의미 검색 <span>· “${esc(q)}” 에 가까운 대목 ${hits.length}</span></p>` +
    readAs(data.expanded) + hits.map(card).join("");
  box.hidden = false;
  shown = q;
}

function ask(q) {
  if (inflight) inflight.abort();
  const ctl = new AbortController();
  inflight = ctl;
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
    .catch(hide)
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
