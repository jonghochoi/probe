/* 계보 — the cells in a paper's 계보 tab.

   The tab arrives with a printed drawing of the paper between the older
   papers it is joined to and the newer ones, and with those same papers as
   JSON (`pages._lineage_data`). This file replaces the drawing with three
   columns of cells — 선행, the paper, 후속 — and in each column sets the
   papers a lineage rail names above the ones only the prose mentions. It
   reads the graph and decides nothing about it.

   Every cell is a link — to the other paper's 계보 tab, or to arXiv for a
   paper with no rewrite — so walking the graph is moving from page to page.

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
    return '<div class="lt-col"><span class="lt-h">' + head + "<b>" + list.length + "</b></span>" +
      group(list.filter(function (n) { return n.r; }), false) +
      group(list.filter(function (n) { return !n.r; }), true) + "</div>";
  }

  box.innerHTML = column("선행", data.before) +
    '<div class="lt-me" data-lane="' + me.l + '"><p class="lt-who">' + mark(me) + esc(me.n) + "</p>" +
    '<p class="lt-tag">' + esc(me.t || "") + '</p><p class="lt-meta"><span>' + ym(me.id) + "</span></p></div>" +
    column("후속", data.after) + "<svg></svg>";

  /* The lines are measured off the cells, so they are drawn again whenever
     the columns change size — which includes the moment the tab is first
     shown. Each runs from a cell to the paper and to nowhere else. */
  function lines() {
    // The overlay is the walk's last child; the marks inside the cells are svg too.
    var s = box.lastElementChild, b = box.getBoundingClientRect();
    if (!b.width) return;
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
