/* 내 서재 — the one page that shows everything this browser has kept.
 *
 * Three lists off two stores: `window.ProbeShelf` (즐겨찾기, 읽기 상태) and
 * `window.ProbeMemo` (메모). Nothing here can be server-rendered, because none
 * of it ever reaches the build — what the build does hand this page is the
 * corpus index in `[data-corpus-index]`, which is how a bare id becomes a title,
 * a tagline and a link. A kept id the index does not carry is a paper that has
 * left the corpus: it still lists, without a link, rather than vanishing.
 *
 * This page is also the export surface. A shelf that lives in one browser
 * profile moves to another only as a file, so the JSON here is the whole
 * envelope — memos, stars and 읽음 marks together — and importing it is how a
 * new machine starts where the old one stopped.
 */

(function () {
"use strict";

const memoApi = window.ProbeMemo;
const shelf = window.ProbeShelf;
const main = document.querySelector("[data-hub]");
if (!memoApi || !shelf || !main) return;

const { MemoStore, download } = memoApi;
const { Stars, Reads, Marks } = shelf;

const FLAG =
  '<svg viewBox="0 0 16 16" width="11" height="11" aria-hidden="true" ' +
  'focusable="false"><path d="M3.6 1.7h8.8v12.6L8 11.1l-4.4 3.2z"/></svg>';

const status = document.querySelector("[data-hub-status]");
const panels = {
  stars: main.querySelector('[data-shelf-panel="stars"]'),
  reads: main.querySelector('[data-shelf-panel="reads"]'),
  marks: main.querySelector('[data-shelf-panel="marks"]'),
  memos: main.querySelector('[data-shelf-panel="memos"]'),
};
const tabs = [...main.querySelectorAll("[data-shelf-tab]")];

/* The corpus, as much of it as a list row needs. */
const INDEX = (() => {
  const el = document.querySelector("[data-corpus-index]");
  const map = new Map();
  if (!el) return map;
  try {
    for (const paper of JSON.parse(el.textContent)) map.set(paper.id, paper);
  } catch (e) { /* an unreadable index costs titles, not the page */ }
  return map;
})();

function esc(s) {
  return String(s === undefined || s === null ? "" : s)
    .replace(/[&<>"]/g, (ch) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[ch]));
}

function titleOf(id, fallback) {
  const meta = INDEX.get(id);
  return (meta && meta.title) || fallback || id;
}

/* ── The three lists ──────────────────────────────────────────────────── */
function itemHtml(id, { title, when, whenLabel, state = true, hash = "", sub = "", lead = "" }) {
  const meta = INDEX.get(id);
  const name = titleOf(id, title);
  const second = sub || (meta && meta.tagline) || "";
  const inner = `<span class="shelf-title">${esc(name)}</span>` +
    (second ? `<span class="shelf-tagline">${esc(second)}</span>` : "");
  const link = meta
    ? `<a class="shelf-main" href="../p/${esc(id)}/index.html${esc(hash)}">${inner}</a>`
    : `<span class="shelf-main gone">${inner}` +
      `<span class="shelf-note">사이트에 없는 논문입니다</span></span>`;
  // Two, as on the landing list: a third wraps the column and makes the row
  // taller than its own title.
  const pillars = meta && meta.pillars
    ? meta.pillars.slice(0, 2)
        .map((p) => `<span class="chip pillar" data-p="${esc(p)}">${esc(p)}</span>`).join("")
    : "";
  const control = lead || `<button type="button" class="starbtn" data-star="${esc(id)}"
          data-star-title="${esc(name)}" aria-pressed="false"
          aria-label="즐겨찾기"><span data-star-glyph>☆</span></button>`;
  return `<article class="shelf-item" data-read-of="${esc(id)}">
  ${control}
  ${link}
  <span class="shelf-pillars">${pillars}</span>
  <span class="shelf-state">${state ? esc(Reads.label(id)) : ""}</span>
  <time class="shelf-when" datetime="${esc(when || "")}"
        title="${esc(whenLabel || "")}">${esc((when || "").slice(0, 10))}</time>
</article>`;
}

function renderStars() {
  const map = Stars.all();
  const ids = Stars.list();
  panels.stars.innerHTML = ids.length
    ? ids.map((id) => itemHtml(id, {
        title: map[id].title, when: map[id].at, whenLabel: "즐겨찾기에 담은 날",
      })).join("")
    : empty("아직 즐겨찾기가 없습니다. 논문 목록의 ☆ 나 논문 페이지의 즐겨찾기 버튼으로 담습니다.");
  return ids.length;
}

function renderReads() {
  const map = Reads.all();
  // Every id in the store is a paper the reader marked, so the state column
  // would say 읽음 on every row and tell nobody anything; the date says the
  // only thing that differs.
  const ids = Reads.list();
  panels.reads.innerHTML = ids.length
    ? ids.map((id) => itemHtml(id, {
        title: map[id].title, when: map[id].at,
        whenLabel: "읽음으로 표시한 날", state: false,
      })).join("")
    : empty("아직 읽음으로 표시한 논문이 없습니다. 논문 페이지 위쪽의 읽음 버튼으로 표시합니다.");
  return ids.length;
}

function renderMarks() {
  const map = Marks.all();
  const ids = Marks.list();
  panels.marks.innerHTML = ids.length
    ? ids.map((id) => itemHtml(id, {
        title: map[id].title, when: map[id].at, whenLabel: "책갈피를 꽂은 날",
        hash: `#${map[id].anchor}`, sub: `${map[id].label} 에서 멈춤`,
        lead: `<button type="button" class="markbtn" data-mark-drop="${esc(id)}"
          aria-label="책갈피 지우기" title="책갈피 지우기">${FLAG}</button>`,
      })).join("")
    : empty("아직 책갈피가 없습니다. 논문 상세 탭의 목차에서 섹션 옆 깃발을 눌러 꽂습니다.");
  return ids.length;
}

function renderMemos() {
  const memos = MemoStore.list().map((id) => MemoStore.load(id)).filter(Boolean);
  memos.sort((a, b) => (b.updatedAt || "").localeCompare(a.updatedAt || ""));
  panels.memos.innerHTML = memos.length
    ? memos.map((m) => `
    <article class="memo-card">
      <div class="memo-card-head">
        <a href="../p/${esc(m.paperId)}/index.html">${esc(titleOf(m.paperId, m.title))}</a>
        <time datetime="${esc(m.updatedAt || "")}">${esc((m.updatedAt || "").slice(0, 10))}</time>
      </div>
      <pre>${esc(m.body || "")}</pre>
      ${m.published ? `<span class="published">발행됨 · ${esc(m.published.at.slice(0, 10))}</span>` : ""}
    </article>`).join("")
    : empty("아직 메모가 없습니다. 논문 페이지 오른쪽 아래의 📝 버튼으로 남길 수 있습니다.");
  return memos.length;
}

function empty(text) {
  return `<p class="corpus-empty">${esc(text)}</p>`;
}

function render() {
  const counts = {
    stars: renderStars(), reads: renderReads(),
    marks: renderMarks(), memos: renderMemos(),
  };
  tabs.forEach((tab) => {
    const n = tab.querySelector("[data-tab-count]");
    if (n) n.textContent = counts[tab.dataset.shelfTab] || 0;
  });
  // The stores wrote the ids; the glyphs and the 읽음 marks are the shelf
  // layer's to fill, on this page as on every other.
  shelf.paint(main);
}

/* ── Tabs ─────────────────────────────────────────────────────────────── */
function showTab(key, push) {
  if (!panels[key]) key = "stars";
  tabs.forEach((tab) => {
    const on = tab.dataset.shelfTab === key;
    tab.setAttribute("aria-selected", on ? "true" : "false");
    panels[tab.dataset.shelfTab].hidden = !on;
  });
  if (push && history.replaceState) {
    history.replaceState(null, "", key === "stars" ? location.pathname : `#${key}`);
  }
}

tabs.forEach((tab) => {
  tab.addEventListener("click", () => showTab(tab.dataset.shelfTab, true));
});

/* ── Export / import ──────────────────────────────────────────────────── */
/* One envelope for the whole shelf. `v: 3` carries all four; an older file
 * carries fewer and still imports, since that is what a backup already sitting
 * in someone's downloads folder looks like. The 새 글 set is deliberately not
 * in here: it is a record of what one browser has been shown, and a browser
 * that has been shown nothing should start quiet rather than inherit someone
 * else's idea of new. */
function snapshot() {
  return JSON.stringify({
    v: 3,
    exportedAt: new Date().toISOString(),
    memos: MemoStore.list().map((id) => MemoStore.load(id)).filter(Boolean),
    stars: Stars.all(),
    reads: Reads.all(),
    marks: Marks.all(),
  }, null, 2);
}

function snapshotMd() {
  const starIds = Stars.list();
  const stars = starIds.length
    ? "## 즐겨찾기\n\n" + starIds.map((id) =>
        `- ${titleOf(id, Stars.all()[id].title)} (\`${id}\`) — ${Reads.label(id)}`).join("\n") + "\n"
    : "";
  const markIds = Marks.list();
  const marks = markIds.length
    ? "## 책갈피\n\n" + markIds.map((id) => {
        const m = Marks.all()[id];
        return `- ${titleOf(id, m.title)} (\`${id}\`) — ${m.label}`;
      }).join("\n") + "\n"
    : "";
  const memos = MemoStore.exportAll("md");
  return [stars, marks, memos].filter(Boolean).join("\n---\n\n");
}

function restore(text) {
  const data = JSON.parse(text);
  // merge:true — an import never overwrites what is already in this browser.
  // A draft lost to a stale export file is not recoverable.
  const memos = MemoStore.importJSON(text, { merge: true });

  let stars = 0;
  for (const [id, rec] of Object.entries(data.stars || {})) {
    if (Stars.has(id)) continue;
    Stars.set(id, true, rec && rec.title);
    stars++;
  }

  let reads = 0;
  for (const [id, rec] of Object.entries(data.reads || {})) {
    // Presence is the claim, except where the envelope carries a `done` flag:
    // an entry marked `done: false` is a paper that was opened and not read,
    // and opening one is not reading it.
    if (!rec || rec.done === false) continue;
    if (Reads.isDone(id)) continue;
    Reads.setDone(id, true, rec.title);
    reads++;
  }
  let marks = 0;
  for (const [id, rec] of Object.entries(data.marks || {})) {
    if (!rec || !rec.anchor || Marks.get(id)) continue;
    Marks.set(id, rec.anchor, rec.label, rec.title);
    marks++;
  }

  return { memos, stars, reads, marks };
}

document.addEventListener("click", (e) => {
  const btn = e.target.closest("[data-hub-action]");
  if (!btn) return;
  const today = new Date().toISOString().slice(0, 10);
  if (btn.dataset.hubAction === "export-json") {
    download(`probe-shelf-${today}.json`, snapshot());
  } else if (btn.dataset.hubAction === "export-md") {
    download(`probe-shelf-${today}.md`, snapshotMd(), "text/markdown");
  }
});

const file = document.querySelector("[data-hub-import]");
if (file) {
  file.addEventListener("change", () => {
    const f = file.files && file.files[0];
    if (!f) return;
    f.text().then((text) => {
      try {
        const n = restore(text);
        if (status) {
          status.textContent =
            `메모 ${n.memos} · 즐겨찾기 ${n.stars} · 읽음 ${n.reads} · ` +
            `책갈피 ${n.marks} 가져옴 (기존 기록은 유지)`;
        }
        render();
      } catch (err) {
        if (status) status.textContent = "가져오기 실패 — JSON 형식이 아닙니다";
      }
      file.value = "";
    });
  });
}

document.addEventListener("click", (e) => {
  const drop = e.target.closest("[data-mark-drop]");
  if (drop) Marks.remove(drop.dataset.markDrop);
});

document.addEventListener("probe:shelf-change", render);
document.addEventListener("probe:shelf-error", (e) => {
  if (status) {
    status.textContent = e.detail.reason === "quota"
      ? "저장 공간이 가득 찼습니다 — 내보내고 정리해 주세요"
      : "저장에 실패했습니다";
  }
});

render();
showTab((location.hash || "").slice(1) || "stars", false);
addEventListener("hashchange", () => showTab((location.hash || "").slice(1) || "stars", false));
})();
