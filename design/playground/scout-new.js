/* The scouting redesign: a month calendar of runs and conference dates, the next dates with a countdown, and one run laid out by priority. */
(function () {
  "use strict";
  var RUNS = window.SN_RUNS || [], EVENTS = window.SN_EVENTS || [], PL = window.SN_PILLARS || {};
  var $ = function (id) { return document.getElementById(id); };
  var esc = function (s) { return String(s == null ? "" : s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); };
  var pad = function (n) { return (n < 10 ? "0" : "") + n; };
  var iso = function (d) { return d.getFullYear() + "-" + pad(d.getMonth() + 1) + "-" + pad(d.getDate()); };
  var md = function (s) { return s.slice(5).replace("-", "."); };
  var today = iso(new Date());
  var runByDate = {}; RUNS.forEach(function (r) { runByDate[r.date] = r; });
  var selected = RUNS.length ? RUNS[0].date : null;
  var pick = ""; // the pillar the run is filtered to, "" for all
  var view = selected ? new Date(selected + "T00:00:00") : new Date();
  view.setDate(1);

  function eventsOn(day) { return EVENTS.filter(function (ev) { return ev.start <= day && day <= ev.end; }); }
  function chip(p, rk) { return '<a class="chip pillar" data-p="' + p + '" href="pillar-' + p + '.html" title="' + esc(PL[p] || p) + ' 소개">' + p + "</a>" + (rk ? '<span class="sn-rk">' + esc(rk) + "</span>" : ""); }

  function drawCalendar() {
    var y = view.getFullYear(), m = view.getMonth();
    $("sn-month").textContent = y + "년 " + (m + 1) + "월";
    var first = new Date(y, m, 1), start = (first.getDay() + 6) % 7, days = new Date(y, m + 1, 0).getDate();
    var out = ["월", "화", "수", "목", "금", "토", "일"].map(function (d) { return '<span class="sn-dow">' + d + "</span>"; });
    for (var i = 0; i < start; i++) out.push('<span class="sn-day is-pad"></span>');
    for (var d = 1; d <= days; d++) {
      var key = y + "-" + pad(m + 1) + "-" + pad(d), run = runByDate[key], evs = eventsOn(key);
      var cls = "sn-day" + (run ? " has-run" : "") + (key === selected ? " is-sel" : "") + (key === today ? " is-today" : "");
      var marks = evs.map(function (ev) { return '<i class="mk ' + ev.kind + (ev.ok ? "" : " unsure") + '" title="' + esc(ev.name) + '"></i>'; }).join("");
      var inner = '<span class="sn-dn">' + d + "</span>" + (run ? '<span class="sn-cnt">' + run.items.length + "편</span>" : "") + (marks ? '<span class="sn-mks">' + marks + "</span>" : "");
      var tip = (run ? run.items.length + "편 탐색 회차" : "") + evs.map(function (ev) { return (run ? " · " : "") + ev.name; }).join(" · ");
      out.push(run
        ? '<button type="button" class="' + cls + '" data-run="' + key + '" aria-label="' + (m + 1) + "월 " + d + "일 " + esc(tip) + '">' + inner + "</button>"
        : '<span class="' + cls + '"' + (tip ? ' title="' + esc(tip) + '"' : "") + ">" + inner + "</span>");
    }
    $("sn-grid").innerHTML = out.join("");
  }

  function drawUpcoming() {
    if (!$("sn-up")) return;
    var t0 = new Date(today + "T00:00:00");
    var up = EVENTS.filter(function (ev) { return ev.end >= today; }).slice(0, 6);
    $("sn-up").innerHTML = up.map(function (ev) {
      var dd = Math.round((new Date(ev.start + "T00:00:00") - t0) / 864e5);
      var badge = dd <= 0 ? "진행 중" : "D-" + dd;
      var when = ev.start === ev.end ? md(ev.start) : md(ev.start) + "–" + md(ev.end);
      return '<li class="sn-ev ' + ev.kind + (ev.ok ? "" : " unsure") + '"><a href="' + esc(ev.url) + '" target="_blank" rel="noopener">' +
        '<span class="sn-dd">' + badge + "</span><span class=\"sn-evn\"><b>" + esc(ev.name) + "</b><span>" + esc(when + (ev.place ? " · " + ev.place : "")) + "</span></span>" +
        '<span class="sn-ext" aria-hidden="true">↗</span></a></li>';
    }).join("");
  }

  function paperCard(it) {
    return '<article class="sn-card"><p class="sn-chips">' + it.picks.map(function (k) { return chip(k[0], k[1]); }).join("") + "</p>" +
      '<h3><a href="https://arxiv.org/abs/' + esc(it.id) + '" target="_blank" rel="noopener">' + esc(it.alias) + "</a></h3>" +
      '<p class="sn-title">' + esc(it.title) + "</p>" + (it.gist ? '<p class="sn-gist">' + esc(it.gist) + "</p>" : "") +
      '<p class="sn-tags">' + it.tags.map(function (t) { return "<span>" + esc(t) + "</span>"; }).join("") + '<a class="sn-arx" href="https://arxiv.org/abs/' + esc(it.id) + '" target="_blank" rel="noopener">arXiv ' + esc(it.id) + " ↗</a></p></article>";
  }
  function paperRow(it) {
    return '<li class="sn-row"><span class="sn-chips">' + it.picks.map(function (k) { return chip(k[0], k[1]); }).join("") + "</span>" +
      '<a href="https://arxiv.org/abs/' + esc(it.id) + '" target="_blank" rel="noopener"><b>' + esc(it.alias) + "</b><span>" + esc(it.gist || it.title) + "</span></a>" +
      '<span class="sn-rtag">' + esc(it.tags[0] || "") + "</span></li>";
  }

  function drawRun() {
    var r = runByDate[selected];
    if (!r) { $("sn-run").innerHTML = ""; return; }
    var has = function (it) { return !pick || it.picks.some(function (k) { return k[0] === pick; }); };
    var counts = {}; r.items.forEach(function (it) { it.picks.forEach(function (k) { counts[k[0]] = (counts[k[0]] || 0) + 1; }); });
    var bar = '<div class="sn-lc"><span class="sn-lab" title="연구 축" aria-hidden="true"><svg viewBox="0 0 20 20"><path d="M10 3 3 6.5l7 3.5 7-3.5z"/><path d="M3 10l7 3.5 7-3.5"/><path d="M3 13.5 10 17l7-3.5"/></svg></span>' +
      '<div class="sn-pf" role="group" aria-label="연구 축으로 거르기"><span class="sn-pf-h">연구 축</span>' +
      Object.keys(PL).map(function (p) {
        return '<button type="button" class="rail-item pillar" data-p="' + p + '" data-pf="' + p + '" aria-pressed="' + (pick === p) + '"' + (counts[p] ? "" : " disabled") +
          '><span class="sw"></span><b>' + p + '</b><span class="rl">' + esc(PL[p]) + '</span><span class="rn">' + (counts[p] || 0) + "</span></button>";
      }).join("") + (pick ? '<button type="button" class="sn-pf-x" data-pf="">거르기 해제</button>' : "") + "</div></div>";
    var all = r.items; r = Object.assign({}, r, { items: r.items.filter(has), near: r.near.filter(function (n) { return !pick || n.p === pick; }) });
    var first = r.items.filter(function (it) { return it.group === "shared" || (it.full && it.rank === 1); });
    var more = r.items.filter(function (it) { return first.indexOf(it) < 0 && it.full; });
    var rest = r.items.filter(function (it) { return !it.full; });
    var idx = RUNS.map(function (x) { return x.date; }).indexOf(r.date), prev = RUNS[idx + 1], next = RUNS[idx - 1];
    var arrived = Object.keys(PL).map(function (p) { return r.arrived.indexOf(p) >= 0 ? chip(p) : '<span class="chip pillar is-miss" data-p="' + p + '">' + p + " 대기</span>"; }).join("");
    var strip = '<div class="sn-strip" role="group" aria-label="탐색 회차">' + RUNS.map(function (x) {
      return '<button type="button" data-run="' + x.date + '" aria-pressed="' + (x.date === selected) + '"><b>' + md(x.date) + "</b><span>" + x.items.length + "편</span></button>";
    }).join("") + '<button type="button" class="sn-calbtn" data-side="1" aria-label="달력으로 회차 고르기">달력 ▾</button></div>';
    var nx = EVENTS.filter(function (ev) { return ev.end >= today; })[0], nextLine = "";
    if (nx) {
      var dd = Math.round((new Date(nx.start + "T00:00:00") - new Date(today + "T00:00:00")) / 864e5);
      nextLine = '<p class="sn-next"><span class="sn-dd">' + (dd <= 0 ? "진행 중" : "D-" + dd) + "</span><span>다음 일정 <b>" + esc(nx.name) + '</b></span><a href="#" data-side="1">일정 모두</a></p>';
    }
    // the run strip folds into the heading: the current run shows, tapping it lists every run
    var caret = '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="m4.5 6.5 3.5 3.5 3.5-3.5"/></svg>';
    var runMenu = '<div class="sn-runmenu" role="group" aria-label="탐색 회차" hidden>' + RUNS.map(function (x) {
      return '<button type="button" data-run="' + x.date + '" aria-pressed="' + (x.date === selected) + '"><b>' + md(x.date) + "</b><span>" + x.items.length + "편</span></button>";
    }).join("") + '<button type="button" class="sn-runmenu-cal" data-side="1">달력으로 보기</button></div>';
    var arrow = function (x, dir) {
      return x ? '<button type="button" class="sn-runstep" data-run="' + x.date + '" aria-label="' + (dir < 0 ? "이전" : "다음") + " 회차 " + md(x.date) + '" title="' + md(x.date) + '"><svg viewBox="0 0 16 16" aria-hidden="true"><path d="' + (dir < 0 ? "m10 3.5-4.5 4.5 4.5 4.5" : "m6 3.5 4.5 4.5L6 12.5") + '"/></svg></button>'
        : '<span class="sn-runstep is-off" aria-hidden="true"></span>';
    };
    $("sn-run").innerHTML = nextLine +
      '<header class="sn-run-h"><div><p class="sn-k">탐색 회차</p><div class="sn-runline">' + arrow(prev, -1) +
      '<div class="sn-runpick-w"><h2><button type="button" class="sn-runpick" aria-haspopup="true" aria-expanded="false">' + md(r.date) + " 회차" + caret + "</button></h2>" + runMenu + "</div>" + arrow(next, 1) + '</div><p class="sn-sum">기준을 넘은 ' + r.items.length + "편 가운데 <b>" + first.length + "편</b>을 먼저 권합니다." + (pick ? ' <span class="sn-pf-note">' + esc(PL[pick]) + " 축만 보는 중 · 전체 " + all.length + "편</span>" : "") + "</p></div>" +
      '<div class="sn-step">' + (prev ? '<button type="button" data-run="' + prev.date + '">‹ ' + md(prev.date) + "</button>" : "") + (next ? '<button type="button" data-run="' + next.date + '">' + md(next.date) + " ›</button>" : "") + "</div>" +
      '<p class="sn-arr">' + arrived + "</p></header>" + bar +
      '<section class="sn-blk"><h3 class="sn-h">먼저 읽을 논문 <span>연구 축별 1위와 여러 축이 함께 고른 것</span></h3><div class="sn-cards">' + first.map(paperCard).join("") + "</div></section>" +
      (more.length ? '<section class="sn-blk"><h3 class="sn-h">축별로 더 <span>2·3위와 인접 후보</span></h3><ul class="sn-rows">' + more.map(paperRow).join("") + "</ul></section>" : "") +
      (rest.length ? '<details class="sn-blk sn-fold"><summary>목록에만 오른 논문 ' + rest.length + "편</summary><ul class=\"sn-rows\">" + rest.map(paperRow).join("") + "</ul></details>" : "") +
      (r.near.length ? '<details class="sn-blk sn-fold"><summary>근접 후보 ' + r.near.length + "편 · 조건이 채워지면 다시 봅니다</summary><ul class=\"sn-near\">" +
        r.near.map(function (n) { return "<li>" + chip(n.p) + "<b>" + esc(n.alias) + "</b><span>" + esc(n.cond) + "</span></li>"; }).join("") + "</ul></details>" : "") +
      '<button type="button" class="sn-more-side" data-side="1">달력으로 회차 고르기</button>';
  }

  // phone: the filter line scrolls sideways; drop the edge fade once its end is in view
  document.addEventListener("keydown", function (e) { var m = document.querySelector(".sn-runmenu"); if (e.key === "Escape" && m && !m.hidden) { m.hidden = true; document.querySelector(".sn-runpick").setAttribute("aria-expanded", "false"); } });
  document.addEventListener("scroll", function (e) { var t = e.target; if (t && t.classList && t.classList.contains("sn-pf")) t.classList.toggle("at-end", t.scrollLeft + t.clientWidth >= t.scrollWidth - 4); }, true);
  document.addEventListener("click", function (e) {
    var menu = document.querySelector(".sn-runmenu"), pk = e.target.closest(".sn-runpick");
    if (menu && (pk || !e.target.closest(".sn-runmenu") || e.target.closest(".sn-runmenu-cal"))) {
      var on = !!pk && menu.hidden; menu.hidden = !on;
      var bt = document.querySelector(".sn-runpick"); if (bt) bt.setAttribute("aria-expanded", on ? "true" : "false");
      if (pk) return;
    }
    var t = e.target.closest("[data-run]");
    if (t) { var mm = document.querySelector(".sn.show-side"); if (mm && window.innerWidth > 680) mm.classList.remove("show-side"); selected = t.getAttribute("data-run"); var d = new Date(selected + "T00:00:00"); view = new Date(d.getFullYear(), d.getMonth(), 1); drawCalendar(); drawRun(); return; }
    var pf = e.target.closest("[data-pf]");
    if (pf) { var v = pf.getAttribute("data-pf"); pick = (pick === v) ? "" : v; drawRun(); return; }
    var sd = e.target.closest("[data-side]");
    if (sd) { e.preventDefault(); var m = document.querySelector(".sn"); m.classList.toggle("show-side"); if (m.classList.contains("show-side") && window.innerWidth <= 680) document.querySelector(".sn-side").scrollIntoView({ behavior: "smooth" }); return; }
    if (!e.target.closest(".sn-side")) { var m2 = document.querySelector(".sn.show-side"); if (m2 && window.innerWidth > 680) m2.classList.remove("show-side"); }
    var n = e.target.closest("[data-cal]");
    if (n) { view = new Date(view.getFullYear(), view.getMonth() + +n.getAttribute("data-cal"), 1); drawCalendar(); }
  });
  drawCalendar(); drawUpcoming(); drawRun();
})();
