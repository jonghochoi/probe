/* The three surfaces of a paper page: the tab strip, and the deck's own
   controls. Without this file the page still works — the first tab is open,
   the other two are reachable by their anchors, and every slide renders — but
   nothing switches and the deck shows only its first slide. */

(function () {
  "use strict";

  /* ── Tabs ───────────────────────────────────────────────────────────── */
  var tabs = [].slice.call(document.querySelectorAll(".tabs .tab"));
  if (!tabs.length) return;

  function show(key, push) {
    tabs.forEach(function (tab) {
      var on = tab.dataset.tab === key;
      tab.setAttribute("aria-selected", on ? "true" : "false");
      var panel = document.getElementById(tab.getAttribute("aria-controls"));
      if (panel) panel.hidden = !on;
    });
    // The surface belongs in the URL: a link to the deck of a paper is a thing
    // people send each other, and the back button should undo a tab switch.
    if (push && history.replaceState) {
      history.replaceState(null, "", key === "full" ? location.pathname : "#" + key);
    }
    if (key === "deck" && stage) stage.focus({ preventScroll: true });
  }

  tabs.forEach(function (tab) {
    tab.addEventListener("click", function () { show(tab.dataset.tab, true); });
  });

  /* ── Deck ───────────────────────────────────────────────────────────── */
  var deck = document.querySelector("[data-deck]");
  var stage = deck && deck.querySelector("[data-dk-stage]");
  var slides = deck ? [].slice.call(deck.querySelectorAll("[data-dk-slide]")) : [];
  var at = 0;
  var step = 1;

  if (deck && slides.length) {
    var film = deck.querySelector("[data-dk-film]");
    var count = deck.querySelector("[data-dk-count]");
    var note = deck.querySelector("[data-dk-note]");
    var qa = deck.querySelector("[data-dk-qa]");
    var chapters = [].slice.call(deck.querySelectorAll(".dk-ch"));

    slides.forEach(function (slide, i) {
      var thumb = document.createElement("button");
      thumb.type = "button";
      thumb.className = "dk-thumb";
      var title = slide.querySelector(".dk-title");
      thumb.innerHTML = "<b>" + (i + 1) + "</b>" + (title ? title.textContent : "");
      thumb.addEventListener("click", function () { go(i); });
      film.appendChild(thumb);
    });
    var thumbs = [].slice.call(film.children);

    function steps() {
      return parseInt(slides[at].dataset.steps || "1", 10);
    }

    function paint() {
      var reveals = slides[at].querySelectorAll("[data-rev]");
      [].forEach.call(reveals, function (el) {
        el.classList.toggle("on", parseInt(el.dataset.rev, 10) <= step);
      });
      count.textContent =
        (at + 1) + " / " + slides.length +
        (steps() > 1 ? " · 단계 " + step + "/" + steps() : "");
    }

    function go(index, toEnd) {
      at = (index + slides.length) % slides.length;
      slides.forEach(function (s, i) { s.hidden = i !== at; });
      step = toEnd ? steps() : 1;
      paint();
      thumbs.forEach(function (t, i) {
        t.setAttribute("aria-current", i === at ? "true" : "false");
      });
      var here = slides[at].dataset.ch || "";
      var reached = -1;
      chapters.forEach(function (ch, i) { if (ch.dataset.ch === here) reached = i; });
      chapters.forEach(function (ch, i) {
        ch.toggleAttribute("data-on", i === reached);
        ch.toggleAttribute("data-done", reached >= 0 && i < reached);
      });
      // The cover has no chapter, so the row would otherwise show every bead
      // unlit — which reads as a broken control rather than as "not started".
      deck.querySelector("[data-dk-chapters]").hidden = reached < 0;
      note.textContent = slides[at].dataset.note || "";
      qa.textContent = slides[at].dataset.qa || "";
      qa.hidden = !slides[at].dataset.qa;
    }

    function next() { if (step < steps()) { step++; paint(); } else go(at + 1); }
    function prev() { if (step > 1) { step--; paint(); } else go(at - 1, true); }

    deck.querySelector("[data-dk-prev]").addEventListener("click", prev);
    deck.querySelector("[data-dk-next]").addEventListener("click", next);
    deck.querySelector("[data-dk-full]").addEventListener("click", function () {
      if (document.fullscreenElement) document.exitFullscreen();
      else if (stage.requestFullscreen) stage.requestFullscreen();
    });
    // Arrow keys belong to the deck only while the deck is the open surface;
    // on the body they are the reader's own scroll.
    document.addEventListener("keydown", function (e) {
      var panel = document.getElementById("p-deck");
      if (!panel || panel.hidden) return;
      if (e.target && /^(INPUT|TEXTAREA)$/.test(e.target.tagName)) return;
      if (e.key === "ArrowRight" || e.key === "PageDown") { next(); e.preventDefault(); }
      if (e.key === "ArrowLeft" || e.key === "PageUp") { prev(); e.preventDefault(); }
    });
    go(0);
  }

  var hash = (location.hash || "").slice(1);
  show(hash === "glance" || hash === "deck" ? hash : "full", false);
})();
