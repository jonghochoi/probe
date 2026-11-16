/* 탐색 — the detail drawer, its tabs, the calendar and the date line.
 *
 * The page is complete without this: the date line and the calendar are
 * links, and every paper's detail stands at the page's foot with a card's
 * link a jump to it. What the script adds is reading a paper without leaving
 * the list — its detail opens in a drawer from the side (a sheet from below
 * on a phone) with its four parts as tabs — and a calendar that shows one
 * month at a time.
 */

(function () {
"use strict";

const root = document.querySelector("[data-scout]");
if (!root) return;

/* ── The drawer ───────────────────────────────────────────────────────── */
const dw = document.createElement("div");
dw.className = "sd-dw"; dw.hidden = true;
dw.innerHTML = '<div class="sd-bg" data-sd-close></div>'
  + '<section class="sd-p" role="dialog" aria-modal="true"></section>';
document.body.appendChild(dw);
const panel = dw.querySelector(".sd-p");
const X = '<svg viewBox="0 0 16 16" width="14" height="14" fill="none" stroke="currentColor" '
  + 'stroke-width="1.8" stroke-linecap="round" aria-hidden="true"><path d="m4 4 8 8M12 4l-8 8"/></svg>';
let host = null, back = null;

function close() {
  if (dw.hidden) return;
  dw.hidden = true; panel.innerHTML = "";
  document.documentElement.classList.remove("sd-on");
  if (host) host.classList.remove("is-open");
  if (location.hash.startsWith("#p-")) history.replaceState(null, "", location.pathname + location.search);
  if (back) back.focus({ preventScroll: true });
  host = back = null;
}

function open(id, from) {
  const src = document.getElementById("p-" + id);
  if (!src) return;
  close();
  // A copy, so the column the script hid keeps its articles and the ids stay
  // unique; the copy's own id goes.
  const art = src.cloneNode(true);
  art.removeAttribute("id");
  const top = art.querySelector(".sd-top");
  top.insertAdjacentHTML("beforeend",
    `<button type="button" class="sd-x" data-sd-close aria-label="닫기">${X}</button>`);
  art.querySelectorAll("[data-dx-pane]").forEach((p, i) => { p.hidden = i > 0; });
  panel.appendChild(art);
  panel.setAttribute("aria-label", (art.querySelector("h2") || {}).textContent || "");
  panel.scrollTop = 0;
  dw.hidden = false;
  document.documentElement.classList.add("sd-on");
  host = root.querySelector(`[data-open="${CSS.escape(id)}"]`);
  if (host) host.classList.add("is-open");
  back = from || null;
  history.replaceState(null, "", "#p-" + id);
  panel.querySelector(".sd-x").focus({ preventScroll: true });
}

/* ── The calendar ─────────────────────────────────────────────────────── */
/* One month at a time, starting on the run's own; ‹ goes back in time. The
 * months are printed newest first, so "back" is the next one down. */
const cal = root.querySelector("[data-scout-cal]");
const months = cal ? [...cal.querySelectorAll(".sn-month")] : [];
let shown = Math.max(0, months.findIndex((m) => m.dataset.month === cal.querySelector(".sn-cal").dataset.here));
function showMonth(i) {
  shown = Math.min(Math.max(i, 0), months.length - 1);
  months.forEach((m, k) => {
    m.hidden = k !== shown;
    const [older, newer] = m.querySelectorAll("[data-cal]");
    older.disabled = k === months.length - 1;
    newer.disabled = k === 0;
  });
}
if (months.length) showMonth(shown);

/* ── The date line ────────────────────────────────────────────────────── */
/* On a phone it scrolls sideways: the run on screen is brought into view,
 * and the edge fades while more of the line is off to the right. */
const line = root.querySelector(".sn-dline");
const items = line && line.querySelector("[data-pline]");
if (items) {
  const on = items.querySelector('[aria-current="page"]');
  if (on && items.scrollWidth > items.clientWidth)
    items.scrollLeft = Math.max(0, on.offsetLeft - items.clientWidth / 2 + on.offsetWidth / 2);
  const edge = () => line.classList.toggle("at-end",
    items.scrollLeft + items.clientWidth >= items.scrollWidth - 4);
  items.addEventListener("scroll", edge, { passive: true });
  addEventListener("resize", edge);
  edge();
}

/* ── Clicks ───────────────────────────────────────────────────────────── */
document.addEventListener("click", (e) => {
  if (e.target.closest("[data-sd-close]")) { close(); return; }
  const tab = e.target.closest("[data-dx-tab]");
  if (tab) {
    const box = tab.closest(".dx");
    box.querySelectorAll("[data-dx-tab]").forEach((b) => b.setAttribute("aria-selected", String(b === tab)));
    box.querySelectorAll("[data-dx-pane]").forEach((p) => { p.hidden = p.dataset.dxPane !== tab.dataset.dxTab; });
    return;
  }
  const step = e.target.closest("[data-cal]");
  if (step) { showMonth(shown + Number(step.dataset.cal)); return; }
  // A click outside the open calendar closes it.
  if (cal && cal.open && !e.target.closest("[data-scout-cal]")) cal.open = false;
  if (!root.contains(e.target)) return;
  const link = e.target.closest("[data-detail]");
  if (link) { e.preventDefault(); open(link.dataset.detail, link); return; }
  // The whole card or row opens the detail; its arXiv id still goes out.
  const card = e.target.closest("[data-open]");
  if (card && !e.target.closest("a, button")) open(card.dataset.open, card.querySelector("[data-detail]"));
});

document.addEventListener("keydown", (e) => {
  if (e.key !== "Escape") return;
  if (!dw.hidden) close();
  else if (cal && cal.open) { cal.open = false; cal.querySelector("summary").focus(); }
});

// An address that names a paper opens it, so a shared link lands on the detail.
if (location.hash.startsWith("#p-")) open(decodeURIComponent(location.hash.slice(3)));
})();
