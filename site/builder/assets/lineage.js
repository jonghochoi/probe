/* 계보 — one paper lit on the map, and the card that names what is lit.

   The map arrives drawn (`builder/lineage.py`): every node is a link carrying
   `data-id`, every line carries the two ids it joins. This file computes
   nothing about the graph but who is next to whom, read off those lines.

   Pointing at a node lights it, its parents and its children; clicking one
   keeps it lit and fills the card above the map, whose link is the one the
   click would otherwise have followed. A name in a card or in a list under
   the map lights that node the same way. `#<arXiv id>` in the address lights
   a node on arrival, which is how a paper's own page sends a reader here.

   The axis chips set back every node filed under none of the pressed axes.

   Without this file the page is the same map, every node a plain link. */

(function () {
  "use strict";
  var frame = document.getElementById("gm-frame");
  var card = document.getElementById("gm-card");
  var svg = frame && frame.querySelector(".gm-svg");
  if (!svg || !card) return;

  var each = function (list, fn) { Array.prototype.forEach.call(list, fn); };
  var nodes = {}, up = {}, down = {};
  each(svg.querySelectorAll(".gm-node"), function (el) {
    var id = el.getAttribute("data-id");
    nodes[id] = el; up[id] = []; down[id] = [];
  });
  var edges = svg.querySelectorAll(".gm-edge");
  each(edges, function (el) {
    var a = el.getAttribute("data-a"), b = el.getAttribute("data-b");
    down[a].push(b); up[b].push(a);
  });

  var papers = {};
  ((window.ProbeIndex || {}).papers || []).forEach(function (p) { papers[p.id] = p; });

  var kept = null, pointed = null, axes = {};

  function esc(s) {
    return String(s).replace(/[&<>"]/g, function (ch) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[ch];
    });
  }
  function isOut(id) { return nodes[id].classList.contains("is-out"); }
  function name(id) { return nodes[id].getAttribute("data-name"); }

  function pick(id) {
    return '<button type="button" class="gm-pick' + (isOut(id) ? " is-out" : "") +
      '" data-go="' + id + '">' + esc(name(id)) + "</button>";
  }
  function column(head, ids, empty) {
    return '<div><p class="gm-col-h">' + head + " <b>" + ids.length + "</b></p>" +
      (ids.length ? '<div class="gm-picks">' + ids.map(pick).join("") + "</div>"
                  : '<p class="gm-none">' + empty + "</p>") + "</div>";
  }
  function fill(id) {
    card.hidden = false;
    if (!id) {
      card.innerHTML = '<div><p class="gm-who">논문을 고르세요</p><p class="gm-tag">' +
        "지도의 원이나 아래 목록의 이름을 누르면 그 논문이 딛고 선 것과 그 논문을 딛는 것이 여기에 나옵니다.</p></div>";
      return;
    }
    var href = nodes[id].getAttribute("href"), p = papers[id], head;
    if (isOut(id)) {
      head = '<p class="gm-who">' + esc(name(id)) + '</p><p class="gm-ttl">재작성본이 없는 논문입니다</p>' +
        '<p class="gm-meta"><span class="gm-id">' + id + '</span><a href="' + href +
        '" target="_blank" rel="noopener noreferrer">arXiv 원문</a></p>';
    } else {
      var chips = ((p && p.pillars) || []).map(function (x) {
        return '<span class="chip pillar" data-p="' + x + '">' + x + "</span>";
      }).join("");
      head = '<p class="gm-who">' + esc(name(id)) + "</p>" +
        (p ? '<p class="gm-ttl">' + esc(p.title) + '</p><p class="gm-tag">' + esc(p.tagline) + "</p>" : "") +
        '<p class="gm-meta">' + chips + '<span class="gm-id">' + id + '</span><a href="' + href + '">재작성본 읽기</a></p>';
    }
    card.innerHTML = "<div>" + head + "</div>" +
      column("딛고 선 것", up[id].slice().sort(), "지도에 그려진 조상이 없습니다") +
      column("이 논문을 딛는 것", down[id].slice().sort(), "아직 없습니다");
  }

  var shown;
  function paint() {
    var lit = pointed || kept;
    var pressed = Object.keys(axes).filter(function (k) { return axes[k]; });
    svg.classList.toggle("is-lit", !!lit);
    Object.keys(nodes).forEach(function (id) {
      var el = nodes[id], own = (el.getAttribute("data-p") || "").split(" ");
      el.classList.toggle("is-on", !!lit && (id === lit || up[lit].indexOf(id) >= 0 || down[lit].indexOf(id) >= 0));
      el.classList.toggle("is-me", id === lit);
      el.classList.toggle("is-off", pressed.length > 0 &&
        !pressed.some(function (k) { return own.indexOf(k) >= 0; }));
    });
    each(edges, function (el) {
      el.classList.toggle("is-up", !!lit && el.getAttribute("data-b") === lit);
      el.classList.toggle("is-down", !!lit && el.getAttribute("data-a") === lit);
    });
    if (lit !== shown) { shown = lit; fill(lit); }
  }

  function centre(id) {
    var x = +nodes[id].querySelector("circle").getAttribute("cx");
    frame.scrollLeft = Math.max(0, x - frame.clientWidth / 2);
  }
  function keep(id, scroll) {
    if (!nodes[id]) return;
    kept = id; pointed = null; paint();
    if (scroll) centre(id);
  }

  svg.addEventListener("click", function (e) {
    var el = e.target.closest(".gm-node");
    // A modified click is a reader opening the link elsewhere; let it through.
    if (e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
    if (el) { e.preventDefault(); keep(el.getAttribute("data-id")); }
    else { kept = null; paint(); }
  });
  svg.addEventListener("mouseover", function (e) {
    var el = e.target.closest(".gm-node"), id = el ? el.getAttribute("data-id") : null;
    if (id !== pointed) { pointed = id; paint(); }
  });
  svg.addEventListener("mouseleave", function () { if (pointed) { pointed = null; paint(); } });
  document.addEventListener("click", function (e) {
    var el = e.target.closest("[data-go]");
    if (!el || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
    if (!nodes[el.getAttribute("data-go")]) return;
    e.preventDefault();
    keep(el.getAttribute("data-go"), true);
  });
  each(document.querySelectorAll(".gm-filter [data-p]"), function (btn) {
    btn.addEventListener("click", function () {
      var k = btn.getAttribute("data-p");
      axes[k] = !axes[k];
      btn.setAttribute("aria-pressed", String(!!axes[k]));
      paint();
    });
  });

  function fromHash() {
    var id = decodeURIComponent(location.hash.slice(1));
    if (nodes[id]) { keep(id, true); return true; }
    return false;
  }
  window.addEventListener("hashchange", fromHash);
  paint();
  // No paper named in the address: open on the newest end of the map, where
  // the corpus is, rather than on its oldest ancestors.
  if (!fromHash()) frame.scrollLeft = frame.scrollWidth;
})();
