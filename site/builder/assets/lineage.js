/* 계보 — the cells in a paper's 계보 tab.

   The tab arrives with a printed drawing of the paper between the older
   papers it is joined to and the newer ones, and with those same papers as
   JSON (`pages._lineage_data`). This file replaces the drawing with three
   columns of cells — 선행, the paper, 후속 — and in each column sets the
   papers a lineage rail names above the ones only the prose mentions. It
   reads the graph and decides nothing about it.

   Every cell is a link — to the other paper's 계보 tab, or to arXiv for a
   paper with no rewrite — so walking the graph is moving from page to page.

   A phone has room neither for three columns nor for the drawing shrunk
   to fit, so there the older and the newer papers are two panes of one
   strip the reader swipes through, with a row of two buttons over it
   naming each side and its count. The paper itself leaves the strip: its
   page already opens on its title. The strip opens on the older papers
   and is as tall as the pane in view, so a short pane leaves no blank
   under it.

   Without this file the tab is its printed drawing. */

(function () {
  "use strict";
  var blob = document.getElementById("lin-data"), box = document.getElementById("lin-tree");
  if (!blob || !box) return;
  var data = JSON.parse(blob.textContent), me = data.me, frame = box.parentNode;
  var each = function (list, fn) { Array.prototype.forEach.call(list, fn); };

  function esc(s) {
    return String(s).replace(/[&<>"]/g, function (ch) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[ch];
    });
  }
  function ym(id) { return "20" + id.slice(0, 2) + "." + id.slice(2, 4); }

  var EXT = '<svg viewBox="0 0 16 16" width="12" height="12" fill="none" stroke="currentColor" stroke-width="1.7" ' +
    'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M6.5 3.5H3.5v9h9V9.5"/>' +
    '<path d="M9.5 3h3.5v3.5M13 3 7.5 8.5"/></svg>';
  function keyLine(text) {
    return '<svg class="k-line' + (text ? " is-text" : "") + '" viewBox="0 0 34 10" width="34" height="10" aria-hidden="true">' +
      '<path d="M1 5H26"/><path class="k-head" d="M25 1.5 32 5 25 8.5Z"/></svg>';
  }
  // A cell opens on what the paper is: its axis when the site has a rewrite,
  // the way out when only arXiv has it.
  function mark(n) {
    return n.x ? '<span class="lt-ext">' + EXT + "</span>"
               : '<span class="lt-ax">' + (/^P\d$/.test(n.l) ? n.l : "–") + "</span>";
  }
  function cell(n) {
    return '<a class="lt-n' + (n.x ? " is-out" : "") + '" href="' + esc(n.h) + '"' +
      (n.x ? ' target="_blank" rel="noopener noreferrer"' : "") +
      ' data-rail="' + n.r + '" data-lane="' + n.l + '" title="' + esc(n.n) + " · " + ym(n.id) + '">' +
      mark(n) + "<span>" + esc(n.n) + "</span></a>";
  }
  // Each group opens on the line it is drawn with, the key's own mark.
  function group(list, text) {
    return list.length ? '<span class="lt-sub">' + keyLine(text) + (text ? "언급" : "계보") + "</span>" + list.map(cell).join("") : "";
  }
  function column(head, list) {
    return '<div class="lt-col' + (list.length ? "" : " is-empty") + '"><span class="lt-h">' + head + "<b>" + list.length + "</b></span>" +
      group(list.filter(function (n) { return n.r; }), false) +
      group(list.filter(function (n) { return !n.r; }), true) + "</div>";
  }

  box.innerHTML = column("선행", data.before) +
    '<div class="lt-me" data-lane="' + me.l + '"><p class="lt-who">' + mark(me) + esc(me.n) + "</p>" +
    '<p class="lt-tag">' + esc(me.t || "") + '</p><p class="lt-meta"><span>' + ym(me.id) + "</span></p></div>" +
    column("후속", data.after) + "<svg></svg>";

  var narrow = window.matchMedia("(max-width: 760px)");
  var panes = [box.children[0], box.children[2]], cur = data.before.length ? 0 : 1, width = 0, settle;
  var tabs = document.createElement("div");
  tabs.className = "lt-tabs";
  tabs.setAttribute("role", "group");
  tabs.setAttribute("aria-label", "계보 이동");
  tabs.innerHTML = [["선행", data.before.length], ["후속", data.after.length]].map(function (t, i) {
    return '<button type="button" data-pane="' + i + '"' + (t[1] ? "" : " disabled") + "><span>" + t[0] +
      "</span><b>" + t[1] + "</b></button>";
  }).join("");
  frame.insertBefore(tabs, box);
  var buttons = tabs.querySelectorAll("button");

  // An empty side is no pane on a phone, so a pane's place counts only the
  // panes shown.
  function place(i) {
    return panes.filter(function (el) { return !el.classList.contains("is-empty"); }).indexOf(panes[i]);
  }
  function point() {
    each(buttons, function (b, i) { b.setAttribute("aria-current", i === cur ? "true" : "false"); });
  }
  function fit() {
    if (!narrow.matches) { box.style.height = ""; return; }
    var cs = getComputedStyle(box);
    box.style.height = panes[cur].offsetHeight + parseFloat(cs.paddingTop) + parseFloat(cs.paddingBottom) + "px";
  }
  function go(i) {
    cur = i; point();
    box.scrollTo({ left: place(i) * box.clientWidth, behavior: "smooth" });
    // A long pane may have carried the buttons off the top; bring them back.
    if (tabs.getBoundingClientRect().top < 0) tabs.scrollIntoView({ block: "start", behavior: "smooth" });
  }
  tabs.addEventListener("click", function (e) {
    var b = e.target.closest("button");
    if (b && !b.disabled) go(+b.getAttribute("data-pane"));
  });
  box.addEventListener("scroll", function () {
    if (!narrow.matches || !box.clientWidth) return;
    var k = Math.round(box.scrollLeft / box.clientWidth);
    panes.forEach(function (el, i) { if (place(i) === k) cur = i; });
    point();
    clearTimeout(settle);
    settle = setTimeout(fit, 90);
  }, { passive: true });
  point();

  /* The lines are measured off the cells, so they are drawn again whenever
     the columns change size — which includes the moment the tab is first
     shown. Each runs from a cell to the paper and to nowhere else. */
  function lines() {
    // The overlay is the walk's last child; the marks inside the cells are svg too.
    var s = box.lastElementChild, b = box.getBoundingClientRect();
    if (!b.width) return;
    if (narrow.matches) {
      s.innerHTML = "";
      // Only a change of width moves the strip: its height follows the pane.
      if (box.clientWidth !== width) { width = box.clientWidth; box.scrollLeft = place(cur) * width; }
      fit();
      return;
    }
    width = 0; box.style.height = "";
    function at(el) { var r = el.getBoundingClientRect(); return { l: r.left - b.left, r: r.right - b.left, y: r.top - b.top + r.height / 2 }; }
    var cols = box.querySelectorAll(".lt-col"), mid = at(box.querySelector(".lt-me")), d = "";
    // Every line ends in an arrowhead on the newer paper: time runs left to right.
    function line(a, z, rail) {
      var dx = z.l - a.r, x = z.l - 7, cls = rail ? "" : " is-text";
      d += '<path class="lt-edge' + cls + '" d="M' + a.r + " " + a.y +
        "C" + (a.r + dx / 2) + " " + a.y + " " + (x - dx / 2) + " " + z.y + " " + x + " " + z.y + '"/>' +
        '<path class="lt-head' + cls + '" d="M' + x + " " + (z.y - 3.5) + "L" + z.l + " " + z.y + "L" + x + " " + (z.y + 3.5) + 'Z"/>';
    }
    each(cols[0].querySelectorAll(".lt-n"), function (el) { line(at(el), mid, el.getAttribute("data-rail") === "1"); });
    each(cols[1].querySelectorAll(".lt-n"), function (el) { line(mid, at(el), el.getAttribute("data-rail") === "1"); });
    s.setAttribute("width", b.width); s.setAttribute("height", b.height); s.innerHTML = d;
    frame.scrollLeft = Math.max(0, (box.scrollWidth - frame.clientWidth) / 2);
  }

  var still = box.closest("[data-walk]").querySelector("[data-walk-still]");
  if (still) still.hidden = true;
  frame.hidden = false;
  lines();
  if (window.ResizeObserver) new ResizeObserver(lines).observe(box);
  else window.addEventListener("resize", lines);
})();
