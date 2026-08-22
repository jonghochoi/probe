/* Paper page: the tab strip, term anchors, quizzes, TOC scroll-spy.
   No framework, no bundler. Without this file the page is still fully
   readable — the first tab is open and the other is reachable by its anchor,
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

  /* ── TOC scroll-spy ───────────────────────────────────────────────── */
  // The contents themselves are server-rendered (pages.py `_toc`), because the
  // act grouping is structure the renderer knows and the DOM does not state.
  // All that is left here is marking which section the reader is in.
  var tocEl = document.querySelector(".toc");

  function spyToc() {
    if (!tocEl || !("IntersectionObserver" in window)) return;
    var links = {};
    [].forEach.call(tocEl.querySelectorAll("a[href^='#']"), function (a) {
      links[a.getAttribute("href").slice(1)] = a;
    });
    var heads = Object.keys(links)
      .map(function (id) { return document.getElementById(id); })
      .filter(Boolean);
    if (!heads.length) return;

    var spy = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        var a = links[en.target.id];
        if (!a) return;
        [].forEach.call(tocEl.querySelectorAll("a.active"), function (x) {
          x.classList.remove("active");
        });
        a.classList.add("active");
      });
    }, { rootMargin: "-12% 0px -75% 0px" });
    heads.forEach(function (h) { spy.observe(h); });
  }

  /* ── The two surfaces: the tab strip ──────────────────────────────── */
  var tabs = [].slice.call(document.querySelectorAll(".tabs .tab"));
  // 이 논문이 들어간 비교 closes both surfaces, so the header chip has two
  // possible targets and only one of them is on screen. Pointing it at the
  // hidden copy would switch surfaces on a reader who only asked to scroll.
  var cmpJump = document.querySelector("[data-cmp-jump]");

  function showSurface(key, push) {
    tabs.forEach(function (tab) {
      var on = tab.dataset.tab === key;
      tab.setAttribute("aria-selected", on ? "true" : "false");
      var panel = document.getElementById(tab.getAttribute("aria-controls"));
      if (panel) panel.hidden = !on;
    });
    if (cmpJump) {
      cmpJump.setAttribute(
        "href", key === "full" ? "#in-comparisons-full" : "#in-comparisons");
    }
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
    // that lives inside 상세. Landing on 요약 with it hidden makes the page look
    // like it ignored the link, so the surface follows the target.
    function surfaceForHash() {
      var hash = (location.hash || "").slice(1);
      var target = hash && document.getElementById(hash);
      var full = document.getElementById("p-full");
      var deep = target && full && full.contains(target);
      showSurface(hash === "full" || deep ? "full" : "glance", false);
      // The browser scrolls to the target as it arrives, while the panel is
      // still hidden, so nothing moves. Now that it is open, do it again —
      // for any target, since a link followed from 상세 into 요약 leaves the
      // 요약 panel hidden at the moment the browser would have scrolled it.
      if (target) target.scrollIntoView();
    }

    surfaceForHash();
    // Changing only the fragment does not reload the document, so the same
    // link followed from this page has to be handled rather than waited for.
    addEventListener("hashchange", surfaceForHash);
  }

  spyToc();
})();
