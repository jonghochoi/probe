/* 서재 — the one page that shows everything this browser has kept.
 *
 * Three lists off two stores: `window.ProbeShelf` (즐겨찾기, 책갈피, and the
 * 읽음 mark each row states) and `window.ProbeMemo` (메모). Nothing here can
 * be server-rendered, because none of it ever reaches the build — what the
 * build does hand this page is `window.ProbeIndex`, which is how a bare id
 * becomes a title, a tagline and a link. A kept id the index does not carry
 * is a paper that has left the corpus: it still lists, without a link, rather
 * than vanishing.
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
  marks: main.querySelector('[data-shelf-panel="marks"]'),
  memos: main.querySelector('[data-shelf-panel="memos"]'),
};
const tabs = [...main.querySelectorAll("[data-shelf-tab]")];

/* The corpus, as much of it as a list row needs — `assets/corpus-index.js`,
 * the same file the ⌘K palette searches. A missing index costs titles and
 * taglines, not the page: every row still lists under its id. */
const INDEX = (() => {
  const map = new Map();
  const data = window.ProbeIndex;
  if (!data || !Array.isArray(data.papers)) return map;
  for (const paper of data.papers) map.set(paper.id, paper);
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

/* ── The three tables ─────────────────────────────────────────────────── */
/* Each kind is the analysis list's table: when it was kept, the arXiv id, the
 * title over a second line that says what was kept, and a trailing column.
 * A paper this browser marked 읽음 says so at its title's end. */
const HEAD = {
  stars: ["저장", "arXiv", "논문 · 한 줄", "연구 축"],
  marks: ["저장", "arXiv", "논문 · 책갈피 자리", "연구 축"],
  memos: ["고침", "arXiv", "논문 · 메모", "상태"],
};

function rowHtml(id, { when, hash = "", sub = "", subCls = "", end }) {
  const meta = INDEX.get(id);
  const title = `<span class="tl-t">${esc(titleOf(id))}` +
    (Reads.isDone(id) ? '<span class="sh-tag">읽음</span>' : "") + "</span>";
  const second = sub ? `<span class="tl-g${subCls}">${sub}</span>` : "";
  const main = meta
    ? `<a class="tl-main" href="../p/${esc(id)}/index.html${esc(hash)}">${title}${second}</a>`
    : `<span class="tl-main gone">${title}${second}` +
      `<span class="sh-note">사이트에 없는 논문입니다</span></span>`;
  // The index carries the axes the paper is filed under and nothing else
  // (`Paper.filed`), so this prints what it is handed — the same pair the
  // analysis list's row and the palette print.
  const pillars = meta && meta.pillars
    ? meta.pillars.map((p) => `<span class="chip pillar" data-p="${esc(p)}">${esc(p)}</span>`).join("")
    : "";
  return `<li class="tl-row" data-read-of="${esc(id)}">` +
    `<time class="tl-id" datetime="${esc(when || "")}">${esc((when || "").slice(5, 10).replace("-", "."))}</time>` +
    `<a class="tl-id sh-id" href="https://arxiv.org/abs/${esc(id)}" target="_blank" rel="noopener" title="arXiv 초록">${esc(id)}</a>` +
    `${main}<span class="tl-p">${end === undefined ? pillars : end}</span></li>`;
}

function table(kind, rows) {
  return `<div class="tl-head" aria-hidden="true">${HEAD[kind].map((h) => `<span>${h}</span>`).join("")}</div>` +
    `<ul class="tl">${rows.join("")}</ul>`;
}

function renderStars() {
  const map = Stars.all();
  const ids = Stars.list();
  panels.stars.innerHTML = ids.length
    ? table("stars", ids.map((id) => {
        const meta = INDEX.get(id);
        return rowHtml(id, { when: map[id].at, sub: esc((meta && meta.tagline) || "") });
      }))
    : empty("아직 즐겨찾기한 논문이 없습니다. 분석 목록의 별이나 논문 페이지의 즐겨찾기 버튼을 누르면 여기에 모입니다.");
  return ids.length;
}

function renderMarks() {
  const map = Marks.all();
  const ids = Marks.list();
  panels.marks.innerHTML = ids.length
    ? table("marks", ids.map((id) => rowHtml(id, {
        when: map[id].at, hash: `#${map[id].anchor}`,
        sub: `<span class="sh-mk">${FLAG}${esc(map[id].label)}</span>`,
      })))
    : empty("아직 책갈피가 없습니다. 논문 상세 탭의 목차에서 섹션 옆 깃발을 누르면 여기에 남습니다.");
  return ids.length;
}

function renderMemos() {
  const memos = MemoStore.list().map((id) => MemoStore.load(id)).filter(Boolean);
  memos.sort((a, b) => (b.updatedAt || "").localeCompare(a.updatedAt || ""));
  panels.memos.innerHTML = memos.length
    ? table("memos", memos.map((m) => rowHtml(m.paperId, {
        when: m.updatedAt, sub: esc(m.body || ""), subCls: " sh-memo",
        end: m.published
          ? `<span class="sh-tag is-pub" title="${esc(m.published.at.slice(0, 10))}">게시됨</span>`
          : '<span class="sh-tag">초안</span>',
      })))
    : empty("아직 메모가 없습니다. 논문 페이지 오른쪽 아래의 메모 버튼으로 남기면 여기에 모입니다.");
  return memos.length;
}

function empty(text) {
  return `<p class="sh-empty">${esc(text)}</p>`;
}

function render() {
  const counts = {
    stars: renderStars(), marks: renderMarks(), memos: renderMemos(),
  };
  tabs.forEach((tab) => {
    const n = tab.querySelector("[data-tab-count]");
    if (n) n.textContent = counts[tab.dataset.shelfTab] || 0;
  });
  // The build prints both exports closed, because an empty shelf has nothing
  // to write out and a file that downloads with nothing in it reports a
  // success that did not happen. Any one store holding something opens both:
  // the JSON is the whole envelope — 읽음 marks included, though no tab lists
  // them — and the Markdown prints every list it finds, so neither is tied to
  // the tab that happens to be showing.
  const kept = counts.stars + Reads.count() + counts.marks + counts.memos;
  for (const btn of main.querySelectorAll("[data-hub-action]")) btn.disabled = !kept;
  shelf.paint(main);
}

/* ── The ⋯ menu ───────────────────────────────────────────────────────── */
const moreBtn = main.querySelector("[data-hub-more]");
const menu = main.querySelector("[data-hub-menu]");
function openMenu(on) {
  if (!menu) return;
  menu.hidden = !on;
  moreBtn.setAttribute("aria-expanded", String(on));
}
document.addEventListener("click", (e) => {
  if (!menu) return;
  if (e.target.closest("[data-hub-more]")) { openMenu(menu.hidden); return; }
  // A pick closes it, and so does a click anywhere else. The import label
  // stays open until the file dialog it opens has answered.
  if (e.target.closest("[data-hub-action]") || !e.target.closest("[data-hub-menu]")) openMenu(false);
});
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape" && menu && !menu.hidden) { openMenu(false); moreBtn.focus(); }
});

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
  let name = "";
  if (btn.dataset.hubAction === "export-json") {
    name = `probe-shelf-${today}.json`;
    download(name, snapshot());
  } else if (btn.dataset.hubAction === "export-md") {
    name = `probe-shelf-${today}.md`;
    download(name, snapshotMd(), "text/markdown");
  } else {
    return;
  }
  // Writing a file is over the moment it is written — the button holds no
  // state and should not look as though it does. A pointer press leaves it
  // focused, the browser's own download UI takes the page's focus and hands it
  // back to whatever held it, and the ring returns on a button nobody is
  // pressing. Only a pointer press is dropped: `detail` is 0 when the keyboard
  // activated the button, and a reader moving by Tab would lose their place in
  // the page rather than a ring they did not want.
  if (e.detail) btn.blur();
  // What a download did is otherwise invisible — the file lands somewhere this
  // page cannot see. The line that reports an import reports this too.
  if (status) status.textContent = `${name} 내보냄`;
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
      openMenu(false);
    });
  });
}

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
