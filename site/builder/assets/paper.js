/* Paper page: the tab strip, term anchors, quizzes, TOC scroll-spy, the act
   strip and its contents sheet.
   No framework, no bundler. Without this file the page is still fully
   readable — the first tab is open and every other tab is reachable by its anchor,
   term definitions render expanded and quizzes show their options.
   (The theme toggle lives in theme.js — every page has the nav button.) */

(function () {
  "use strict";

  /* ── Readable layer: term anchors + quizzes ───────────────────────── */
  // Delegated, because both live inside panels that are re-shown by the view
  // switcher; binding per element would miss anything in a hidden panel.
  document.addEventListener("click", function (e) {
    var ref = e.target.closest && e.target.closest(".tref");
    if (ref) {
      // The panel is the anchor's own next sibling — R4 opens the definition
      // where the word is, so there is nothing to look up by id.
      var def = ref.nextElementSibling;
      if (!def || !def.classList.contains("tbox")) return;
      var open = def.hidden;
      def.hidden = !open;
      ref.setAttribute("aria-expanded", open ? "true" : "false");
      return;
    }

    var opt = e.target.closest && e.target.closest(".qopt");
    if (!opt) return;
    var quiz = opt.closest("[data-quiz]");
    // Answer once: re-picking after seeing the explanation teaches nothing.
    if (!quiz || quiz.hasAttribute("data-answered")) return;
    quiz.setAttribute("data-answered", "");
    [].forEach.call(quiz.querySelectorAll(".qopt"), function (o) {
      o.dataset.chosen = o === opt ? "1" : "0";
      o.disabled = true;
    });
    var why = quiz.querySelector(".qwhy");
    if (why) why.hidden = false;
  });

  // The contents are server-rendered (pages.py `_toc`), because the act
  // grouping is structure the renderer knows and the DOM does not state. What
  // is left here is marking where the reader is (below) and opening the whole
  // list over the article when the reader reaches for the rail.
  var tocEl = document.querySelector(".shell > .toc");

  /* ── The two surfaces: the tab strip ──────────────────────────────── */
  var tabs = [].slice.call(document.querySelectorAll(".tabs .tab"));

  function panelOf(tab) {
    return document.getElementById(tab.getAttribute("aria-controls"));
  }

  function showSurface(key, push) {
    tabs.forEach(function (tab) {
      var on = tab.dataset.tab === key;
      tab.setAttribute("aria-selected", on ? "true" : "false");
      var panel = panelOf(tab);
      if (panel) panel.hidden = !on;
    });
    // The surface belongs in the URL: a link to one surface of a paper is a
    // thing people send each other, and the back button should undo a switch.
    if (push && history.replaceState) {
      history.replaceState(null, "", key === "glance" ? location.pathname : "#" + key);
    }
  }

  if (tabs.length) {
    tabs.forEach(function (tab) {
      tab.addEventListener("click", function () { showSurface(tab.dataset.tab, true); });
    });
    // A link into the body — a section, a term, a figure — names an element
    // that lives inside one particular tab. Landing on 요약 with that tab
    // hidden makes the page look like it ignored the link, so the surface
    // follows the target: whichever panel holds it wins, and a bare `#full` or
    // `#cmp` names its tab directly.
    function surfaceForHash() {
      var hash = (location.hash || "").slice(1);
      var target = hash && document.getElementById(hash);
      var holder = "";
      tabs.forEach(function (tab) {
        var panel = panelOf(tab);
        if (!holder && target && panel && panel.contains(target)) {
          holder = tab.dataset.tab;
        }
      });
      var named = tabs.some(function (t) { return t.dataset.tab === hash; });
      showSurface(holder || (named ? hash : "glance"), false);
      // The browser scrolls to the target as it arrives, while its panel is
      // still hidden, so nothing moves. Now that it is open, do it again.
      if (target) target.scrollIntoView();
    }

    surfaceForHash();
    // Changing only the fragment does not reload the document, so the same
    // link followed from this page has to be handled rather than waited for.
    addEventListener("hashchange", surfaceForHash);
  }

  /* ── Where the reader is: the contents and the act strip ───────────── */
  // The section being read is the last heading above the bars' lower edge,
  // within the act being read. It is the only thing that moves as the page
  // scrolls: the rail marks it and nothing else, so reading is not watched by
  // a column that changes on every line.
  var full = document.getElementById("p-full");
  var strip = document.querySelector(".actstrip");
  var article = document.querySelector("#p-full .article");
  if (!full || !article) return;
  var actLinks = strip ? [].slice.call(strip.querySelectorAll(".as-link")) : [];
  var acts = actLinks.map(function (a) {
    return document.getElementById(a.getAttribute("href").slice(1));
  });
  var nav = document.querySelector(".site-nav");
  var secLinks = tocEl ? [].slice.call(tocEl.querySelectorAll(".ms-sec")) : [];
  var secs = secLinks.map(function (a) {
    return { id: a.getAttribute("href").slice(1), el: document.getElementById(a.getAttribute("href").slice(1)),
             g: a.closest(".ms-g") };
  });
  var groups = tocEl ? [].slice.call(tocEl.querySelectorAll(".ms-g")) : [];
  var hereId = null, hereG = null;

  var ticking = false;
  function follow() {
    ticking = false;
    if (full.hidden) return;
    var bars = [nav, document.querySelector(".tabs-wrap"), strip];
    var top = bars.reduce(function (y, el) {
      return el && el.offsetHeight ? Math.max(y, el.getBoundingClientRect().bottom) : y;
    }, 0);
    var cur = -1;
    acts.forEach(function (el, i) {
      if (el && el.getBoundingClientRect().top < top + 40) cur = i;
    });
    actLinks.forEach(function (a, i) {
      if (i === Math.max(cur, 0)) a.setAttribute("aria-current", "true");
      else a.removeAttribute("aria-current");
    });
    var g = groups[Math.max(cur, 0)] || null, id = "";
    secs.forEach(function (x) {
      if (x.el && x.g === g && x.el.getBoundingClientRect().top < top + 40) id = x.id;
    });
    if (id === hereId && g === hereG) return;
    hereId = id; hereG = g;
    // Every copy of the contents — the rail and the sheet's — marks the same place.
    [].forEach.call(document.querySelectorAll(".toc .ms-sec"), function (a) {
      if (a.getAttribute("href") === "#" + id) a.setAttribute("aria-current", "true");
      else a.removeAttribute("aria-current");
    });
    var gi = groups.indexOf(g);
    [].forEach.call(document.querySelectorAll(".toc"), function (t) {
      [].forEach.call(t.querySelectorAll(".ms-g"), function (e, i) { e.classList.toggle("on", i === gi); });
    });
  }
  function soon() { if (!ticking) { ticking = true; requestAnimationFrame(follow); } }
  addEventListener("scroll", soon, { passive: true });
  addEventListener("resize", soon);
  tabs.forEach(function (tab) { tab.addEventListener("click", soon); });
  addEventListener("hashchange", soon);
  follow();

  // The rail, reached for: the whole list opens over the article. A beat late
  // both ways, so a pointer crossing the rail on its way elsewhere opens
  // nothing, and one that slips off the list's edge does not shut it.
  if (tocEl) {
    var timer = 0;
    var setOpen = function (on, wait) {
      clearTimeout(timer);
      timer = setTimeout(function () { tocEl.classList.toggle("is-open", on); }, wait);
    };
    tocEl.addEventListener("mouseenter", function () { setOpen(true, 200); });
    tocEl.addEventListener("mouseleave", function () { setOpen(false, 400); });
    tocEl.addEventListener("focusin", function () { setOpen(true, 0); });
    tocEl.addEventListener("focusout", function (e) {
      if (!tocEl.contains(e.relatedTarget)) setOpen(false, 0);
    });
    tocEl.addEventListener("click", function (e) {
      if (e.target.closest && e.target.closest("a")) setOpen(false, 0);
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && tocEl.classList.contains("is-open")) setOpen(false, 0);
    });
  }

  // 목차: the same server-rendered contents, opened from below.
  var open = strip && strip.querySelector("[data-toc-open]");
  if (!open || !tocEl) return;
  var sheet = document.createElement("div");
  sheet.className = "toc-sheet"; sheet.hidden = true;
  sheet.setAttribute("role", "dialog"); sheet.setAttribute("aria-modal", "true");
  sheet.setAttribute("aria-label", "목차");
  var inner = document.createElement("div"); inner.className = "toc-sheet-in";
  var head = document.createElement("div"); head.className = "toc-sheet-h";
  head.appendChild(document.createTextNode("목차"));
  var x = document.createElement("button");
  x.type = "button"; x.className = "toc-sheet-x"; x.setAttribute("aria-label", "닫기");
  x.innerHTML = '<svg viewBox="0 0 16 16" width="14" height="14" fill="none" stroke="currentColor" ' +
    'stroke-width="1.8" stroke-linecap="round" aria-hidden="true"><path d="m4 4 8 8M12 4l-8 8"/></svg>';
  head.appendChild(x);
  inner.appendChild(head);
  inner.appendChild(tocEl.cloneNode(true));
  sheet.appendChild(inner);
  document.body.appendChild(sheet);
  function close() { if (!sheet.hidden) { sheet.hidden = true; open.focus({ preventScroll: true }); } }
  open.hidden = false;
  open.addEventListener("click", function () { sheet.hidden = false; x.focus({ preventScroll: true }); });
  x.addEventListener("click", close);
  sheet.addEventListener("click", function (e) {
    if (e.target === sheet || (e.target.closest && e.target.closest("a"))) sheet.hidden = true;
  });
  document.addEventListener("keydown", function (e) { if (e.key === "Escape") close(); });
})();
