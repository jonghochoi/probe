/* The nav's pill and the card it grows into (`components.nav_island()`).
 *
 * The pill's magnifier belongs to `palette.js`; this file owns the other
 * button. Pressing it grows the pill's shell into the card, and each row of
 * the card that picks one of several slides its indicator to the marked item.
 * Both move on springs rather than on timed curves, so a card that is
 * reopened mid-close, or a pick made mid-slide, carries its speed into the
 * new target instead of restarting. Every element is markup the build
 * printed: the script sizes, moves and toggles `inert`, and builds nothing.
 *
 * The card closes on Escape, on its own ✕, on a press outside it, when focus
 * leaves it, and on following one of its links.
 */
(function () {
  const isl = document.querySelector("[data-isl]");
  if (!isl) return;
  const shell = isl.querySelector(".isl-shell");
  const rest = isl.querySelector('[data-isl-face="rest"]');
  const card = isl.querySelector('[data-isl-face="card"]');
  const btn = isl.querySelector("[data-isl-open]");
  const still = matchMedia("(prefers-reduced-motion: reduce)");

  // Unit-mass springs: `k` stiffness, `c` damping. GROW sizes the shell and
  // rounds its corner and is let to overshoot a little, so the card lands;
  // SLIDE moves an indicator and is stiffer, so a pick answers at once.
  const GROW = { k: 340, c: 27 };
  const SLIDE = { k: 520, c: 38 };
  const live = new Set();
  let raf = 0, last = 0;
  function step(now) {
    const dt = Math.min(0.05, (now - last) / 1000);
    last = now;
    const n = Math.max(1, Math.ceil(dt * 240)), h = dt / n;
    for (const s of live) {
      for (let i = 0; i < n; i++) {
        s.v += (-s.cfg.k * (s.x - s.t) - s.cfg.c * s.v) * h;
        s.x += s.v * h;
      }
      if (Math.abs(s.x - s.t) < 0.05 && Math.abs(s.v) < 0.5) { s.x = s.t; s.v = 0; live.delete(s); }
      s.paint(s.x);
    }
    raf = live.size ? requestAnimationFrame(step) : 0;
  }
  function spring(cfg, paint) {
    const s = {
      x: 0, v: 0, t: 0, cfg, paint,
      set(t) { s.t = s.x = t; s.v = 0; live.delete(s); paint(t); },
      to(t) {
        if (still.matches) return s.set(t);
        s.t = t; live.add(s);
        if (!raf) { last = performance.now(); raf = requestAnimationFrame(step); }
      },
    };
    return s;
  }

  const sw = spring(GROW, (v) => { shell.style.width = `${v}px`; });
  const sh = spring(GROW, (v) => { shell.style.height = `${v}px`; });
  const sr = spring(GROW, (v) => { shell.style.borderRadius = `${Math.max(0, v)}px`; });
  const cardRadius = () => parseFloat(getComputedStyle(document.documentElement).getPropertyValue("--radius")) || 12;
  let open = false;

  function fit(jump) {
    const face = open ? card : rest;
    const how = jump ? "set" : "to";
    sw[how](face.offsetWidth);
    sh[how](face.offsetHeight);
    sr[how](open ? cardRadius() : face.offsetHeight / 2);
  }
  function show(on, restore) {
    if (on === open) return;
    open = on;
    rest.classList.toggle("is-on", !on); rest.inert = on;
    card.classList.toggle("is-on", on); card.inert = !on;
    isl.classList.toggle("is-open", on);
    btn.setAttribute("aria-expanded", String(on));
    fit(false);
    if (on) card.focus({ preventScroll: true });
    else if (restore) btn.focus({ preventScroll: true });
  }

  // The pill keeps its own box in the row, so the row never reflows while
  // the shell over it grows; the box follows the pill when a font arrives or
  // the viewport crosses into the phone's two-glyph pill.
  new ResizeObserver(() => {
    isl.style.width = `${rest.offsetWidth}px`;
    isl.style.height = `${rest.offsetHeight}px`;
    if (!open) fit(true);
  }).observe(rest);
  new ResizeObserver(() => { if (open) fit(false); }).observe(card);

  btn.addEventListener("click", () => show(true));
  card.addEventListener("click", (e) => {
    if (e.target.closest("[data-isl-close]")) show(false, true);
    else if (e.target.closest("a")) show(false);
  });
  document.addEventListener("pointerdown", (e) => { if (open && !isl.contains(e.target)) show(false); });
  isl.addEventListener("focusout", (e) => {
    if (open && e.relatedTarget && !isl.contains(e.relatedTarget)) show(false);
  });
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && open) show(false, true);
  });

  // Each row's indicator sits under whichever item carries the mark, and
  // follows the mark when `theme.js` moves it — by a pick or by the theme
  // shortcut with the card shut, in which case it moves without sliding.
  isl.querySelectorAll(".isl-seg").forEach((seg) => {
    const blob = seg.querySelector(".isl-blob");
    const bx = spring(SLIDE, (v) => { blob.style.transform = `translateX(${v}px)`; });
    const bw = spring(SLIDE, (v) => { blob.style.width = `${v}px`; });
    let placed = false;
    function place(jump) {
      const it = seg.querySelector('[aria-checked="true"], [aria-current="page"]');
      if (!it || !it.offsetWidth) { blob.style.opacity = "0"; placed = false; return; }
      const how = jump || !placed || !open ? "set" : "to";
      bx[how](it.offsetLeft);
      bw[how](it.offsetWidth);
      blob.style.opacity = "1";
      placed = true;
    }
    new MutationObserver(() => place(false))
      .observe(seg, { subtree: true, attributes: true, attributeFilter: ["aria-checked", "aria-current"] });
    new ResizeObserver(() => place(true)).observe(seg);
    place(true);
  });
})();

/* How many papers this browser has starred, on 서재 in the row and in the
 * phone's menu — shown only when there is at least one. The count is read
 * straight from the shelf's store (`shelf.js`), because every page has the nav
 * and not every page loads the shelf; it follows a star toggled on this page
 * and one toggled in another tab. */
(function () {
  const slots = document.querySelectorAll("[data-star-count]");
  if (!slots.length) return;
  function paint() {
    let n = 0;
    try {
      const map = JSON.parse(localStorage.getItem("probe.stars.v1") || "{}");
      if (map && typeof map === "object" && !Array.isArray(map)) n = Object.keys(map).length;
    } catch (e) { /* blocked or unreadable storage: no count */ }
    slots.forEach((s) => {
      s.hidden = !n;
      s.textContent = n ? String(n) : "";
      if (n) s.setAttribute("aria-label", `즐겨찾기 ${n}편`); else s.removeAttribute("aria-label");
    });
  }
  document.addEventListener("probe:shelf-change", paint);
  addEventListener("storage", (e) => { if (!e.key || e.key === "probe.stars.v1") paint(); });
  paint();
})();
