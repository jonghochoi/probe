/* Memo hub — reads the same localStorage store the paper panels write to.
 *
 * Loaded after memo.js, which puts the store on `window.ProbeMemo`. Nothing
 * here can come from the build: the memos never leave the reader's browser.
 */

(function () {
"use strict";

const api = window.ProbeMemo;
const list = document.querySelector("[data-hub-list]");
if (!api || !list) return;

const { MemoStore, download } = api;
const empty = document.querySelector("[data-hub-empty]");
const status = document.querySelector("[data-hub-status]");

function esc(s) {
  return String(s).replace(/[&<>"]/g, (ch) =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[ch]));
}

function render() {
  const memos = MemoStore.list().map((id) => MemoStore.load(id)).filter(Boolean);
  memos.sort((a, b) => (b.updatedAt || "").localeCompare(a.updatedAt || ""));

  list.innerHTML = memos.map((m) => `
    <article class="memo-card">
      <div class="memo-card-head">
        <a href="../p/${esc(m.paperId)}/index.html">${esc(m.title || m.paperId)}</a>
        <time datetime="${esc(m.updatedAt || "")}">${esc((m.updatedAt || "").slice(0, 10))}</time>
      </div>
      <pre>${esc(m.body || "")}</pre>
      ${m.published ? `<span class="published">발행됨 · ${esc(m.published.at.slice(0, 10))}</span>` : ""}
    </article>`).join("");

  if (empty) empty.hidden = memos.length > 0;
  if (status) status.textContent = memos.length ? `${memos.length}개` : "";
}

document.addEventListener("click", (e) => {
  const btn = e.target.closest("[data-hub]");
  if (!btn) return;
  const today = new Date().toISOString().slice(0, 10);
  if (btn.dataset.hub === "export-json") {
    download(`probe-memos-${today}.json`, MemoStore.exportAll("json"));
  } else if (btn.dataset.hub === "export-md") {
    download(`probe-memos-${today}.md`, MemoStore.exportAll("md"), "text/markdown");
  }
});

const file = document.querySelector("[data-hub-import]");
if (file) {
  file.addEventListener("change", () => {
    const f = file.files && file.files[0];
    if (!f) return;
    f.text().then((text) => {
      try {
        // merge:true — an import never overwrites a memo already in this
        // browser. Losing a draft to a stale export file is not recoverable.
        const n = MemoStore.importJSON(text, { merge: true });
        if (status) status.textContent = `${n}개 가져옴 (기존 메모는 유지)`;
        render();
      } catch (err) {
        if (status) status.textContent = "가져오기 실패 — JSON 형식이 아닙니다";
      }
      file.value = "";
    });
  });
}

render();
})();
