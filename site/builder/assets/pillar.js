/* 연구 축 — what an axis chip opens: the axis's introduction where its owner
 * wrote one, and the open questions it keeps (the titles of the entries its
 * pillar file owns). A card under the chip on a desktop, a sheet from below on
 * a phone.
 *
 * Its smaller sibling is what a `D#` citation opens: the question's title, the
 * axis it belongs to, and the other rewrites that cite it. The browser's own
 * `title` tooltip reaches only a mouse, so the script takes the title off and
 * opens this card on a resting pointer, on focus and on a tap instead.
 *
 * Every page carries it, because every page carries chips. The data is
 * `window.ProbeIndex` (`assets/corpus-index.js`): `axes` for both cards, each
 * paper's `d` for who cites what. With no script a chip is the plain label it
 * was and a `D#` keeps its `title`, which is all a page without this loses.
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

/* Under the trigger, inside the screen; above it when there is no room below.
 * The card grows out of the trigger's edge, so the transform origin is put
 * where the trigger meets the card. */
function place() {
  const p = box.querySelector(".axp-p");
  if (!p || !cur || PHONE.matches) return;
  const r = cur.getBoundingClientRect();
  const w = p.offsetWidth, h = p.offsetHeight;
  let top = r.bottom + 8, below = true;
  if (top + h > innerHeight - 12) { top = Math.max(12, r.top - h - 8); below = false; }
  const left = Math.min(Math.max(12, r.left), innerWidth - w - 12);
  p.style.left = `${left}px`;
  p.style.top = `${top}px`;
  p.style.setProperty("--ox", `${Math.round(r.left + r.width / 2 - left)}px`);
  p.style.setProperty("--oy", below ? "0px" : "100%");
}

function show(trigger, html) {
  box.className = `axp ${PHONE.matches ? "axp-sheet" : "axp-pop"}`;
  box.innerHTML = '<div class="axp-bg" data-axp-close></div>' + html;
  box.hidden = false;
  cur = trigger;
  document.documentElement.classList.toggle("axp-lock", PHONE.matches);
  place();
}

function open(chip) {
  const code = chip.dataset.p;
  if (!AXES[code]) return;
  show(chip, card(code));
  box.querySelector(".axp-x").focus({ preventScroll: true });
}

/* The card is left in the box as the box hides, so it can shrink back into
 * its trigger; the next open replaces it. */
function close() {
  if (box.hidden) return;
  const back = cur, peeked = byHover;
  box.hidden = true; cur = null; byHover = false;
  document.documentElement.classList.remove("axp-lock");
  // A card a resting pointer opened never took focus, so there is none to
  // hand back.
  if (back && !peeked) back.focus({ preventScroll: true });
}

/* ── D# ─────────────────────────────────────────────────────────────────── */
const DECS = {};
Object.keys(AXES).forEach((code) =>
  (AXES[code].decisions || []).forEach(([id, title]) => { DECS[id] = { p: code, t: title }; }));
const CITED = {};
(index.papers || []).forEach((p) => (p.d || []).forEach((d) => { (CITED[d] = CITED[d] || []).push(p); }));
const here = document.querySelector("[data-paper-acts]");
const SELF = here ? here.dataset.paperId : "";
const me = document.currentScript || document.querySelector('script[src*="assets/pillar.js"]');
const ROOT = me ? me.src.replace(/assets\/pillar\.js(\?.*)?$/, "") : "";
const MORE = 5;

function dcard(el) {
  const code = el.dataset.d;
  const d = DECS[code];
  const others = (CITED[code] || []).filter((p) => p.id !== SELF);
  const items = others.slice(0, MORE).map((p) =>
    `<li><a href="${esc(ROOT)}p/${esc(p.id)}/index.html">${esc(p.title)}</a></li>`).join("") +
    (others.length > MORE ? `<li class="axp-dc">외 ${others.length - MORE}편</li>` : "");
  const pc = d ? d.p.toLowerCase() : "pna";
  return `<div class="axp-p axp-d" role="dialog" aria-label="${esc(code)}" style="--pc:var(--${pc})">` +
    `<header class="axp-h">` +
    (d ? `<span class="chip pillar" data-p="${esc(d.p)}">${esc(d.p)}</span>` : "") +
    `<div class="axp-names"><span class="axp-code">${esc(code)}${d ? ` · ${esc(LABELS[d.p] || "")}` : ""}</span>` +
    `<b>${esc(d ? d.t : el.dataset.tip || "")}</b></div>` +
    `<button type="button" class="axp-x" data-axp-close aria-label="닫기">${X}</button></header>` +
    (items ? `<section class="axp-decs"><h3>같은 질문을 다룬 글<span>${others.length}</span></h3><ul>${items}</ul></section>` : "") +
    "</div>";
}

/* A card the pointer is only resting on leaves the page live under it — its
 * backdrop takes no clicks until a click pins the card. */
function openD(el, hover) {
  show(el, dcard(el));
  byHover = !!hover;
  box.classList.toggle("axp-peek", byHover);
  if (!hover) box.querySelector(".axp-x").focus({ preventScroll: true });
}

/* A citation is a control now: its title becomes the card's, and the
 * keyboard reaches it. */
function armD(root) {
  root.querySelectorAll("abbr.dref:not([data-d])").forEach((el) => {
    el.dataset.d = el.textContent.trim();
    el.dataset.tip = el.title || "";
    el.removeAttribute("title");
    el.setAttribute("tabindex", "0");
    el.setAttribute("role", "button");
    el.setAttribute("aria-haspopup", "dialog");
  });
}

/* A resting pointer opens the card after a beat and a pointer that leaves
 * both the citation and the card closes it after another, so the card can be
 * reached to follow a link in it. A click or a tap pins it open. */
const HOVER = matchMedia("(hover: hover)");
const inCard = (n) => { const c = box.querySelector(".axp-p"); return !!(c && n && c.contains(n)); };
let byHover = false, openT = 0, shutT = 0;
document.addEventListener("pointerover", (e) => {
  if (!HOVER.matches) return;
  const el = e.target.closest && e.target.closest("abbr.dref[data-d]");
  if (el && !box.contains(el)) {
    clearTimeout(shutT);
    if (cur !== el) { clearTimeout(openT); openT = setTimeout(() => openD(el, true), 400); }
  } else if (byHover && inCard(e.target)) clearTimeout(shutT);
});
document.addEventListener("pointerout", (e) => {
  if (!HOVER.matches) return;
  const el = e.target.closest && e.target.closest("abbr.dref[data-d]");
  if (el) clearTimeout(openT);
  if (!byHover) return;
  const to = e.relatedTarget;
  if (to && (inCard(to) || (cur && cur.contains(to)))) return;
  clearTimeout(shutT); shutT = setTimeout(close, 300);
});

/* The chip opens its popup and nothing else. Chips sit inside cards and over
 * a row's link, so the click is taken before those see it. */
document.addEventListener("click", (e) => {
  if (e.target.closest("[data-axp-close]")) { close(); return; }
  const dref = e.target.closest("abbr.dref[data-d]");
  if (dref && !box.contains(dref)) {
    e.preventDefault(); e.stopPropagation(); clearTimeout(openT);
    if (cur === dref && byHover) {
      byHover = false; box.classList.remove("axp-peek");
      box.querySelector(".axp-x").focus({ preventScroll: true });
    }
    else if (cur === dref) close(); else openD(dref, false);
    return;
  }
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
arm(document); armD(document);
new MutationObserver(() => { arm(document); armD(document); })
  .observe(document.body, { childList: true, subtree: true });

document.addEventListener("keydown", (e) => {
  if (e.key === "Escape" && !box.hidden) { close(); return; }
  const dref = e.target.closest && e.target.closest("abbr.dref[data-d]");
  if (dref && (e.key === "Enter" || e.key === " ") && !box.contains(dref)) {
    e.preventDefault(); e.stopPropagation();
    openD(dref, false);
    return;
  }
  const chip = e.target.closest && e.target.closest(".chip.pillar[data-p]");
  if (chip && (e.key === "Enter" || e.key === " ") && AXES[chip.dataset.p] && !box.contains(chip)) {
    e.preventDefault(); e.stopPropagation();
    open(chip);
  }
}, true);
addEventListener("scroll", place, { passive: true });
addEventListener("resize", () => { if (!box.hidden) close(); });
})();
