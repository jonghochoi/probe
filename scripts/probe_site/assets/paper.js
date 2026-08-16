/* Paper page: term anchors, quizzes, TOC scroll-spy.
   No framework, no bundler. Without this file the page is still fully
   readable — term definitions render expanded and quizzes show their options.
   (The theme toggle lives in theme.js — every page has the nav button.) */

(function () {
  "use strict";

  /* ── Readable layer: term anchors + quizzes ───────────────────────── */
  // Delegated, because both live inside panels that are re-shown by the view
  // switcher; binding per element would miss anything in a hidden panel.
  document.addEventListener("click", function (e) {
    var ref = e.target.closest && e.target.closest(".tref");
    if (ref) {
      var def = document.getElementById("term-" + ref.dataset.term);
      if (!def) return;
      var open = def.hidden;
      def.hidden = !open;
      ref.setAttribute("aria-expanded", open ? "true" : "false");
      return;
    }

    var opt = e.target.closest && e.target.closest(".qopt");
    if (!opt) return;
    var quiz = opt.closest("[data-quiz]");
    // Answer once: re-picking after seeing the explanation teaches nothing.
    if (!quiz || quiz.hasAttribute("data-answered")) { e.preventDefault(); return; }
    quiz.setAttribute("data-answered", "");
    var input = opt.querySelector("input");
    if (input) input.checked = true;   // before disabling — a disabled input
    [].forEach.call(quiz.querySelectorAll(".qopt"), function (o) {
      var i = o.querySelector("input");
      o.dataset.correct = i && i.dataset.correct === "1" ? "1" : "0";
      o.dataset.chosen = o === opt ? "1" : "0";
      if (i) i.disabled = true;        // ...would not take the check
    });
    var why = quiz.querySelector(".qwhy");
    if (why) why.hidden = false;
  });

  /* ── TOC + scroll-spy ─────────────────────────────────────────────── */
  var tocEl = document.querySelector("[data-toc]");
  var spy = null;

  function buildToc() {
    if (!tocEl) return;
    var heads = [].slice.call(document.querySelectorAll(".article h2.h-sec, .article h3[id]"));
    tocEl.innerHTML = '<div class="toc-title">목차</div>' + heads.map(function (h) {
      var lv = h.tagName === "H3" ? " lv3" : "";
      var txt = h.textContent.replace(/#$/, "").trim();
      return '<a class="' + lv.trim() + '" href="#' + h.id + '">' + escapeHtml(txt) + "</a>";
    }).join("");

    if (spy) spy.disconnect();
    var links = {};
    tocEl.querySelectorAll("a").forEach(function (a) {
      links[a.getAttribute("href").slice(1)] = a;
    });
    spy = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        var a = links[en.target.id];
        if (!a) return;
        if (en.isIntersecting) {
          tocEl.querySelectorAll("a.active").forEach(function (x) { x.classList.remove("active"); });
          a.classList.add("active");
        }
      });
    }, { rootMargin: "-70px 0px -75% 0px" });
    heads.forEach(function (h) { spy.observe(h); });
  }

  function escapeHtml(s) {
    return s.replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }

  buildToc();
})();
