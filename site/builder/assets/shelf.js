/* 서재 층 — 즐겨찾기·읽음·책갈피·새 글, 메모와 같은 조건으로 저장된다.
 *
 * Scope of "local" is the memo layer's, and for the same reason: GitHub Pages
 * is static, so there is no account to hang a star on. Every mark here lives
 * in `localStorage` — this browser profile, on this device, for this origin —
 * so Chrome and Safari on one machine are two different shelves, a private
 * window is a third that empties itself, and clearing site data empties all of
 * them. The 내 서재 page's export is the only way one shelf reaches another
 * machine.
 *
 * 읽음 is the reader's claim, never the site's guess. Scroll depth is not
 * evidence of reading — a page scrolled to the end may have been skimmed,
 * searched, or scrolled past on the way to the references — and opening a page
 * is not evidence either. The button is the only thing that sets it, and
 * un-marking takes the record away again, so the store holds exactly the
 * papers the reader has said they are done with.
 *
 * Four stores in one file because they are one shelf seen from four sides —
 * 즐겨찾기 is what the reader picked out, 읽음 is what they are done with,
 * 책갈피 is where they stopped, and the corpus set is what they have already
 * been shown — and every surface that shows one shows another: a landing row,
 * a paper page, the hub.
 *
 * 책갈피 is placed by hand, in the table of contents rather than on the
 * headings themselves: the reading column already refuses a glyph that appears
 * under the cursor on every heading (`render.py`), and the contents are the
 * page's map — sticky, reachable from anywhere in the article, and the surface
 * a reader already looks at to answer "where am I".
 *
 * The file wires whatever markup it finds and needs no page to tell it which
 * page it is:
 *   [data-star="<id>"]      a toggle; gets its pressed state and glyph here
 *   [data-read-of="<id>"]   any element that wants `data-read` on it
 *   [data-paper-acts]       the paper header's controls, and 책갈피's context
 *   [data-resume]           the landing's one-line link back to the 책갈피
 * Landing, paper page and hub each load it and take what applies.
 */

(function () {
"use strict";

const STAR_KEY = "probe.stars.v1";
const READ_KEY = "probe.read.v1";
const MARK_KEY = "probe.mark.v1";
const CORPUS_KEY = "probe.corpus.v1";

function emit(name, detail) {
  document.dispatchEvent(new CustomEvent(name, { detail }));
}

function readMap(key) {
  try {
    const raw = localStorage.getItem(key);
    const val = raw ? JSON.parse(raw) : null;
    return val && typeof val === "object" && !Array.isArray(val) ? val : {};
  } catch (e) { return {}; }
}

function writeMap(key, map) {
  try {
    localStorage.setItem(key, JSON.stringify(map));
    return true;
  } catch (e) {
    // Never fail silently — a full quota must surface as something the reader
    // can act on, the way the memo layer's does.
    emit("probe:shelf-error", {
      reason: e && e.name === "QuotaExceededError" ? "quota" : "serialize",
    });
    return false;
  }
}

function now() { return new Date().toISOString(); }

/* ── 즐겨찾기 ──────────────────────────────────────────────────────────── */
/* `{ "<id>": { at, title } }`. The title is a fallback, not the truth: the hub
 * prefers the corpus index the build hands it, and falls back to this copy for
 * a paper that has since left the corpus — so a starred paper is still legible
 * after it stops being a page. */
const Stars = {
  all() { return readMap(STAR_KEY); },

  has(id) { return !!this.all()[id]; },

  /** Ids, most recently starred first. */
  list() {
    const map = this.all();
    return Object.keys(map).sort((a, b) =>
      (map[b].at || "").localeCompare(map[a].at || ""));
  },

  count() { return Object.keys(this.all()).length; },

  set(id, on, title) {
    const map = this.all();
    if (on) map[id] = { at: now(), title: title || (map[id] || {}).title || id };
    else delete map[id];
    if (!writeMap(STAR_KEY, map)) return this.has(id);
    emit("probe:shelf-change", { kind: "star", id, on });
    return on;
  },

  toggle(id, title) { return this.set(id, !this.has(id), title); },
};

/* ── 읽음 ──────────────────────────────────────────────────────────────── */
/* `{ "<id>": { at, title } }` — one fact, and a certain one: on this date, in
 * this browser, the reader said they were done with this paper. An id is in
 * the map or it is not, which is the whole of 읽음 / 안 읽음. */
const Reads = {
  all() { return readMap(READ_KEY); },

  get(id) { return this.all()[id] || null; },

  count() { return Object.keys(this.all()).length; },

  isDone(id) { return !!this.get(id); },

  /** Ids, most recently marked first. */
  list() {
    const map = this.all();
    return Object.keys(map).sort((a, b) =>
      (map[b].at || "").localeCompare(map[a].at || ""));
  },

  state(id) { return this.isDone(id) ? "done" : "none"; },

  label(id) { return this.isDone(id) ? "읽음" : "안 읽음"; },

  setDone(id, done, title) {
    const map = this.all();
    if (done) {
      const prev = map[id] || {};
      map[id] = { at: now(), title: title || prev.title || id };
    } else {
      // Un-marking removes the record rather than storing a false: "I have not
      // read this" is the absence of the claim, not a second kind of claim.
      delete map[id];
    }
    if (!writeMap(READ_KEY, map)) return this.isDone(id);
    emit("probe:shelf-change", { kind: "read", id });
    return done;
  },
};

/* ── 책갈피 ────────────────────────────────────────────────────────────── */
/* `{ "<id>": { anchor, label, title, at } }` — one per paper, because a second
 * mark in the same rewrite is a question ("which of these was I at?") the
 * feature exists to answer. Placing one over another replaces it; placing the
 * same one twice takes it back off. */
const Marks = {
  all() { return readMap(MARK_KEY); },

  get(id) { return this.all()[id] || null; },

  count() { return Object.keys(this.all()).length; },

  /** Ids, most recently marked first. */
  list() {
    const map = this.all();
    return Object.keys(map).sort((a, b) =>
      (map[b].at || "").localeCompare(map[a].at || ""));
  },

  /** The one the landing offers to take the reader back to. */
  latest() {
    const id = this.list()[0];
    return id ? { id, ...this.all()[id] } : null;
  },

  at(id, anchor) { const m = this.get(id); return !!m && m.anchor === anchor; },

  set(id, anchor, label, title) {
    const map = this.all();
    if (this.at(id, anchor)) delete map[id];
    else map[id] = { anchor, label: label || anchor, title: title || id, at: now() };
    if (!writeMap(MARK_KEY, map)) return this.get(id);
    emit("probe:shelf-change", { kind: "mark", id });
    return map[id] || null;
  },

  remove(id) {
    const map = this.all();
    delete map[id];
    if (!writeMap(MARK_KEY, map)) return;
    emit("probe:shelf-change", { kind: "mark", id });
  },
};

/* ── 새 글 ─────────────────────────────────────────────────────────────── */
/* Which papers this browser has already been shown, as a set of ids rather
 * than a last-visit timestamp. A clock gets this wrong in ways nobody can see:
 * read the same paper on a phone and the desktop still calls it new, publish
 * three at once and a single stamp cannot say which of them arrived after the
 * last look. Set difference cannot be wrong.
 *
 * `seeded` is what keeps the first visit quiet. Arriving at a 32-paper corpus
 * to be told all 32 are new is not news, so the first sight of the landing
 * records the whole corpus silently and the badge starts from the next one.
 */
const Corpus = {
  read() {
    const raw = readMap(CORPUS_KEY);
    return { seeded: !!raw.seeded, ids: Array.isArray(raw.ids) ? raw.ids : [] };
  },

  known() { return new Set(this.read().ids); },

  seeded() { return this.read().seeded; },

  isNew(id) { const r = this.read(); return r.seeded && !r.ids.includes(id); },

  save(ids, seeded) {
    if (!writeMap(CORPUS_KEY, { seeded, ids: [...ids], at: now() })) return;
    emit("probe:shelf-change", { kind: "corpus" });
  },

  /** Called by the landing, the one page that knows the whole corpus.
   *  Prunes ids that have left it, so the set stays the size of the site. */
  sync(corpusIds) {
    const r = this.read();
    const live = new Set(corpusIds);
    if (!r.seeded) { this.save(corpusIds, true); return; }
    const kept = r.ids.filter((id) => live.has(id));
    if (kept.length !== r.ids.length) this.save(kept, true);
  },

  /** Opening a paper is what takes its badge off. */
  mark(id) {
    const r = this.read();
    if (r.ids.includes(id)) return;
    this.save([...r.ids, id], r.seeded);
  },

  markAll(ids) {
    const r = this.read();
    this.save([...new Set([...r.ids, ...ids])], true);
  },
};

/* ── Painting whatever is on the page ─────────────────────────────────── */
function paint(root = document) {
  root.querySelectorAll("[data-star]").forEach((el) => {
    const on = Stars.has(el.dataset.star);
    el.setAttribute("aria-pressed", on ? "true" : "false");
    const glyph = el.querySelector("[data-star-glyph]");
    if (glyph) glyph.textContent = on ? "★" : "☆";
    const label = el.querySelector("[data-star-text]");
    if (label) label.textContent = on ? "즐겨찾기 됨" : "즐겨찾기";
  });
  root.querySelectorAll("[data-read-of]").forEach((el) => {
    const id = el.dataset.readOf;
    el.dataset.read = Reads.state(id);
    el.dataset.fresh = Corpus.isNew(id) ? "1" : "0";
  });
  paintResume(root);
}

/* The landing's one line back to wherever the reader stopped — the three most
 * recent marks as chips, and a door to the rest. Everything it prints came out
 * of the marks themselves, so it needs no corpus index to render.
 *
 * Built as elements rather than as a string: every part of a mark is text the
 * reader's own corpus put there, and text goes in through `textContent`, which
 * has no escaping to get wrong. */
const RESUME_CHIPS = 3;

function paintResume(root = document) {
  const strip = root.querySelector("[data-resume]");
  if (!strip) return;
  const box = strip.querySelector("[data-resume-chips]");
  const all = strip.querySelector("[data-resume-all]");
  const ids = Marks.list();
  if (!ids.length) {
    strip.hidden = true;
    if (box) box.textContent = "";
    return;
  }
  strip.hidden = false;
  const marks = Marks.all();
  if (box) {
    box.textContent = "";
    ids.slice(0, RESUME_CHIPS).forEach((id) => {
      const rec = marks[id];
      const chip = document.createElement("a");
      chip.className = "resume-chip";
      chip.href = `${strip.dataset.resume || ""}${id}/index.html#${rec.anchor}`;
      // The id is what fits; the title is what identifies. One is printed and
      // the other is a hover away.
      chip.title = rec.title || id;
      const num = document.createElement("b");
      num.textContent = id;
      const sec = document.createElement("span");
      sec.textContent = rec.label || "";
      chip.append(num, sec);
      box.append(chip);
    });
  }
  // The link is the door to 내 서재 either way; when marks are being left off
  // the strip it says how many, so the count is never silently dropped.
  if (all) {
    const rest = ids.length - RESUME_CHIPS;
    all.textContent = rest > 0 ? `외 ${rest}개 →` : "내 서재 →";
  }
}

// One listener for every star on the page, whichever page it is. The title
// rides on the button because the store keeps a fallback copy of it and the
// row is the only place that knows it.
document.addEventListener("click", (e) => {
  const btn = e.target.closest("[data-star]");
  if (!btn) return;
  Stars.toggle(btn.dataset.star, btn.dataset.starTitle || "");
});

document.addEventListener("probe:shelf-change", () => paint());

/* ── The paper page: the two buttons ──────────────────────────────────── */
const acts = document.querySelector("[data-paper-acts]");
if (acts) {
  const id = acts.dataset.paperId;
  const title = acts.dataset.paperTitle || id;
  const toggle = acts.querySelector("[data-read-toggle]");

  syncState();

  function syncState() {
    if (toggle) {
      const done = Reads.isDone(id);
      toggle.setAttribute("aria-pressed", done ? "true" : "false");
      toggle.textContent = done ? "읽음 해제" : "읽음으로 표시";
    }
  }

  if (toggle) {
    toggle.addEventListener("click", () => {
      Reads.setDone(id, !Reads.isDone(id), title);
      syncState();
    });
  }

  // Opening the paper is what takes its 새 글 badge off — the badge asks
  // "have you been shown this", and now the answer is yes.
  Corpus.mark(id);

  /* ── 책갈피, in the contents ───────────────────────────────────────── */
  // The buttons are built here rather than shipped by the build: a mark is
  // the reader's and the build has nothing to say about it, and a control
  // that cannot work without a script should not be in the page without one.
  const FLAG =
    '<svg viewBox="0 0 16 16" width="11" height="11" aria-hidden="true" ' +
    'focusable="false"><path d="M3.6 1.7h8.8v12.6L8 11.1l-4.4 3.2z"/></svg>';

  document.querySelectorAll(".toc .toc-row").forEach((row) => {
    const link = row.querySelector("a[href^='#']");
    if (!link) return;
    const anchor = link.getAttribute("href").slice(1);
    const label = (link.querySelector(".toc-k") || link).textContent.trim();
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "toc-mark";
    btn.dataset.markAt = anchor;
    btn.setAttribute("aria-pressed", "false");
    btn.setAttribute("aria-label", `${label} 에 책갈피`);
    btn.innerHTML = FLAG;
    btn.addEventListener("click", (e) => {
      // The row is a link with a button in its own column. A tap that lands on
      // the button must not also count as a tap on the row.
      e.preventDefault();
      e.stopPropagation();
      Marks.set(id, anchor, label, title);
    });
    row.appendChild(btn);
  });

  /* ── 책갈피, from wherever the reader is ─────────────────────────────── */
  // The contents are exact but they are also at the top of the article, and a
  // reader who stops reading is at the bottom of it. This marks the section on
  // screen, which is the one they mean, and it is the same store and the same
  // toggle — placing it twice takes it off.
  const fab = document.querySelector("[data-mark-fab]");
  const full = document.getElementById("p-full");
  let here = "", hereLabel = "";

  if (fab && full) {
    // A section heading carries its English keyword line inside it; the label
    // a 책갈피 shows is the Korean half, the same half the contents print.
    const headLabel = (h) => {
      const en = h.querySelector(".en");
      return (en ? h.textContent.replace(en.textContent, "") : h.textContent).trim();
    };
    const heads = [...full.querySelectorAll("h2.h-sec[id], h4.h-sub[id]")];
    if (heads[0]) { here = heads[0].id; hereLabel = headLabel(heads[0]); }

    if (heads.length && "IntersectionObserver" in window) {
      // The same band the memo layer anchors in, so the two features never
      // disagree about which section the reader is on.
      const obs = new IntersectionObserver((entries) => {
        entries.forEach((e) => {
          if (!e.isIntersecting) return;
          here = e.target.id;
          hereLabel = headLabel(e.target);
          paintMarks();
        });
      }, { rootMargin: "-70px 0px -75% 0px" });
      heads.forEach((h) => obs.observe(h));
    }

    fab.addEventListener("click", () => {
      if (here) Marks.set(id, here, hereLabel, title);
    });

    // 책갈피 is a place in 상세, so the button belongs to that surface only.
    // The tab strip swaps `hidden` on the panel; watching the attribute keeps
    // this independent of who does the swapping.
    const followSurface = () => { fab.hidden = full.hidden; };
    new MutationObserver(followSurface).observe(
      full, { attributes: true, attributeFilter: ["hidden"] });
    followSurface();
  }

  function paintMarks() {
    const mark = Marks.get(id);
    document.querySelectorAll(".toc-mark").forEach((btn) => {
      btn.setAttribute(
        "aria-pressed", mark && mark.anchor === btn.dataset.markAt ? "true" : "false");
    });
    if (fab) {
      const on = !!mark && mark.anchor === here;
      fab.setAttribute("aria-pressed", on ? "true" : "false");
      const label = on ? "이 자리의 책갈피 빼기" : "여기에 책갈피";
      fab.setAttribute("aria-label", label);
      fab.title = label;
    }
  }
  paintMarks();
  document.addEventListener("probe:shelf-change", paintMarks);
}

paint();

// No bundler, so the shared surface goes on `window` — the same door
// `window.ProbeMemo` uses.
window.ProbeShelf = { Stars, Reads, Marks, Corpus, paint };
})();
