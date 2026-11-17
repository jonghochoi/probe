/* ⌘K — the corpus, one keystroke from any page.
 *
 * Reaching a second paper from the one on screen otherwise means walking back
 * to the list, and that walk is the most repeated move on the site: it gets
 * longer every time a rewrite lands. This is the shortcut past it — open, type,
 * Enter, and the reader is on the paper they meant.
 *
 * Both kinds of document answer here. A comparison is otherwise reachable from
 * 비교 and from the papers it names, and a reader who wants one is rarely
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
 * query is read is `match.js`, the same rule the analysis list reads a `#q=` with:
 * the two surfaces answer the same question the same way or one of them is
 * lying.
 *
 * A build given a search endpoint adds a second answer: a tab of passages the
 * remote index finds by meaning, asked for only when the reader takes the row
 * that offers it (see "의미" below).
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
const PILLAR_LABELS = data.pillarLabels || {};

/* Where the site's root is, seen from whatever depth this page sits at. Read
 * off this script's own resolved `src` rather than printed into every page: it
 * is right on `file://`, under `--serve`'s `/probe/` prefix, on Pages, and on
 * `404.html`, which is served at whatever depth the bad URL had.
 *
 * `currentScript` first, since it is this script whatever its URL says. The
 * selector behind it matches a substring, not a suffix: every `src` carries
 * the build's `?v=` token after the file name, so a suffix match finds no
 * script, the root comes back empty, and every row resolves against the page
 * it was opened from — `p/A/p/B/index.html` from any paper. */
const self = document.currentScript
  || document.querySelector('script[src*="assets/palette.js"]');
const ROOT = self ? self.src.replace(/assets\/palette\.js(\?.*)?$/, "") : "";

/* ── The index, compacted once ────────────────────────────────────────── */
/* Fragments rather than one joined string: `match.compact` strips every
 * character that could have fenced them off, so a list is what keeps a query
 * from matching across the end of the title and the start of an axis.
 *
 * Where a word lands is a signal, as it is on the analysis list. The id and the title
 * are what the paper *is*; its 연구 축 are what it is filed under; the
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

function build(doc, kind) {
  const paper = kind === "paper";
  const key = paper ? doc.id : doc.slug;
  const of = doc.of || [];
  return {
    kind: kind,
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
    filed: [...(doc.pillars || []),
            ...(doc.pillars || []).map((p) => PILLAR_NAMES[p] || ""),
            ...(doc.pillars || []).map((p) => PILLAR_LABELS[p] || ""), ...of]
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
  // the analysis list's filter makes, for the same reason.
  let kept = scored.filter((s) => s.hit === terms.length);
  const partial = !kept.length && scored.length > 0;
  if (partial) kept = scored;
  kept.sort((a, b) => b.total - a.total || a.row.order - b.row.order);
  return { rows: kept.map((s) => s.row), partial: partial, all: false };
}

/* ── How an excerpt prints ─────────────────────────────────────────────
 * The index answers with excerpts of the rewrites as written, and a rewrite
 * writes its inline math as TeX — `\hat{\mathbf{x}}_{o}` reads as noise in a
 * two-line excerpt — so a passage prints through this and reads `x̂ₒ`. It
 * covers the commands the corpus actually writes — fonts, accents, Greek, the
 * common operators, sub- and superscripts — and leaves anything else as its
 * bare name rather than guessing; the page itself is where a formula is read
 * properly. */
const SYM = {
  alpha: "α", beta: "β", gamma: "γ", delta: "δ", epsilon: "ε", varepsilon: "ε",
  zeta: "ζ", eta: "η", theta: "θ", iota: "ι", kappa: "κ", lambda: "λ", mu: "μ",
  nu: "ν", xi: "ξ", pi: "π", rho: "ρ", sigma: "σ", tau: "τ", upsilon: "υ",
  phi: "φ", varphi: "φ", chi: "χ", psi: "ψ", omega: "ω",
  Gamma: "Γ", Delta: "Δ", Theta: "Θ", Lambda: "Λ", Xi: "Ξ", Pi: "Π",
  Sigma: "Σ", Phi: "Φ", Psi: "Ψ", Omega: "Ω",
  times: "×", cdot: "·", in: "∈", notin: "∉", to: "→", rightarrow: "→",
  leftarrow: "←", Rightarrow: "⇒", mapsto: "↦", top: "⊤", sim: "~", pm: "±",
  dots: "…", ldots: "…", cdots: "⋯", star: "⋆", mid: "|", sum: "∑", prod: "∏",
  int: "∫", le: "≤", leq: "≤", ge: "≥", geq: "≥", neq: "≠", ne: "≠",
  approx: "≈", propto: "∝", odot: "⊙", otimes: "⊗", oplus: "⊕", circ: "∘",
  partial: "∂", nabla: "∇", infty: "∞", ell: "ℓ", forall: "∀", exists: "∃",
  subset: "⊂", subseteq: "⊆", cup: "∪", cap: "∩", langle: "⟨", rangle: "⟩",
  lVert: "‖", rVert: "‖", Vert: "‖", lvert: "|", rvert: "|", lfloor: "⌊",
  rfloor: "⌋", lceil: "⌈", rceil: "⌉", max: "max", min: "min", log: "log",
  exp: "exp", sin: "sin", cos: "cos", tanh: "tanh", arg: "arg", argmax: "argmax",
  argmin: "argmin", left: "", right: "", quad: " ", qquad: " ",
};
const ACCENT = { hat: "̂", widehat: "̂", tilde: "̃", widetilde: "̃",
                 bar: "̄", overline: "̄", dot: "̇", ddot: "̈", vec: "⃗" };
// Patterns as strings: each is built into the rule that reads its argument.
const FONT = "\\\\(?:mathbf|mathrm|mathcal|mathbb|mathit|mathsf|mathtt|boldsymbol|bm|" +
             "text|textbf|textit|textrm|operatorname|rm)(?![A-Za-z])";
const ACCENTS = "\\\\(" + Object.keys(ACCENT).join("|") + ")(?![A-Za-z])";
const SUB = { 0: "₀", 1: "₁", 2: "₂", 3: "₃", 4: "₄", 5: "₅", 6: "₆", 7: "₇", 8: "₈", 9: "₉",
              "+": "₊", "-": "₋", "=": "₌", "(": "₍", ")": "₎", ".": ".", ",": ",", a: "ₐ", e: "ₑ", h: "ₕ", i: "ᵢ",
              j: "ⱼ", k: "ₖ", l: "ₗ", m: "ₘ", n: "ₙ", o: "ₒ", p: "ₚ", r: "ᵣ", s: "ₛ", t: "ₜ",
              u: "ᵤ", v: "ᵥ", x: "ₓ" };
const SUP = { 0: "⁰", 1: "¹", 2: "²", 3: "³", 4: "⁴", 5: "⁵", 6: "⁶", 7: "⁷", 8: "⁸", 9: "⁹",
              "+": "⁺", "-": "⁻", "=": "⁼", "(": "⁽", ")": "⁾", ".": ".", a: "ᵃ", b: "ᵇ", c: "ᶜ", d: "ᵈ",
              e: "ᵉ", f: "ᶠ", g: "ᵍ", h: "ʰ", i: "ⁱ", j: "ʲ", k: "ᵏ", l: "ˡ", m: "ᵐ", n: "ⁿ",
              o: "ᵒ", p: "ᵖ", r: "ʳ", s: "ˢ", t: "ᵗ", u: "ᵘ", v: "ᵛ", w: "ʷ", x: "ˣ", y: "ʸ",
              z: "ᶻ", T: "ᵀ", "⊤": "ᵀ", "*": "*", "′": "′", "'": "′" };
// One brace group, innermost first — every rule below reads a group that has
// no group inside it, and the loop runs until none is left to read.
const ARG = "\\{([^{}]*)\\}";

function script(body, table, mark) {
  const chars = [...body.replace(/\s+/g, "")];
  if (chars.length && chars.every((ch) => table[ch])) return chars.map((ch) => table[ch]).join("");
  return mark + (chars.length > 1 ? "(" + body + ")" : body);
}

function readable(s) {
  let t = String(s == null ? "" : s)
    .replace(/\\\\(?=[A-Za-z{}|%,!; ])/g, "\\")        // a fence's doubled escape
    .replace(/\$`([^`]*)`\$/g, "$1")
    // Escaped braces are text, not groups: parked where the group rules below
    // cannot read them, and put back at the end.
    .replace(/\\\{/g, "").replace(/\\\}/g, "")
    .replace(/\\([%#&_$])/g, "$1").replace(/\\\|/g, "‖")
    // Symbols first, while each command still ends where its letters do —
    // with a font command dropped, `\neq\mathcal{F}` would read as `\neqF`.
    .replace(/\\([A-Za-z]+)/g, (m, k) => (k in SYM ? SYM[k] : m));
  for (let i = 0; i < 8; i++) {
    const before = t;
    t = t
      .replace(new RegExp(FONT + "\\s*" + ARG, "g"), (m, a) => a)
      .replace(new RegExp("\\\\[dt]?frac\\s*" + ARG + "\\s*" + ARG, "g"), (m, a, b) => a + "/" + b)
      .replace(new RegExp("\\\\sqrt\\s*" + ARG, "g"), (m, a) => "√" + a)
      .replace(new RegExp(ACCENTS + "\\s*" + ARG, "g"),
        (m, k, a) => ([...a].length === 1 ? a + ACCENT[k] : a))
      .replace(new RegExp("_" + ARG, "g"), (m, a) => script(a, SUB, "_"))
      .replace(new RegExp("\\^" + ARG, "g"), (m, a) => script(a, SUP, "^"))
      .replace(new RegExp(ARG, "g"), "$1");
    if (t === before) break;
  }
  return t
    .replace(new RegExp(FONT + "\\s*", "g"), "")
    .replace(new RegExp(ACCENTS + "\\s*([A-Za-z])", "g"), (m, k, a) => a + ACCENT[k])
    .replace(/\\([A-Za-z]+)/g, "$1")
    .replace(/\\[,;:! ]/g, " ")
    .replace(/_([A-Za-z0-9])/g, (m, ch) => SUB[ch] || m)
    .replace(/\^([A-Za-z0-9⊤*'])/g, (m, ch) => SUP[ch] || m)
    .replace(//g, "{").replace(//g, "}")
    .replace(/[ \t]{2,}/g, " ");
}

/* ── 의미 — the remote index ──────────────────────────────────────────── */
/* The endpoint `site/search/` deploys, carried by the index rather than by
 * each page: the index already reaches every page, and a build without
 * `--search-api` leaves the field out, so a default build shows no tab and
 * makes no request.
 *
 * It is asked only when the reader chooses to. A sentence typed here is
 * matched letter for letter as it is typed, and that list is often noise — a
 * question's particles land in some tagline or other, and "일부만 일치" can be
 * forty papers — but a round trip and two model calls per keystroke is a cost
 * nobody chose. So the 글자 list ends on one row that offers the question to
 * the index, and the 의미 tab holds the same row until it is taken. */
const API = typeof data.searchApi === "string" ? data.searchApi : "";
const MIN = 2;
/* An uncached question spends two to six seconds in the function before the
 * reader's own round trip, so the cap sits well past the slow end of that: a
 * give-up costs the reader the answer they chose to wait for. */
const TIMEOUT = 10000;
const KINDS = { paper: "논문", section: "섹션", term: "용어", figure: "그림" };
const PASSAGES = 3;      // per paper: the best three are the answer, the rest repeat it
const PAPER = new Map(PAPERS.map((p) => [p.id, p]));

/* One answer per question for the life of the page: going back to the 글자
 * tab and returning, or editing back to a question already asked, costs no
 * second request. */
const answers = new Map();
/* The question the 의미 tab is about and where it stands: `idle` (offered,
 * not asked), `wait`, `done` or `fail`. */
let sem = { q: "", state: "idle", data: null };
let inflight = null;

function forget() {
  if (inflight) { inflight.abort(); inflight = null; }
  sem = { q: "", state: "idle", data: null };
}

function ask(q) {
  if (!API || q.length < MIN) return;
  tab = "sem";
  active = 0;
  if (sem.q === q && sem.state !== "fail" && sem.state !== "idle") return draw();
  if (inflight) { inflight.abort(); inflight = null; }
  if (answers.has(q)) {
    sem = { q: q, state: "done", data: answers.get(q) };
    return draw();
  }
  sem = { q: q, state: "wait", data: null };
  draw();
  const ctl = new AbortController();
  inflight = ctl;
  const bail = setTimeout(() => ctl.abort(), TIMEOUT);
  fetch(API, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ q: q, limit: 12 }),
    signal: ctl.signal,
  })
    .then((r) => (r.ok ? r.json() : Promise.reject(r.status)))
    .then((d) => {
      answers.set(q, d);
      // An answer to a question no longer in the box is dropped: the tab
      // belongs to what the reader is looking at.
      if (sem.q === q) { sem = { q: q, state: "done", data: d }; active = 0; draw(); }
    })
    .catch(() => {
      if (inflight === ctl && sem.q === q) { sem = { q: q, state: "fail", data: null }; draw(); }
    })
    .finally(() => {
      clearTimeout(bail);
      if (inflight === ctl) inflight = null;
    });
}

/* Papers, ordered by their best hit, each with its passages. One question is
 * often answered in one paper several times over, and a flat list spends the
 * tab on that repetition while never saying how many works are behind it. */
function byPaper(hits) {
  const order = [];
  const groups = new Map();
  for (const hit of hits || []) {
    const id = hit.paperId || "";
    if (!groups.has(id)) { groups.set(id, []); order.push(id); }
    const kept = groups.get(id);
    // Two chunks of one passage are one place to go, not two.
    if (!kept.some((h) => h.kind === hit.kind && h.title === hit.title
                       && h.anchor === hit.anchor)) kept.push(hit);
  }
  return order.map((id) => ({ id: id, hits: groups.get(id) }));
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
        'spellcheck="false" placeholder="' +
        (API ? "제목 · 태그 · arXiv id — 또는 찾는 내용을 문장으로"
             : "제목 · 태그 · 연구 축 · arXiv id") + '">' +
      '<button type="button" class="cmdk-esc" data-cmdk-dismiss aria-label="닫기">' +
        '<span class="k">esc</span><span class="x">' +
        '<svg class="ico ico-close" viewBox="0 0 16 16" width="13" height="13" ' +
          'fill="none" stroke="currentColor" stroke-width="1.6" ' +
          'stroke-linecap="round" aria-hidden="true" focusable="false">' +
          '<path d="M3.8 3.8 12.2 12.2M12.2 3.8 3.8 12.2"/></svg></span></button>' +
    '</div>' +
    /* The two answers, one at a time. Two buttons, one pressed — the same
     * reading the analysis list's strip has, for the same reason: what each
     * shows is a list of rows rather than one panel to point a `tab` at. */
    '<div class="cmdk-tabs" role="group" aria-label="검색 결과" hidden>' +
      '<button type="button" class="cmdk-tab" data-cmdk-tab="lex" aria-pressed="true">' +
        '글자<span class="cmdk-tab-n" data-cmdk-n="lex"></span></button>' +
      '<button type="button" class="cmdk-tab" data-cmdk-tab="sem" aria-pressed="false">' +
        '의미<span class="cmdk-tab-n" data-cmdk-n="sem"></span></button>' +
      '<span class="cmdk-tab-key" aria-hidden="true">Tab 으로 바꾸기</span>' +
    '</div>' +
    '<ul class="cmdk-list" id="cmdk-list" role="listbox" aria-label="검색 결과"></ul>' +
    '<p class="cmdk-foot"><span data-cmdk-note></span>' +
      '<span class="cmdk-keys" aria-hidden="true" data-cmdk-keys></span></p>' +
  '</div>';

const box = root.querySelector(".cmdk-box");
const input = root.querySelector(".cmdk-input");
const tabs = root.querySelector(".cmdk-tabs");
const list = root.querySelector(".cmdk-list");
const note = root.querySelector("[data-cmdk-note]");
const keys = root.querySelector("[data-cmdk-keys]");
document.body.appendChild(root);

let result = search("");
let tab = "lex";
let active = 0;
let opener = null;
/* What a row that is not a link does, by its index. The ask row is the one:
 * choosing it puts the question to the index instead of leaving the page. */
let acts = [];

function shelfMarks(id) {
  const shelf = window.ProbeShelf;
  if (!shelf || !id) return "";
  const star = shelf.Stars.has(id)
    ? '<span class="cmdk-star" title="즐겨찾기" aria-label="즐겨찾기">' +
      shelf.STAR + "</span>" : "";
  const read = shelf.Reads.isDone(id)
    ? '<span class="cmdk-read" aria-label="읽음">읽음</span>' : "";
  return star + read;
}

function chips(pillars) {
  return pillars.map((k) =>
    '<span class="chip pillar" data-p="' + esc(k) + '">' + esc(k) + '</span>').join("");
}

/* Every choosable row goes through here, so the index `data-i` carries, the
 * id `aria-activedescendant` names and the place in `acts` stay one count. */
function option(cls, href, inner, act) {
  const i = acts.length;
  acts.push(act || null);
  return '<li role="presentation"><a class="cmdk-row' + (cls ? " " + cls : "") +
    '" role="option" id="cmdk-o-' + i + '" data-i="' + i + '" ' +
    'aria-selected="false" href="' + esc(href || "#") + '">' + inner + '</a></li>';
}

function line(text, cls) {
  return '<li class="' + (cls || "cmdk-none") + '" role="presentation">' + text + '</li>';
}

function docRow(row) {
  /* Which kind a row is rides on the left, beside the shelf marks, because
   * that is the column a narrow screen keeps — and where Enter lands is
   * the one thing about a row a reader has to know before pressing it. */
  const kind = row.kind === "comparison"
    ? '<span class="cmdk-kind">비교</span>' : "";
  return option("", row.href,
    '<span class="cmdk-marks">' + kind + shelfMarks(row.id) + '</span>' +
    '<span class="cmdk-main"><span class="cmdk-title">' + esc(row.title) + '</span>' +
    '<span class="cmdk-line">' + esc(row.tagline) + '</span></span>' +
    '<span class="cmdk-meta">' + chips(row.pillars) +
    '<span class="cmdk-id">' + esc(row.tail) + '</span></span>');
}

function askRow(q) {
  return option("cmdk-ask", "",
    '<span class="cmdk-marks"><span class="cmdk-hit">의미</span></span>' +
    '<span class="cmdk-main"><span class="cmdk-title">“' + esc(q) + '” 의 뜻으로 찾기</span>' +
    '<span class="cmdk-line">글자가 아니라 뜻이 가까운 대목을 찾습니다 · 몇 초 걸립니다</span></span>',
    () => ask(q));
}

/* A hit lands on the passage it matched, not on the paper: "the paper is
 * somewhere in here" is the answer the reader already had. The paper's own
 * row above its passages is the one link to the whole of it. Its axes come
 * from this index rather than the hit, so a chip says what the paper page
 * says even when the remote index was built from an older rewrite. */
function hitHref(hit) {
  return ROOT + hit.path + "index.html" + (hit.anchor ? "#" + hit.anchor : "");
}

function group(g) {
  const doc = PAPER.get(g.id);
  let html = option("cmdk-paper", ROOT + "p/" + g.id + "/index.html",
    '<span class="cmdk-marks">' + shelfMarks(g.id) + '</span>' +
    '<span class="cmdk-main"><span class="cmdk-title">' + esc(doc ? doc.title : g.id) + '</span></span>' +
    '<span class="cmdk-meta">' + chips(doc ? doc.pillars : []) +
    '<span class="cmdk-id">' + esc(g.id) + '</span></span>');
  for (const hit of g.hits.slice(0, PASSAGES)) {
    html += option("cmdk-sub", hitHref(hit),
      '<span class="cmdk-marks"><span class="cmdk-hit">' +
        esc(KINDS[hit.kind] || hit.kind) + '</span></span>' +
      '<span class="cmdk-main"><span class="cmdk-title">' + esc(readable(hit.title)) + '</span>' +
      // A caption is its own chunk and trims to nothing: no empty line under
      // a title that says it all.
      (hit.snippet ? '<span class="cmdk-line">' + esc(readable(hit.snippet)) + '</span>' : "") +
      '</span>');
  }
  return html;
}

/* What the question was read as. A search that silently rewrites itself
 * cannot be trusted, and a reader who sees "느려터진 → inference latency"
 * can tell a good answer from a misread one at a glance. */
function gist(terms) {
  if (!terms || !terms.length) return "";
  return line('<span class="cmdk-gist-h">읽은 뜻</span>' + terms.slice(0, 5).map(
    (t) => '<span class="cmdk-term">' + esc(t) + '</span>').join(""), "cmdk-gist");
}

function semPane(q) {
  if (sem.q !== q || sem.state === "idle") return askRow(q);
  if (sem.state === "wait")
    return line("“" + esc(q) + "” 에 가까운 대목을 찾는 중…", "cmdk-none cmdk-wait");
  if (sem.state === "fail")
    return line("의미 검색에 닿지 못했습니다. 글자 탭의 결과를 보세요.");
  const groups = byPaper(sem.data.hits);
  if (!groups.length) return line("뜻이 가까운 대목이 없습니다.");
  return gist(sem.data.expanded) + groups.map(group).join("");
}

function draw() {
  const q = input.value.trim();
  const offer = API && !result.all && q.length >= MIN;
  if (!offer) tab = "lex";
  acts = [];
  let html;
  if (tab === "sem") {
    html = semPane(q);
  } else {
    const rows = result.rows.slice(0, LIMIT);
    html = rows.length ? rows.map(docRow).join("")
      : offer ? "" : line("찾는 글이 없습니다. 제목의 한 단어나 arXiv id 로 다시 해보세요.");
    if (offer) html += askRow(q);
  }
  list.innerHTML = html;

  tabs.hidden = !offer;
  const answered = offer && sem.q === q && sem.state === "done";
  const semCount = answered ? byPaper(sem.data.hits).length + "편"
    : offer && sem.q === q && sem.state === "wait" ? "…" : "";
  if (offer) {
    tabs.querySelectorAll("[data-cmdk-tab]").forEach((b) =>
      b.setAttribute("aria-pressed", String(b.dataset.cmdkTab === tab)));
    tabs.querySelector('[data-cmdk-n="lex"]').textContent = result.rows.length + "편";
    tabs.querySelector('[data-cmdk-n="sem"]').textContent = semCount;
  }
  const count = result.rows.length;
  note.textContent = result.all
    ? "최근 " + count + "편"
    : (result.partial ? "일부만 일치 · " : "") + (API ? "글자 " : "") + count + "편" +
      (answered ? " · 의미 " + semCount : "");
  keys.textContent = "↑↓ 이동 · ↵ 열기" + (offer ? " · Tab 글자/의미" : "") + " · esc 닫기";
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
  // fastest way to the bottom of a short list — and to the ask row.
  active = (active + step + n) % n;
  paintActive();
}

function choose(el) {
  const act = acts[+el.dataset.i];
  if (act) { act(); input.focus(); return; }
  close();
  el.click();
}

function show(which) {
  if (tabs.hidden || which === tab) return;
  tab = which;
  active = 0;
  draw();
}

function typed() {
  const q = input.value.trim();
  result = search(q);
  active = 0;
  // A new question starts on the letters again; the old answer stays cached.
  if (sem.q !== q) { forget(); tab = "lex"; }
  draw();
}

function open() {
  if (!root.hidden) return;
  opener = document.activeElement;
  root.hidden = false;
  document.documentElement.classList.add("cmdk-on");
  input.value = "";
  typed();
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
input.addEventListener("input", typed);

root.addEventListener("click", (e) => {
  if (e.target.closest("[data-cmdk-dismiss]")) { close(); return; }
  const t = e.target.closest("[data-cmdk-tab]");
  if (t) { show(t.dataset.cmdkTab); input.focus(); return; }
  const row = e.target.closest(".cmdk-row");
  // A plain click on a link navigates on its own; the ask row has nowhere to
  // go, and a modified click is the reader's own business.
  if (!row) return;
  if (acts[+row.dataset.i]) { e.preventDefault(); choose(row); }
  else if (!e.metaKey && !e.ctrlKey && !e.shiftKey) close();
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
  // On a Korean keyboard the first Enter commits the syllable under the
  // cursor; taking that one would open a row for a half-written word.
  if (e.isComposing || e.keyCode === 229) return;
  if (e.key === "ArrowDown") { e.preventDefault(); move(1); }
  else if (e.key === "ArrowUp") { e.preventDefault(); move(-1); }
  else if (e.key === "Enter") {
    const row = rows()[active];
    if (row) { e.preventDefault(); choose(row); }
  } else if (e.key === "Escape") { e.preventDefault(); close(); }
  // Nothing inside is focusable but the box itself, so Tab has nowhere to go
  // that is not out of an open dialog — it moves between the two answers
  // instead, where there are two.
  else if (e.key === "Tab") {
    e.preventDefault();
    show(tab === "lex" ? "sem" : "lex");
    input.focus();
  }
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

// Which key the nav pill advertises — in its tooltip, its name and the key it
// prints beside the magnifier — is the one thing about it the build cannot
// know, so it prints the majority platform's and this corrects it for a Mac.
if (/Mac|iPhone|iPad/.test(navigator.platform || navigator.userAgent)) {
  document.querySelectorAll("[data-cmdk-open]").forEach((btn) => {
    btn.title = btn.title.replace("Ctrl K", "⌘K");
    const name = btn.getAttribute("aria-label");
    if (name) btn.setAttribute("aria-label", name.replace("Ctrl K", "⌘K"));
  });
  document.querySelectorAll("[data-cmdk-key]").forEach((k) => { k.textContent = "⌘K"; });
}

// A star or a 읽음 mark set on the page behind changes what a row should say.
document.addEventListener("probe:shelf-change", () => {
  if (!root.hidden) draw();
});
})();
