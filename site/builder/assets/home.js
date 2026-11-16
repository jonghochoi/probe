/* 첫 화면 — the schedule against the reader's own date.
 *
 * The build prints each date's countdown as of the day it ran, and a page
 * can sit deployed for days after that. This counts again from today, drops
 * what has ended since, and drops the whole group once nothing is left. With
 * no script the build's own count stands.
 */
(function () {
"use strict";

const box = document.querySelector("[data-events]");
if (!box) return;
const pad = (n) => String(n).padStart(2, "0");
const now = new Date();
const today = `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())}`;
const day = (iso) => Date.UTC(+iso.slice(0, 4), +iso.slice(5, 7) - 1, +iso.slice(8, 10));

let left = 0;
box.querySelectorAll(".hm-ev").forEach((ev) => {
  if (ev.dataset.end < today) { ev.hidden = true; return; }
  left++;
  const n = Math.round((day(ev.dataset.start) - day(today)) / 864e5);
  const dd = ev.querySelector("[data-dday]");
  if (dd) dd.textContent = n <= 0 ? "진행 중" : `D-${n}`;
});
if (!left) box.hidden = true;
})();
