/* The scouting redesign: a month calendar of runs and conference dates, the next dates with a countdown, and one run laid out by priority. */
(function () {
  "use strict";
  var RUNS = window.SN_RUNS || [], EVENTS = window.SN_EVENTS || [], PL = window.SN_PILLARS || {};
  var $ = function (id) { return document.getElementById(id); };
  // the playground sets these; unset, the page reads its trimmed defaults
  var CAL_ICON = '<svg viewBox="0 0 20 20"><rect x="3" y="4.5" width="14" height="12.5" rx="2"/><path d="M3 8.5h14M7 2.8v3.4M13 2.8v3.4"/></svg>';
  var X_ICON = '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="m4 4 8 8M12 4l-8 8"/></svg>';
  // each recommended paper's overview figure, picked from its arXiv HTML for the playground
  var FIGS = {};
  fetch("assets/scout-figs.json").then(function (r) { return r.json(); }).then(function (d) { FIGS = d || {}; if (window.snRedraw) window.snRedraw(); }).catch(function () {});
  var opt = function (k, d) { var o = window.SN_OPTS || {}; return o[k] || d; };
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
  // an axis chip and what that axis made of the paper: text after it, a bare number, one pill, a numbered badge, or (in the table) a column of its own
  function chip(p, rk) {
    var how = opt("rankStyle", "pill"), n = rk && /^(\d)위$/.exec(rk), a = '<a class="chip pillar" data-p="' + p + '" href="pillar-' + p + '.html" title="' + esc(PL[p] || p) + ' 소개"';
    if (rk && how === "pill") return '<a class="chip pillar sn-chip-rk" data-p="' + p + '" href="pillar-' + p + '.html" title="' + esc(PL[p] || p) + ' 소개">' + p + "<i>·</i>" + esc(rk) + "</a>";
    if (n && how === "badge") return '<span class="sn-bw">' + a + ">" + p + '</a><span class="sn-badge" aria-label="' + esc(rk) + '">' + n[1] + "</span></span>";
    if (n && how === "num") rk = n[1];
    return a + ">" + p + "</a>" + (rk ? '<span class="sn-rk' + (n && how === "num" ? " is-num" : "") + '">' + esc(rk) + "</span>" : "");
  }

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
    // the title opens the detail and carries the full title on hover; the arXiv number links out
    var full = opt("card", "full") === "full", tags = opt("tags", "card") !== "none";
    // "1위" is what the section title already says; a second axis's mark stays
    var ranks = opt("rank", "show") === "trim";
    var fig = FIGS[it.id], how = opt("fig", "thumb"), figHtml = fig && (how === "thumb" || how === "cover") ? '<div class="sn-fig sn-fig-' + how + '"><img src="' + esc(fig.src) + '" alt="" loading="lazy"></div>' : "";
    return '<article class="sn-card' + (fig && how === "cover" ? " has-cover" : "") + '" data-card="' + esc(it.id) + '">' + (how === "cover" ? figHtml : "") + '<div class="sn-ctop"><p class="sn-chips">' + it.picks.map(function (k) { return chip(k[0], ranks && k[1] === "1위" ? "" : k[1]); }).join("") + "</p>" +
      '<a class="sn-id" href="https://arxiv.org/abs/' + esc(it.id) + '" target="_blank" rel="noopener">' + esc(it.id) + "</a></div>" +
      '<h3><a href="#p-' + esc(it.id) + '" data-detail="' + esc(it.id) + '" title="' + esc(it.title) + '">' + esc(it.alias) + "</a></h3>" +
      (how === "thumb" ? figHtml : "") + (full ? '<p class="sn-title">' + esc(it.title) + "</p>" : "") + (it.gist ? '<p class="sn-gist">' + esc(it.gist) + "</p>" : "") +
      (tags ? '<p class="sn-tags">' + (tags ? it.tags.map(function (t) { return "<span>" + esc(t) + "</span>"; }).join("") : "") +
        "</p>" : "") + "</article>";
  }
  function paperRow(it) {
    // the analysis list's table row: the arXiv number, the title over its line, the axis with its rank
    if (opt("rows", "table") === "table")
      return '<li class="sn-tr" data-card="' + esc(it.id) + '"><a class="sn-tid" href="https://arxiv.org/abs/' + esc(it.id) + '" target="_blank" rel="noopener">' + esc(it.id) + "</a>" +
        '<a class="sn-tmain" href="#p-' + esc(it.id) + '" data-detail="' + esc(it.id) + '" title="' + esc(it.title) + '"><span class="sn-tt">' + esc(it.alias) + '</span><span class="sn-tg">' + esc(it.gist || it.title) + "</span></a>" +
        (opt("rankStyle", "pill") === "column" ? (function (r0) { var nn = /^(\d)위$/.exec(r0); return '<span class="sn-trk' + (nn ? " is-n" : "") + '">' + esc(nn ? nn[1] : r0) + "</span>"; })((it.picks[0] || [])[1] || "") : "") +
        '<span class="sn-tp">' + it.picks.map(function (k, i) { return chip(k[0], opt("rankStyle", "pill") === "column" && i === 0 ? "" : k[1]); }).join("") + "</span></li>";
    return '<li class="sn-row" data-card="' + esc(it.id) + '"><span class="sn-chips">' + it.picks.map(function (k) { return chip(k[0], k[1]); }).join("") + "</span>" +
      '<a href="#p-' + esc(it.id) + '" data-detail="' + esc(it.id) + '"><b>' + esc(it.alias) + "</b><span>" + esc(it.gist || it.title) + "</span></a>" +
      (opt("tags", "card") === "all" ? '<span class="sn-rtag">' + esc(it.tags[0] || "") + "</span>" : '<a class="sn-id" href="https://arxiv.org/abs/' + esc(it.id) + '" target="_blank" rel="noopener">' + esc(it.id) + "</a>") + "</li>";
  }

  // what one date in the date line says: the date and its paper count, the date alone, days under a month label,
  // the date with a dot per recommended paper, or the date over its count
  function dateItems() {
    var how = opt("dates", "count"), lastM = "";
    var recs = function (x) { return x.items.filter(function (it) { return it.group === "shared" || (it.full && it.rank === 1); }).length; };
    return RUNS.map(function (x) {
      var on = x.date === selected, m = +x.date.slice(5, 7), d = +x.date.slice(8, 10), lead = "", inner;
      if (how === "month") { if (m + "" !== lastM) { lead = '<span class="sn-dm">' + m + "월</span>"; lastM = m + ""; } inner = "<b>" + d + "</b>"; }
      else if (how === "plain") inner = "<b>" + md(x.date) + "</b>";
      else if (how === "dots") inner = "<b>" + md(x.date) + '</b><span class="sn-dots" aria-hidden="true">' + new Array(recs(x) + 1).join("<i></i>") + "</span>";
      else if (how === "stack") inner = "<b>" + md(x.date) + '</b><span class="rn">' + x.items.length + "편</span>";
      else inner = "<b>" + md(x.date) + '</b><span class="rn">' + x.items.length + "</span>";
      return lead + '<button type="button" class="rail-item" data-run="' + x.date + '" aria-pressed="' + on + '" aria-label="' + m + "월 " + d + "일 회차, " + x.items.length + '편">' + inner + "</button>";
    }).join("");
  }

  function drawRun() {
    closeDetail();
    var r = runByDate[selected];
    if (!r) { $("sn-run").innerHTML = ""; return; }
    // section titles follow the first screen's rule: a short noun, then a grey line
    var NAMES = opt("names", "none") === "now"
      ? { first: "먼저 읽을 논문|연구 축별 1위와 여러 축이 함께 고른 것", more: "축별로 더|2·3위와 인접 후보", rest: "목록에만 오른 논문 #편|", near: "근접 후보 #편 · 조건이 채워지면 다시 봅니다|" }
      : { first: "추천|축별 1위", more: "후보|축별 2·3위", rest: "기타|목록에만 오른 #편", near: "보류|조건을 기다리는 #편" };
    var noTitles = opt("names", "none") === "none";
    var name = function (k, n) { var p = NAMES[k].replace("#", n).split("|"); return esc(p[0]) + (p[1] ? " <span>" + esc(p[1]) + "</span>" : ""); };
    var folds = opt("folds", "hide") === "show";
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
    // the run picker sits at the filter line's right end, where the list page keeps its count
    var showFilter = opt("filter", "hide") === "show", spot = opt("runSpot", "date");
    if (spot === "bar" && !showFilter) spot = "date";
    if (!showFilter) bar = "";
    var inBar = spot === "bar";
    // the run dates in the filter line's place: one tap a run, the calendar at the end
    if (spot === "date") bar = '<div class="sn-lc sn-lc-date"><button type="button" class="sn-lab sn-lab-btn" data-side="1" title="달력으로 보기" aria-label="달력으로 보기">' + CAL_ICON + "</button>" +
      '<div class="sn-pf sn-dates is-' + opt("dates", "count") + '" role="group" aria-label="탐색 회차">' + dateItems() + '</div></div>' + bar;
    if (inBar) bar = bar.slice(0, -6) + '<div class="sn-runcell">' + arrow(prev, -1) + '<div class="sn-runpick-w"><button type="button" class="sn-runpick" aria-haspopup="true" aria-expanded="false">' +
      md(r.date) + '<span class="sn-runw"> 회차</span>' + caret + "</button>" + runMenu + "</div>" + arrow(next, 1) + "</div></div>";
    var sumLine = '<p class="sn-sum">' + (opt("head", "short") === "full" ? "기준을 넘은 " + r.items.length + "편 가운데 <b>" + first.length + "편</b>을 먼저 권합니다." : r.items.length + "편 중 <b>" + first.length + "편</b> 추천") + "</p>";
    $("sn-run").innerHTML = nextLine + (inBar || spot === "date" ? "" :
      '<header class="sn-run-h"><div>' + (opt("head", "short") === "full" ? '<p class="sn-k">탐색 회차</p>' : "") + '<div class="sn-runline">' + arrow(prev, -1) +
      '<div class="sn-runpick-w"><h2><button type="button" class="sn-runpick" aria-haspopup="true" aria-expanded="false">' + md(r.date) + " 회차" + caret + "</button></h2>" + runMenu + "</div>" + arrow(next, 1) + '</div><p class="sn-sum">' + (opt("head", "short") === "full" ? "기준을 넘은 " + r.items.length + "편 가운데 <b>" + first.length + "편</b>을 먼저 권합니다." : r.items.length + "편 중 <b>" + first.length + "편</b> 추천") + (pick ? ' <span class="sn-pf-note">' + esc(PL[pick]) + " 축만 보는 중 · 전체 " + all.length + "편</span>" : "") + "</p></div>" +
      '<div class="sn-step">' + (prev ? '<button type="button" data-run="' + prev.date + '">‹ ' + md(prev.date) + "</button>" : "") + (next ? '<button type="button" data-run="' + next.date + '">' + md(next.date) + " ›</button>" : "") + "</div>" +
      '<p class="sn-arr">' + arrived + "</p></header>") + bar +
      '<section class="sn-blk">' + (noTitles ? "" : '<h3 class="sn-h">' + name("first") + "</h3>") + '<div class="sn-cards' + (opt("cards", "even") === "even" ? " is-even" : "") + '" style="--cols:' + Math.ceil(first.length / Math.ceil(first.length / 4 || 1)) + '">' + first.map(paperCard).join("") + "</div></section>" +
      (more.length ? '<section class="sn-blk">' + (noTitles ? "" : '<h3 class="sn-h">' + name("more") + "</h3>") + (opt("rows", "table") === "table" ? '<div class="sn-lh' + (opt("rankStyle", "pill") === "column" ? " has-rk" : "") + '" aria-hidden="true"><span>arXiv</span><span>논문 · 한 줄</span>' + (opt("rankStyle", "pill") === "column" ? "<span>순위</span>" : "") + '<span>연구 축</span></div><ul class="sn-rows sn-tbl' + (opt("rankStyle", "pill") === "column" ? " has-rk" : "") + '">' : '<ul class="sn-rows">') + more.map(paperRow).join("") + "</ul></section>" : "") +
      (folds && rest.length ? '<details class="sn-blk sn-fold"><summary>' + name("rest", rest.length) + "</summary><ul class=\"sn-rows\">" + rest.map(paperRow).join("") + "</ul></details>" : "") +
      (folds && r.near.length ? '<details class="sn-blk sn-fold"><summary>' + name("near", r.near.length) + "</summary><ul class=\"sn-near\">" +
        r.near.map(function (n) { return "<li>" + chip(n.p) + "<b>" + esc(n.alias) + "</b><span>" + esc(n.cond) + "</span></li>"; }).join("") + "</ul></details>" : "") +
      '<button type="button" class="sn-more-side" data-side="1">달력으로 회차 고르기</button>';
    var dl = document.querySelector(".sn-dates"), on = dl && dl.querySelector('[aria-pressed="true"]');
    if (on && dl.scrollWidth > dl.clientWidth) dl.scrollLeft = Math.max(0, on.offsetLeft - dl.clientWidth / 2 + on.offsetWidth / 2);
  }

  // detail: the built run page already carries each paper's brief, so fetch that page once per run and lift the item out
  var DETAIL = {};
  function detailFor(date, id, cb) {
    if (DETAIL[date]) return cb(DETAIL[date][id] || "");
    var url = new URL("s/" + date + "/index.html", document.baseURI).href;
    fetch(url).then(function (r) { return r.text(); }).then(function (t) {
      var d = new DOMParser().parseFromString(t, "text/html"), m = {};
      [].forEach.call(d.querySelectorAll("details.sc-item"), function (el) {
        var b = el.querySelector(".sc-body"); if (!b) return;
        [].forEach.call(b.querySelectorAll("[href]"), function (a) { if (a.getAttribute("href").charAt(0) !== "#") a.setAttribute("href", new URL(a.getAttribute("href"), url).href); });
        [].forEach.call(b.querySelectorAll("[src]"), function (a) { a.setAttribute("src", new URL(a.getAttribute("src"), url).href); });
        m[el.id.replace(/^p-/, "")] = b.innerHTML;
      });
      DETAIL[date] = m; cb(m[id] || "");
    }).catch(function () { cb(""); });
  }
  // the run page's brief, read into parts so it can be laid out more than one way
  function parseDetail(html) {
    var d = new DOMParser().parseFromString("<div>" + html + "</div>", "text/html").body.firstChild;
    var inner = function (el) { return el ? el.innerHTML.trim() : ""; };
    var steps = [].map.call(d.querySelectorAll(".sc-bstep"), function (st) {
      return { name: st.getAttribute("data-step") || inner(st.querySelector(".sc-bstep-h")), fields: [].map.call(st.querySelectorAll(".sc-bf"), function (f) {
        var dd = f.querySelector("dd"), p = dd && dd.querySelector("p");
        return { label: inner(f.querySelector("dt")), lead: p ? inner(p) : "", items: dd ? [].map.call(dd.querySelectorAll(":scope > ul > li"), inner) : [] };
      }) };
    });
    var axes = [].map.call(d.querySelectorAll(".sc-ax"), function (a) {
      var h = a.querySelector(".sc-ax-h"), chip = h && h.querySelector(".chip"), spans = h ? h.querySelectorAll(":scope > span") : [];
      return { chip: chip ? chip.outerHTML : "", head: spans.length ? inner(spans[spans.length - 1]) : "", items: [].map.call(a.querySelectorAll(":scope > ul > li"), inner) };
    });
    var check = d.querySelector(".sc-check");
    return { steps: steps, axes: axes, checks: check ? [].map.call(check.querySelectorAll(":scope > ul > li"), inner) : [], links: inner(d.querySelector(".sc-links")) };
  }
  // a lead line that only announces its bullets, or that restates the header's one-liner, is left out
  var words = function (t) { return (String(t).replace(/<[^>]+>/g, "").match(/[가-힣A-Za-z0-9]{2,}/g) || []); };
  function trimFields(fields, gist) {
    var gw = words(gist);
    return fields.map(function (f) {
      var plain = f.lead.replace(/<[^>]+>/g, "").trim(), lw = words(plain), shared = gw.filter(function (w) { return lw.indexOf(w) >= 0; }).length;
      var filler = f.items.length && plain.length < 22, repeat = gw.length && shared >= Math.max(2, Math.ceil(gw.length / 2));
      return { label: f.label, lead: filler || repeat ? "" : f.lead, items: f.items };
    });
  }
  function renderDetail(html, ctx) {
    ctx = ctx || {};
    var how = opt("detailStyle", "tabs4");
    if (how === "site") return '<div class="sc-body">' + html + "</div>";
    var D = parseDetail(html);
    var list = function (items) { return items.length ? "<ul>" + items.map(function (i) { return "<li>" + i + "</li>"; }).join("") + "</ul>" : ""; };
    var field = function (f) { return '<div class="dx-f"><b class="dx-l">' + f.label + '</b><div class="dx-c">' + (f.lead ? '<p class="dx-lead">' + f.lead + "</p>" : "") + list(f.items) + "</div></div>"; };
    var axisHtml = function (a) { return '<div class="dx-ax"><p class="dx-ax-h">' + a.chip + "<span>" + a.head + "</span></p>" + list(a.items) + "</div>"; };
    var steps = D.steps.map(function (st) { return '<section class="dx-step"><h4 class="dx-sh">' + st.name + "</h4>" + st.fields.map(field).join("") + "</section>"; }).join("");
    var axes = D.axes.length ? '<section class="dx-blk"><h4 class="dx-h">연구 축별 시사점</h4>' + D.axes.map(axisHtml).join("") + "</section>" : "";
    var checks = D.checks.length ? '<section class="dx-blk dx-check"><h4 class="dx-h">먼저 확인할 점</h4>' + list(D.checks) + "</section>" : "";
    var foot = D.links ? '<p class="dx-links">' + D.links + "</p>" : "";
    if (how === "brief") {
      var all = []; D.steps.forEach(function (st) { st.fields.forEach(function (f) { all.push(f); }); });
      var pickF = function (lbl) { return all.filter(function (f) { return f.label.replace(/\s/g, "") === lbl; })[0]; };
      var glance = ["문제", "핵심 방법", "핵심 기여", "가치"].map(function (l) { var f = pickF(l.replace(/\s/g, "")); return f && f.lead ? "<dt>" + l + "</dt><dd>" + f.lead + "</dd>" : ""; }).join("");
      return '<div class="dx dx-brief"><section class="dx-glance"><h4 class="dx-h">한눈에</h4><dl>' + glance + "</dl></section>" + axes + checks +
        D.steps.map(function (st, i) { return '<details class="dx-more"' + (i ? "" : "") + "><summary><b>" + st.name + "</b><span>" + st.fields.map(function (f) { return f.label; }).join(" · ") + "</span></summary>" + st.fields.map(field).join("") + "</details>"; }).join("") + foot + "</div>";
    }
    var byLabel = {}; D.steps.forEach(function (st) { trimFields(st.fields, ctx.gist).forEach(function (f) { byLabel[f.label.replace(/\s/g, "")] = f; }); });
    var fieldsOf = function (labels) { return labels.map(function (l) { return byLabel[l.replace(/\s/g, "")]; }).filter(Boolean); };
    var tabbed = function (cls, tabs) {
      tabs = tabs.filter(function (t) { return t.body; });
      return '<div class="dx dx-tabs ' + cls + '"><div class="dx-tabbar" role="tablist">' + tabs.map(function (t, i) {
        return '<button type="button" role="tab" data-dx-tab="' + t.key + '" aria-selected="' + (i === 0) + '">' + t.name + (t.n ? '<span class="dx-tn">' + t.n + "</span>" : "") + "</button>";
      }).join("") + "</div>" + tabs.map(function (t, i) { return '<div class="dx-pane' + (t.cls ? " " + t.cls : "") + '" data-dx-pane="' + t.key + '"' + (i ? " hidden" : "") + ">" + t.body + "</div>"; }).join("") + foot + "</div>";
    };
    var folded = function (f) {
      var more = f.items.length ? '<details class="dx-fold"><summary>' + (f.lead ? "자세히" : f.items.length + "가지") + '<span class="dx-tn">' + f.items.length + "</span></summary>" + list(f.items) + "</details>" : "";
      return '<div class="dx-f"><b class="dx-l">' + f.label + '</b><div class="dx-c">' + (f.lead ? '<p class="dx-lead">' + f.lead + "</p>" : "") + more + "</div></div>";
    };
    var axesBody = D.axes.map(axisHtml).join(""), checkBody = D.checks.length ? '<div class="dx-check">' + list(D.checks) + "</div>" : "";
    var usBody = (axesBody ? '<h4 class="dx-h">연구 축별 시사점</h4>' + axesBody : "") + (checkBody ? '<h4 class="dx-h dx-h2">먼저 확인할 점</h4>' + checkBody : "");
    if (how === "tabs4") return tabbed("dx-t4", [
      { key: "q", name: "문제", body: fieldsOf(["문제", "기존 한계"]).map(field).join("") },
      { key: "m", name: "방법", body: fieldsOf(["핵심 방법", "차별점"]).map(field).join("") },
      { key: "r", name: "결과", body: fieldsOf(["핵심 기여", "가치"]).map(field).join("") },
      { key: "u", name: "우리에게", n: D.checks.length ? String(D.checks.length) : "", body: usBody }]);
    if (how === "tabs2") return tabbed("dx-t2", [
      { key: "u", name: "판단", n: D.checks.length ? String(D.checks.length) : "", body: usBody },
      { key: "b", name: "요지", body: D.steps.map(function (st) { return '<section class="dx-step"><h4 class="dx-sh">' + st.name + "</h4>" + fieldsOf(st.fields.map(function (f) { return f.label; })).map(folded).join("") + "</section>"; }).join("") }]);
    if (how === "tabsfig") return tabbed("dx-tf", [
      { key: "o", name: "개요", body: (ctx.fig || "") + '<dl class="dx-glance-l">' + fieldsOf(["문제", "핵심 방법", "가치"]).filter(function (f) { return f.lead; }).map(function (f) { return "<dt>" + f.label + "</dt><dd>" + f.lead + "</dd>"; }).join("") + "</dl>" },
      { key: "d", name: "방법 · 결과", body: fieldsOf(["기존 한계", "핵심 방법", "차별점", "핵심 기여"]).map(field).join("") },
      { key: "u", name: "우리에게", n: D.checks.length ? String(D.checks.length) : "", body: usBody }]);
    if (how === "tabs") {
      var T = [["brief", "요지", D.steps.length], ["axes", "시사점", D.axes.length], ["check", "확인할 점", D.checks.length]].filter(function (t) { return t[2]; });
      return '<div class="dx dx-tabs"><div class="dx-tabbar" role="tablist">' + T.map(function (t, i) { return '<button type="button" role="tab" data-dx-tab="' + t[0] + '" aria-selected="' + (i === 0) + '">' + t[1] + "</button>"; }).join("") + "</div>" +
        '<div class="dx-pane" data-dx-pane="brief">' + steps + "</div>" + '<div class="dx-pane" data-dx-pane="axes" hidden>' + D.axes.map(axisHtml).join("") + "</div>" +
        '<div class="dx-pane dx-check" data-dx-pane="check" hidden>' + list(D.checks) + "</div>" + foot + "</div>";
    }
    if (how === "cards") {
      var cards = []; D.steps.forEach(function (st) { st.fields.forEach(function (f) { cards.push('<div class="dx-card"><p class="dx-eb">' + st.name + "</p><h5>" + f.label + "</h5>" + (f.lead ? '<p class="dx-lead">' + f.lead + "</p>" : "") + list(f.items) + "</div>"); }); });
      return '<div class="dx dx-cards"><div class="dx-grid">' + cards.join("") + "</div>" +
        (D.axes.length ? '<div class="dx-grid dx-grid-ax">' + D.axes.map(function (a) { return '<div class="dx-card dx-card-ax">' + axisHtml(a) + "</div>"; }).join("") + "</div>" : "") +
        (D.checks.length ? '<div class="dx-card dx-card-check"><h5>먼저 확인할 점</h5>' + list(D.checks) + "</div>" : "") + foot + "</div>";
    }
    return '<div class="dx dx-flow">' + steps + axes + checks + foot + "</div>";
  }
  function closeDetail() {
    [].forEach.call(document.querySelectorAll(".sn-dw, .sn-inl"), function (n) { n.remove(); });
    [].forEach.call(document.querySelectorAll(".is-open[data-card]"), function (n) { n.classList.remove("is-open"); });
    document.documentElement.classList.remove("sn-dw-on");
  }
  function openDetail(id) {
    var r = runByDate[selected], it = r && r.items.filter(function (x) { return x.id === id; })[0]; if (!it) return;
    var host = document.querySelector('[data-card="' + id + '"]'), was = host && host.classList.contains("is-open");
    closeDetail(); if (was) return;
    if (!document.querySelector('link[data-sc-css]')) { var l = document.createElement("link"); l.rel = "stylesheet"; l.href = "assets/scout.css"; l.setAttribute("data-sc-css", ""); document.head.appendChild(l); }
    var head = '<p class="sn-chips">' + it.picks.map(function (k) { return chip(k[0], k[1]); }).join("") + "</p>" +
      '<a class="sn-id" href="https://arxiv.org/abs/' + esc(it.id) + '" target="_blank" rel="noopener">arXiv ' + esc(it.id) + " ↗</a>";
    var f = FIGS[id], figBlock = f ? '<figure class="sn-dt-fig"><img src="' + esc(f.src) + '" alt=""><figcaption>' + esc(f.caption) + "<span>" + esc(f.source) + "</span></figcaption></figure>" : "";
    var figInTab = opt("detailStyle", "tabs4") === "tabsfig";
    var box = (figInTab ? "" : figBlock) + '<div class="sn-dt-body sc-body-host"><p class="sn-dt-wait">불러오는 중…</p></div>';
    if (opt("detail", "drawer") === "inline" && host) {
      var anchor = host;
      if (host.classList.contains("sn-card")) { var top = host.offsetTop; [].forEach.call(host.parentNode.children, function (c) { if (c.classList.contains("sn-card") && c.offsetTop === top) anchor = c; }); }
      var inl = document.createElement(host.tagName === "LI" ? "li" : "div"); inl.className = "sn-inl";
      inl.innerHTML = '<div class="sn-inl-h">' + head + '<button type="button" class="sn-dw-x" data-dw-close aria-label="닫기">' + X_ICON + "</button></div>" + box;
      anchor.after(inl); host.classList.add("is-open");
    } else {
      var dw = document.createElement("div"); dw.className = "sn-dw" + (opt("detail", "drawer") === "page" ? " is-page" : "");
      dw.innerHTML = '<div class="sn-dw-bg" data-dw-close></div><section class="sn-dw-p" role="dialog" aria-modal="true" aria-label="' + esc(it.alias) + '">' +
        '<header class="sn-dw-h"><div class="sn-dw-top">' + head + '<button type="button" class="sn-dw-x" data-dw-close aria-label="닫기">' + X_ICON + "</button></div>" +
        "<h2>" + esc(it.alias) + '</h2><p class="sn-dw-t">' + esc(it.title) + "</p>" + (it.gist ? '<p class="sn-dw-g">' + esc(it.gist) + "</p>" : "") +
        (it.tags.length ? '<p class="sn-tags">' + it.tags.map(function (t) { return "<span>" + esc(t) + "</span>"; }).join("") + "</p>" : "") + "</header>" + box + "</section>";
      document.body.appendChild(dw); document.documentElement.classList.add("sn-dw-on"); if (host) host.classList.add("is-open");
      var x = dw.querySelector(".sn-dw-x"); if (x) x.focus();
    }
    detailFor(selected, id, function (html) {
      var b = document.querySelector(".sn-dt-body"); if (!b) return;
      b.innerHTML = html ? renderDetail(html, { gist: it.gist || "", fig: figInTab ? figBlock : "" }) : '<p class="sn-dt-wait">이 논문은 회차 리포트에 세부 내용이 없습니다.</p>';
    });
  }

  // phone: the filter line scrolls sideways; drop the edge fade once its end is in view
  document.addEventListener("keydown", function (e) { if (e.key === "Escape" && document.querySelector(".sn-dw, .sn-inl")) closeDetail(); });
  document.addEventListener("keydown", function (e) { var m = document.querySelector(".sn-runmenu"); if (e.key === "Escape" && m && !m.hidden) { m.hidden = true; document.querySelector(".sn-runpick").setAttribute("aria-expanded", "false"); } });
  document.addEventListener("scroll", function (e) { var t = e.target; if (t && t.classList && t.classList.contains("sn-pf")) t.classList.toggle("at-end", t.scrollLeft + t.clientWidth >= t.scrollWidth - 4); }, true);
  document.addEventListener("click", function (e) {
    if (e.target.closest("[data-dw-close]")) { closeDetail(); return; }
    var dxt = e.target.closest("[data-dx-tab]");
    if (dxt) { var box = dxt.closest(".dx-tabs"); [].forEach.call(box.querySelectorAll("[data-dx-tab]"), function (b) { b.setAttribute("aria-selected", String(b === dxt)); });
      [].forEach.call(box.querySelectorAll("[data-dx-pane]"), function (p) { p.hidden = p.getAttribute("data-dx-pane") !== dxt.getAttribute("data-dx-tab"); }); return; }
    var dt = e.target.closest("[data-detail]");
    if (dt) { e.preventDefault(); openDetail(dt.getAttribute("data-detail")); return; }
    var cd = e.target.closest(".sn-card[data-card], .sn-tr[data-card]");
    if (cd && !e.target.closest("a, button")) { openDetail(cd.getAttribute("data-card")); return; }
    var menu = document.querySelector(".sn-runmenu"), pk = e.target.closest(".sn-runpick");
    if (menu && (pk || !e.target.closest(".sn-runmenu") || e.target.closest(".sn-runmenu-cal"))) {
      var on = !!pk && menu.hidden; menu.hidden = !on;
      var bt = document.querySelector(".sn-runpick"); if (bt) bt.setAttribute("aria-expanded", on ? "true" : "false");
      if (pk) return;
    }
    var t = e.target.closest("[data-run]");
    if (t) { var mm = document.querySelector(".sn.show-side"); if (mm) mm.classList.remove("show-side"); selected = t.getAttribute("data-run"); var d = new Date(selected + "T00:00:00"); view = new Date(d.getFullYear(), d.getMonth(), 1); drawCalendar(); drawRun(); return; }
    var pf = e.target.closest("[data-pf]");
    if (pf) { var v = pf.getAttribute("data-pf"); pick = (pick === v) ? "" : v; drawRun(); return; }
    var sd = e.target.closest("[data-side]");
    if (sd) { e.preventDefault(); var m = document.querySelector(".sn"); m.classList.toggle("show-side"); return; }
    if (!e.target.closest(".sn-side")) { var m2 = document.querySelector(".sn.show-side"); if (m2) m2.classList.remove("show-side"); }
    var n = e.target.closest("[data-cal]");
    if (n) { view = new Date(view.getFullYear(), view.getMonth() + +n.getAttribute("data-cal"), 1); drawCalendar(); }
  });
  drawCalendar(); drawUpcoming(); drawRun();
  window.snRedraw = drawRun;
  // hover: the figure floats under the card, the same card the analysis list shows on its rows
  (function () {
    var pop = document.createElement("div"); pop.className = "sn-figpop"; pop.hidden = true; pop.setAttribute("aria-hidden", "true");
    pop.innerHTML = '<img alt=""><p class="sn-figpop-c"></p><p class="sn-figpop-s"></p>'; document.body.appendChild(pop);
    var cur = null, timer = null;
    var can = function () { return opt("fig", "thumb") === "hover" && window.matchMedia("(hover: hover) and (min-width: 721px)").matches; };
    document.addEventListener("mouseover", function (e) {
      if (!can()) return; var card = e.target.closest(".sn-card[data-card]"); if (!card || card === cur) return;
      cur = card; clearTimeout(timer);
      timer = setTimeout(function () {
        var f = FIGS[card.getAttribute("data-card")]; if (cur !== card || !f) return;
        var img = pop.querySelector("img"); if (img.getAttribute("src") !== f.src) img.src = f.src;
        pop.querySelector(".sn-figpop-c").textContent = f.caption.length > 150 ? f.caption.slice(0, 148) + "…" : f.caption;
        pop.querySelector(".sn-figpop-s").textContent = f.source; pop.hidden = false;
        var r = card.getBoundingClientRect(), pw = pop.offsetWidth, ph = pop.offsetHeight, vw = window.innerWidth, vh = window.innerHeight;
        var left = Math.min(Math.max(12, r.left + (r.width - pw) / 2), vw - pw - 12), top = r.bottom + 8; if (top + ph > vh - 12) top = r.top - ph - 8;
        pop.style.left = (left + window.scrollX) + "px"; pop.style.top = (top + window.scrollY) + "px";
        pop.classList.remove("is-in"); void pop.offsetWidth; pop.classList.add("is-in");
      }, 160);
    });
    document.addEventListener("mouseout", function (e) { var card = e.target.closest(".sn-card[data-card]"); if (!card || card.contains(e.relatedTarget)) return; cur = null; clearTimeout(timer); pop.hidden = true; });
  })();
})();
