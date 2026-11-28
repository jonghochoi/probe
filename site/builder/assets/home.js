/* 첫 화면 — the schedule against the reader's own date, and what the mascot
 * wears.
 *
 * The build prints each date's countdown as of the day it ran, and a page
 * can sit deployed for days after that. This counts again from today, drops
 * what has ended since, and drops the whole group once nothing is left. With
 * no script the build's own count stands.
 *
 * The mascot reads the same day. One costume answers the first thing that
 * holds, in this order: a followed deadline three days out or nearer, a
 * scouting run this browser has not yet been shown, the reader's hour
 * between 23 and 6, a rewrite or comparison this browser has not yet
 * celebrated. When none holds it has nothing to report, and walks the four
 * tracks' costumes instead, one every few seconds, each with that track's
 * newest line. A reader who asked for less motion gets the costume and no
 * walk. With no script it stays the plain mark saying where to start.
 *
 * Both news costumes are counted per browser, because the corpus grows
 * almost daily and runs land twice a week, so anything "from today or
 * yesterday" would be on most visits. What the costume was worn for is kept
 * once it has shown — the run's date (`data-run`) under `probe.home.run.v1`,
 * the newest piece's path (`data-new-key`) under `probe.home.seen.v1`. A
 * browser with nothing kept yet is shown only a run from today or yesterday
 * and a piece from today, and keeps the current value either way so the
 * next one counts from there. A costume that outranks a news costume leaves
 * its value unkept, so the news waits for a quieter visit rather than being
 * spent behind a deadline.
 *
 * The first screen settles in as it opens once a session; this marks the
 * session (`probe.home.entered`, sessionStorage) so the head's boot script
 * opens it still on the next visit.
 */
(function () {
"use strict";

try { sessionStorage.setItem("probe.home.entered", "1"); } catch (e) { /* every visit animates */ }

const pad = (n) => String(n).padStart(2, "0");
const now = new Date();
const today = `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())}`;
const day = (iso) => Date.UTC(+iso.slice(0, 4), +iso.slice(5, 7) - 1, +iso.slice(8, 10));
const until = (iso) => Math.round((day(iso) - day(today)) / 864e5);

const box = document.querySelector("[data-events]");
if (box) {
  let left = 0;
  box.querySelectorAll(".hm-ev").forEach((ev) => {
    if (ev.dataset.end < today) { ev.hidden = true; return; }
    left++;
    const n = until(ev.dataset.start);
    const dd = ev.querySelector("[data-dday]");
    if (dd) dd.textContent = n <= 0 ? "진행 중" : `D-${n}`;
  });
  if (!left) box.hidden = true;
}

const host = document.querySelector("[data-mascot]");
const mark = host && host.querySelector(".probe-mark");
if (!mark) return;
const bubble = host.querySelector(".hm-bubble");
const lines = {};
host.querySelectorAll("[data-say]").forEach((s) => { lines[s.dataset.say] = s; });
const still = matchMedia("(prefers-reduced-motion: reduce)").matches;

function wear(costume, line, swap) {
  const show = () => {
    Object.keys(lines).forEach((k) => { lines[k].hidden = k !== line; });
    bubble.classList.remove("is-swap");
  };
  mark.dataset.w = costume;
  if (!swap || still) { show(); return; }
  mark.classList.remove("w-on");
  void mark.getBoundingClientRect();
  mark.classList.add("w-on");
  bubble.classList.add("is-swap");
  setTimeout(show, 200);
}

const recent = (iso) => iso && until(iso) >= -1 && until(iso) <= 0;
const hour = now.getHours();
const due = [].slice.call(document.querySelectorAll(".hm-ev.deadline:not([hidden])"))
  .find((ev) => until(ev.dataset.start) >= 0 && until(ev.dataset.start) <= 3);

// News this browser has not been shown: `first` decides it while nothing
// is kept yet, and `keep()` marks it shown.
function news(store, value, first) {
  if (!value) return { fresh: false, keep() {} };
  let kept = null;
  try { kept = localStorage.getItem(store); } catch (e) { /* no storage: `first` decides */ }
  const keep = () => { try { localStorage.setItem(store, value); } catch (e) { /* nothing kept */ } };
  if (kept === null) keep();
  return { fresh: kept === null ? first : kept !== value, keep };
}
const run = news("probe.home.run.v1", host.dataset.run, recent(host.dataset.run));
const piece = news("probe.home.seen.v1", host.dataset.newKey, until(host.dataset.new) === 0);

if (due && lines.deadline) {
  const n = until(due.dataset.start);
  lines.deadline.querySelector("[data-dl-name]").textContent = due.querySelector("b").textContent;
  lines.deadline.querySelector("[data-dl-n]").textContent = n ? `D-${n}` : "오늘";
  wear("deadline", "deadline");
} else if (run.fresh && lines.run) {
  wear("scout", "run");
  run.keep();
} else if ((hour >= 23 || hour < 6) && lines.night) {
  wear("sleep", "night");
} else if (piece.fresh && lines.new) {
  wear("party", "new");
  piece.keep();
} else if (!still) {
  // Nothing to report: walk the tracks, the plain mark first.
  const walk = [["", "base"], ["scout", "scout"], ["analysis", "analysis"],
                ["compare", "compare"], ["idea", "idea"]].filter(([, l]) => lines[l]);
  let i = 0;
  setInterval(() => {
    if (document.hidden) return;
    i = (i + 1) % walk.length;
    wear(walk[i][0], walk[i][1], true);
  }, 6000);
}
})();
