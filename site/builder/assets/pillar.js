/* 연구 축 — what an axis chip opens: the axis's introduction where its owner
 * wrote one, and the open questions it keeps (the titles of the entries its
 * pillar file owns). A card under the chip on a desktop, a sheet from below on
 * a phone.
 *
 * Every page carries it, because every page carries chips. The data is
 * `window.ProbeIndex.axes` (`assets/corpus-index.js`). With no script a chip
 * is the plain label it was, which is all a page without this loses.
 */
(function () {
"use strict";

const index = window.ProbeIndex;
const AXES = index && index.axes;
if (!AXES) return;
const LABELS = index.pillarLabels || {};
const NAMES = index.pillars || {};
const PHONE = matchMedia("(max-width: 720px)");
const X = '<svg viewBox="0 0 16 16" width="14" height="14" fill="none" stroke="currentColor" ' +
  'stroke-width="1.8" stroke-linecap="round" aria-hidden="true"><path d="m4 4 8 8M12 4l-8 8"/></svg>';
const esc = (t) => String(t == null ? "" : t)
  .replace(/[&<>"]/g, (ch) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[ch]));

const box = document.createElement("div");
box.className = "axp"; box.hidden = true;
document.body.appendChild(box);
document.documentElement.classList.add("axp-on");
let cur = null;

function card(code) {
  const a = AXES[code];
  const decs = a.decisions.map(([id, title]) =>
    `<li><span class="axp-dt">${esc(title)}</span>` +
    `<span class="axp-dc">${esc(id)}</span></li>`).join("");
  return `<div class="axp-p" role="dialog" aria-label="${esc(`${code} ${LABELS[code] || ""}`)}" ` +
    `style="--pc:var(--${code.toLowerCase()})">` +
    `<header class="axp-h"><span class="chip pillar" data-p="${esc(code)}">${esc(code)}</span>` +
    `<div class="axp-names"><b>${esc(LABELS[code] || code)}</b><span>${esc(NAMES[code] || "")}</span></div>` +
    `<button type="button" class="axp-x" data-axp-close aria-label="닫기">${X}</button></header>` +
    (a.intro ? `<p class="axp-intro">${esc(a.intro)}</p>` : "") +
    (decs ? `<section class="axp-decs"><h3>열린 질문<span>${a.decisions.length}</span></h3><ul>${decs}</ul></section>` : "") +
    "</div>";
}

/* Under the chip, inside the screen; above it when there is no room below. */
function place() {
  const p = box.querySelector(".axp-p");
  if (!p || !cur || PHONE.matches) return;
  const r = cur.getBoundingClientRect();
  const w = p.offsetWidth, h = p.offsetHeight;
  let top = r.bottom + 8;
  if (top + h > innerHeight - 12) top = Math.max(12, r.top - h - 8);
  p.style.left = `${Math.min(Math.max(12, r.left), innerWidth - w - 12)}px`;
  p.style.top = `${top}px`;
}

function open(chip) {
  const code = chip.dataset.p;
  if (!AXES[code]) return;
  box.className = `axp ${PHONE.matches ? "axp-sheet" : "axp-pop"}`;
  box.innerHTML = '<div class="axp-bg" data-axp-close></div>' + card(code);
  box.hidden = false;
  cur = chip;
  document.documentElement.classList.toggle("axp-lock", PHONE.matches);
  place();
  box.querySelector(".axp-x").focus({ preventScroll: true });
}

function close() {
  if (box.hidden) return;
  const back = cur;
  box.hidden = true; box.innerHTML = ""; cur = null;
  document.documentElement.classList.remove("axp-lock");
  if (back) back.focus({ preventScroll: true });
}

/* The chip opens its popup and nothing else. Chips sit inside cards and over
 * a row's link, so the click is taken before those see it. */
document.addEventListener("click", (e) => {
  if (e.target.closest("[data-axp-close]")) { close(); return; }
  const chip = e.target.closest(".chip.pillar[data-p]");
  if (chip && !box.contains(chip) && AXES[chip.dataset.p]) {
    e.preventDefault(); e.stopPropagation();
    if (cur === chip) close(); else open(chip);
    return;
  }
  if (!box.hidden && !box.contains(e.target)) close();
}, true);

/* A chip is a control now, so the keyboard reaches it too. */
function arm(root) {
  root.querySelectorAll(".chip.pillar[data-p]").forEach((chip) => {
    if (box.contains(chip) || !AXES[chip.dataset.p] || chip.hasAttribute("tabindex")) return;
    chip.setAttribute("tabindex", "0");
    chip.setAttribute("role", "button");
    chip.setAttribute("aria-haspopup", "dialog");
  });
}
arm(document);
new MutationObserver(() => arm(document)).observe(document.body, { childList: true, subtree: true });

document.addEventListener("keydown", (e) => {
  if (e.key === "Escape" && !box.hidden) { close(); return; }
  const chip = e.target.closest && e.target.closest(".chip.pillar[data-p]");
  if (chip && (e.key === "Enter" || e.key === " ") && AXES[chip.dataset.p] && !box.contains(chip)) {
    e.preventDefault(); e.stopPropagation();
    open(chip);
  }
}, true);
addEventListener("scroll", place, { passive: true });
addEventListener("resize", () => { if (!box.hidden) close(); });
})();
