/* Memo layer — localStorage draft + publish to GitHub Discussions.
 *
 * Scope of "local": the browser you are looking at right now. GitHub Pages is
 * static, so there is no server to hold a memo; a draft lives in this browser
 * profile on this device only, and is lost if you clear site data. The publish
 * button is the durable path — it moves the memo into the repository, where it
 * syncs across devices and can be read back.
 *
 * Note on giscus: its comment box is a cross-origin iframe and cannot be
 * filled programmatically. Publishing therefore goes through a prefilled
 * `discussions/new` URL, which actually works — giscus stays a read-only
 * enhancement, loaded only on demand.
 */

(function () {
"use strict";

const KEY = (id) => `probe.memo.v1.${id}`;
const INDEX_KEY = "probe.memo.index.v1";
const DEBOUNCE_MS = 800;
const BODY_LIMIT = 6000;

const MemoStore = {
  load(id) {
    try {
      const raw = localStorage.getItem(KEY(id));
      return raw ? JSON.parse(raw) : null;
    } catch (e) { return null; }
  },

  save(id, patch) {
    const prev = this.load(id) || { v: 1, paperId: id, body: "", published: null };
    const next = { ...prev, ...patch, v: 1, paperId: id, updatedAt: new Date().toISOString() };
    try {
      if (!next.body || !next.body.trim()) {
        this.remove(id);
        return next;
      }
      localStorage.setItem(KEY(id), JSON.stringify(next));
      const idx = this.list();
      if (!idx.includes(id)) localStorage.setItem(INDEX_KEY, JSON.stringify([...idx, id]));
      emit("probe:memo-saved", { id, updatedAt: next.updatedAt });
    } catch (e) {
      // Never fail silently — a quota error must become a visible CTA.
      emit("probe:memo-error", { id, reason: e && e.name === "QuotaExceededError" ? "quota" : "serialize" });
    }
    return next;
  },

  list() {
    try { return JSON.parse(localStorage.getItem(INDEX_KEY) || "[]"); }
    catch (e) { return []; }
  },

  remove(id) {
    try {
      localStorage.removeItem(KEY(id));
      localStorage.setItem(INDEX_KEY, JSON.stringify(this.list().filter((x) => x !== id)));
      emit("probe:memo-cleared", { id });
    } catch (e) {}
  },

  exportAll(format = "json") {
    const memos = this.list().map((id) => this.load(id)).filter(Boolean);
    if (format === "json") {
      return JSON.stringify({ v: 1, exportedAt: new Date().toISOString(), memos }, null, 2);
    }
    return memos.map((m) =>
      `## ${m.title || m.paperId}\n\`analysis/${m.paperId}.md\` · ${m.updatedAt.slice(0, 10)}\n\n${m.body}\n`
    ).join("\n---\n\n");
  },

  importJSON(text, { merge = true } = {}) {
    const data = JSON.parse(text);
    let n = 0;
    for (const m of data.memos || []) {
      if (!m.paperId) continue;
      if (!merge || !this.load(m.paperId)) { this.save(m.paperId, m); n++; }
    }
    return n;
  },
};

function emit(name, detail) {
  document.dispatchEvent(new CustomEvent(name, { detail }));
}

function download(filename, text, type = "application/json") {
  const url = URL.createObjectURL(new Blob([text], { type }));
  const a = document.createElement("a");
  a.href = url; a.download = filename;
  document.body.appendChild(a); a.click(); a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

/* ── Panel wiring ─────────────────────────────────────────────────────── */
const root = document.querySelector("[data-memo-root]");
if (root) {
  const id = root.dataset.paperId;
  const title = root.dataset.paperTitle || id;
  const input = root.querySelector("[data-memo-input]");
  const status = root.querySelector("[data-memo-status]");
  const anchorEl = root.querySelector("[data-memo-anchor]");
  const fab = document.querySelector("[data-memo-fab]");
  const scrim = document.querySelector("[data-scrim]");
  let timer = null;
  let anchor = "";

  const stored = MemoStore.load(id);
  if (stored) {
    input.value = stored.body || "";
    anchor = stored.anchor || "";
    setStatus(`저장됨 · ${stored.updatedAt.slice(0, 10)}`);
    showAnchor();
  }
  refreshFab();

  function setStatus(text) { if (status) status.textContent = text; }

  function refreshFab() {
    if (!fab) return;
    const has = !!(input.value && input.value.trim());
    fab.dataset.hasMemo = has ? "1" : "0";
    const c = fab.querySelector(".count");
    if (c) c.textContent = has ? "1" : "";
  }

  function showAnchor() {
    if (!anchorEl) return;
    if (!anchor) { anchorEl.hidden = true; return; }
    const el = document.getElementById(anchor);
    const label = el ? el.textContent.trim() : anchor;
    anchorEl.hidden = false;
    anchorEl.innerHTML = `📍 <a href="#${anchor}">${label}</a> 을(를) 읽던 중`;
  }

  function flush() {
    if (timer) { clearTimeout(timer); timer = null; }
    MemoStore.save(id, { body: input.value, title, anchor });
    refreshFab();
  }


  input.addEventListener("input", () => {
    setStatus("입력 중…");
    if (timer) clearTimeout(timer);
    timer = setTimeout(() => { flush(); setStatus("저장됨"); }, DEBOUNCE_MS);
    refreshFab();
  });

  // A fast tab-close must not lose a draft.
  addEventListener("visibilitychange", () => { if (document.visibilityState === "hidden") flush(); });
  addEventListener("beforeunload", flush);

  // Freeze the section the reader was on when they start writing. Two levels,
  // section and sub-point — an act is a divider band, not a heading, so it has
  // no id to anchor to. (`h3` was the section tag before the spine changed.)
  const heads = () => [...document.querySelectorAll('.article h2.h-sec, .article h4.h-sub[id]')];
  let topmost = "";
  const obs = new IntersectionObserver((entries) => {
    entries.forEach((e) => { if (e.isIntersecting) topmost = e.target.id; });
  }, { rootMargin: "-70px 0px -75% 0px" });
  const observeHeads = () => heads().forEach((h) => obs.observe(h));
  observeHeads();

  input.addEventListener("focus", () => {
    if (!anchor && topmost) { anchor = topmost; showAnchor(); }
  });

  /* Open / close */
  function open(v) {
    root.dataset.open = v ? "1" : "0";
    if (scrim) scrim.dataset.open = v ? "1" : "0";
    if (v) input.focus();
  }
  if (fab) fab.addEventListener("click", () => open(root.dataset.open !== "1"));
  if (scrim) scrim.addEventListener("click", () => open(false));
  addEventListener("keydown", (e) => { if (e.key === "Escape") open(false); });

  /* Actions */
  root.querySelectorAll("[data-memo-action]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const action = btn.dataset.memoAction;
      if (action === "publish") return publish();
      if (action === "export") {
        return download(`probe-memo-${id}.md`, MemoStore.exportAll("md"), "text/markdown");
      }
      if (action === "clear") {
        if (!confirm("이 논문의 메모를 삭제할까요? 되돌릴 수 없습니다.")) return;
        input.value = ""; anchor = ""; showAnchor();
        MemoStore.remove(id); refreshFab(); setStatus("삭제됨");
      }
    });
  });

  function publish() {
    flush();
    const body = buildBody();
    const base = root.dataset.discussionsNew;
    if (!base) return;
    const url = new URL(base);
    url.searchParams.set("title", `[${id}] ${title}`);
    if (body.length <= BODY_LIMIT) {
      url.searchParams.set("body", body);
      window.open(url.toString(), "_blank", "noopener");
    } else {
      navigator.clipboard.writeText(body).then(
        () => { setStatus("메모가 길어 클립보드에 복사했습니다 — 붙여넣기 하세요"); },
        () => { setStatus("클립보드 복사 실패 — 수동 복사가 필요합니다"); }
      );
      window.open(url.toString(), "_blank", "noopener");
    }
    MemoStore.save(id, { published: { url: url.toString(), at: new Date().toISOString() } });
  }

  function buildBody() {
    const link = root.dataset.paperUrl || "";
    const where = anchor ? `\n읽던 위치: \`#${anchor}\`` : "";
    return `> ${title}\n> ${link}${where}\n\n${input.value}`;
  }

  document.addEventListener("probe:memo-error", (e) => {
    if (e.detail.reason === "quota") {
      setStatus("저장 공간이 가득 찼습니다 — 내보내고 정리해 주세요");
    } else {
      setStatus("저장에 실패했습니다");
    }
  });
}

// The memos hub page reuses the store; no bundler, so it goes on window.
window.ProbeMemo = { MemoStore, download };
})();
