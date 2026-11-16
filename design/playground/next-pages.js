/* The comparison list and the shelf, drawn in the new scouting page's and the analysis list's grammar:
   a line card with an icon cell on top, then the list's table or the scouting page's cards. */
(function () {
  "use strict";
  var KIND = window.NX_KIND, PL = window.NX_PILLARS || {};
  var root = document.getElementById("nx-root"); if (!root) return;
  var esc = function (s) { return String(s == null ? "" : s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); };
  var opt = function (k, d) { var o = window.PG_OPTS || {}; return o[k] || d; };
  var md = function (d) { return d ? d.slice(5, 10).replace("-", ".") : ""; };
  var chip = function (p) { return '<a class="chip pillar" data-p="' + p + '" href="pillar-' + p + '.html" title="' + esc(PL[p] || p) + ' 소개">' + p + "</a>"; };
  var ICON = {
    pillars: '<svg viewBox="0 0 20 20"><path d="M10 3 3 6.5l7 3.5 7-3.5z"/><path d="M3 10l7 3.5 7-3.5"/><path d="M3 13.5 10 17l7-3.5"/></svg>',
    fork: '<svg viewBox="0 0 20 20"><circle cx="5" cy="4.5" r="1.8"/><circle cx="15" cy="4.5" r="1.8"/><circle cx="10" cy="15.5" r="1.8"/><path d="M5 6.3c0 4 5 4 5 7.4M15 6.3c0 4-5 4-5 7.4"/></svg>',
    shelf: '<svg viewBox="0 0 20 20"><path d="M6 3h8v14l-4-3-4 3z"/></svg>',
    more: '<svg viewBox="0 0 20 20"><circle cx="5" cy="10" r="1.3"/><circle cx="10" cy="10" r="1.3"/><circle cx="15" cy="10" r="1.3"/></svg>',
    stars: '<svg viewBox="0 0 20 20"><path d="m10 2.8 2.2 4.6 5 .7-3.6 3.5.9 5L10 14.2l-4.5 2.4.9-5L2.8 8.1l5-.7z"/></svg>',
    marks: '<svg viewBox="0 0 20 20"><path d="M6 3h8v14l-4-3-4 3z"/></svg>',
    memos: '<svg viewBox="0 0 20 20"><path d="M4 16h3.2L16 7.2 12.8 4 4 12.8z"/><path d="m11.2 5.6 3.2 3.2"/></svg>'
  };
  var line = function (icon, label, items, right) {
    return '<div class="sn-lc nx-lc"><span class="sn-lab" title="' + label + '" aria-hidden="true">' + icon + "</span>" +
      '<div class="sn-pf nx-pf" role="group" aria-label="' + label + '">' + items + "</div>" + (right || "") + "</div>";
  };
  var even = function (n, max) { return Math.ceil(n / Math.ceil(n / max || 1)); };

  /* ── 비교 ── */
  var pick = "";
  function drawCmp() {
    var all = window.NX_CMPS || [], list = all.filter(function (c) { return !pick || c.pillars.indexOf(pick) >= 0; });
    var counts = {}; all.forEach(function (c) { c.pillars.forEach(function (p) { counts[p] = (counts[p] || 0) + 1; }); });
    var head = "";
    if (opt("cmpFilter", "show") === "show") {
      head = line(ICON[opt("cmpIcon", "pillars")], "연구 축으로 거르기", Object.keys(PL).map(function (p) {
        return '<button type="button" class="rail-item pillar" data-p="' + p + '" data-nx-pick="' + p + '" aria-pressed="' + (pick === p) + '"' + (counts[p] ? "" : " disabled") +
          '><span class="sw"></span><b>' + p + '</b><span class="rl">' + esc(PL[p]) + '</span><span class="rn">' + (counts[p] || 0) + "</span></button>";
      }).join(""), '<span class="nx-stat">' + all.length + "편 · 최근 " + esc((all[0] || {}).date || "") + "</span>");
    }
    var how = opt("cmpList", "cards"), sub = opt("cmpSub", "fork"), body;
    var forkLine = function (c) {
      return c.papers.map(function (p) { return '<span class="nx-br"><b>' + esc(p.alias) + "</b>" + esc(p.stance) + "</span>"; }).join('<i class="nx-vs">vs</i>');
    };
    var subLine = function (c) {
      if (sub === "common") return '<span class="nx-cm"><b class="nx-cl">공통</b>' + esc(c.common) + "</span>";
      if (sub === "tagline") return esc(c.tagline);
      return forkLine(c);
    };
    var href = function (c) { return "c/" + c.slug + "/index.html"; };
    if (how === "table") {
      body = '<div class="sn-lh nx-cols-cmp" aria-hidden="true"><span>작성</span><span>질문 · ' + (sub === "common" ? "공통" : sub === "tagline" ? "한 줄" : "갈래") + "</span><span>연구 축</span></div>" +
        '<ul class="sn-rows sn-tbl">' + list.map(function (c) {
          return '<li class="sn-tr nx-cols-cmp"><span class="sn-tid">' + esc(c.date.slice(5)) + '</span><a class="sn-tmain" href="' + href(c) + '"><span class="sn-tt">' + esc(c.title) +
            '</span><span class="sn-tg nx-sub">' + subLine(c) + '</span></a><span class="sn-tp">' + c.pillars.map(chip).join("") + "</span></li>";
        }).join("") + "</ul>";
    } else if (how === "cards") {
      body = '<div class="sn-cards is-even" style="--cols:' + even(list.length, 3) + '">' + list.map(function (c) {
        return '<a class="sn-card nx-card" href="' + href(c) + '"><div class="sn-ctop"><p class="sn-chips">' + c.pillars.map(function (p) { return '<span class="chip pillar" data-p="' + p + '">' + p + "</span>"; }).join("") +
          '</p><span class="sn-id">' + md(c.date) + "</span></div><h3>" + esc(c.title) + '</h3><p class="nx-cm"><b class="nx-cl">공통</b>' + esc(c.common) + "</p>" +
          '<div class="nx-sts">' + c.papers.map(function (p) { return '<p class="nx-st"><b>' + esc(p.alias) + "</b><span>" + esc(p.stance) + "</span></p>"; }).join("") + "</div></a>";
      }).join("") + "</div>";
    } else {
      body = '<div class="nx-vss">' + list.map(function (c) {
        return '<a class="nx-vsc" href="' + href(c) + '"><div class="sn-ctop"><p class="sn-chips">' + c.pillars.map(function (p) { return '<span class="chip pillar" data-p="' + p + '">' + p + "</span>"; }).join("") +
          '</p><span class="sn-id">' + md(c.date) + "</span></div><h3>" + esc(c.title) + '</h3><div class="nx-split" style="--n:' + c.papers.length + '">' +
          c.papers.map(function (p, i) { return (i ? '<i class="nx-vs">vs</i>' : "") + '<div class="nx-side"><b>' + esc(p.alias) + "</b><span>" + esc(p.stance) + "</span></div>"; }).join("") +
          '</div><p class="nx-cm"><b class="nx-cl">공통</b>' + esc(c.common) + "</p></a>";
      }).join("") + "</div>";
    }
    if (!list.length) body = '<p class="nx-empty">이 연구 축의 비교가 아직 없습니다.</p>';
    root.innerHTML = head + body;
  }

  /* ── 서재 ── */
  var tab = "stars";
  function store() {
    if (opt("shSample", "show") === "show") return window.NX_SAMPLE || {};
    var read = function (k) { try { return JSON.parse(localStorage.getItem(k) || "{}") || {}; } catch (e) { return {}; } };
    var memos = {}; try { (JSON.parse(localStorage.getItem("probe.memo.index.v1") || "[]") || []).forEach(function (id) { var m = JSON.parse(localStorage.getItem("probe.memo.v1." + id) || "null"); if (m) memos[id] = m; }); } catch (e) {}
    return { stars: read("probe.stars.v1"), marks: read("probe.mark.v1"), reads: read("probe.read.v1"), memos: memos };
  }
  function byDate(map, key) { return Object.keys(map || {}).sort(function (a, b) { return String(map[b][key] || "").localeCompare(String(map[a][key] || "")); }); }
  function drawShelf() {
    var S = store(), P = window.NX_PAPERS || {};
    var stars = byDate(S.stars, "at"), marks = byDate(S.marks, "at"), memos = byDate(S.memos, "updatedAt"), reads = S.reads || {};
    var layout = opt("shLayout", "tabs"), N = { stars: stars.length, marks: marks.length, memos: memos.length };
    var NAME = { stars: "즐겨찾기", marks: "책갈피", memos: "메모" };
    var items = ["stars", "marks", "memos"].map(function (k) {
      return '<button type="button" class="rail-item" data-nx-tab="' + k + '" aria-pressed="' + (layout === "tabs" && tab === k) + '"><b>' + NAME[k] + '</b><span class="rn">' + N[k] + "</span></button>";
    }).join("");
    var acts = opt("shActions", "menu");
    var menu = acts === "menu" ? '<div class="nx-more"><button type="button" class="nx-more-b" data-nx-more aria-haspopup="true" aria-expanded="false" title="내보내기 · 가져오기">' + ICON.more + "</button>" +
      '<div class="nx-menu" hidden><button type="button" data-nx-act="json">JSON 내보내기</button><button type="button" data-nx-act="md">마크다운 내보내기</button><button type="button" data-nx-act="import">가져오기</button></div></div>' : "";
    var bar = acts === "bar" ? '<div class="nx-bar"><button type="button" data-nx-act="json">JSON 내보내기</button><button type="button" data-nx-act="md">마크다운 내보내기</button><button type="button" data-nx-act="import">가져오기</button></div>' : "";
    var paper = function (id) { return P[id] || { alias: id, title: id, tagline: "", pillars: [] }; };
    var link = function (id, anchor) { return "p/" + id + "/index.html" + (anchor ? "#" + anchor : ""); };
    var readTag = function (id) { return reads[id] ? '<span class="nx-tag">읽음</span>' : ""; };
    var table = function (k) {
      var ids = k === "stars" ? stars : k === "marks" ? marks : memos;
      if (!ids.length) return '<p class="nx-empty">' + (k === "stars" ? "아직 즐겨찾기한 논문이 없습니다. 분석 목록의 ☆을 누르면 여기에 모입니다." : k === "marks" ? "아직 책갈피가 없습니다. 논문을 읽다가 절 제목 옆 책갈피를 누르면 여기에 남습니다." : "아직 메모가 없습니다. 논문 페이지의 메모 칸에 쓰면 여기에 모입니다.") + "</p>";
      if (k === "stars" && opt("shStars", "table") === "cards") {
        return '<div class="sn-cards is-even" style="--cols:' + even(ids.length, 3) + '">' + ids.map(function (id) {
          var p = paper(id);
          return '<a class="sn-card nx-card" href="' + link(id) + '"><div class="sn-ctop"><p class="sn-chips">' + p.pillars.map(function (x) { return '<span class="chip pillar" data-p="' + x + '">' + x + "</span>"; }).join("") +
            '</p><span class="sn-id">' + esc(id) + "</span></div><h3>" + esc(p.alias) + '</h3><p class="sn-gist">' + esc(p.tagline) + '</p><p class="sn-tags"><span>저장 ' + md(S.stars[id].at) + "</span>" + (reads[id] ? "<span>읽음</span>" : "") + "</p></a>";
        }).join("") + "</div>";
      }
      var col = k === "stars" ? "논문 · 한 줄" : k === "marks" ? "논문 · 책갈피 자리" : "논문 · 메모";
      var last = k === "memos" ? "상태" : "연구 축";
      var whenH = k === "memos" ? "고침" : "저장";
      var label = layout === "stack" ? NAME[k] + " " + ids.length : col;
      return '<div class="sn-lh nx-cols-sh" aria-hidden="true"><span>' + whenH + "</span><span>arXiv</span><span>" + label + "</span><span>" + last + "</span></div>" +
        '<ul class="sn-rows sn-tbl">' + ids.map(function (id) {
          var p = paper(id), rec = (k === "stars" ? S.stars : k === "marks" ? S.marks : S.memos)[id];
          var when = (k === "memos" ? rec.updatedAt : rec.at) || "";
          var sub = k === "stars" ? esc(p.tagline) : k === "marks" ? '<span class="nx-mk">' + ICON.shelf + esc(rec.label) + "</span>" : esc(rec.body);
          var end = k === "memos" ? '<span class="nx-tag' + (rec.published ? " is-pub" : "") + '">' + (rec.published ? "게시됨" : "초안") + "</span>" : p.pillars.map(chip).join("");
          return '<li class="sn-tr nx-cols-sh"><span class="sn-tid">' + esc(when.slice(5, 10)) + '</span><a class="sn-tid nx-id" href="https://arxiv.org/abs/' + esc(id) + '" target="_blank" rel="noopener">' + esc(id) + "</a>" +
            '<a class="sn-tmain" href="' + link(id, k === "marks" ? rec.anchor : "") + '"><span class="sn-tt">' + esc(p.title) + readTag(id) + '</span><span class="sn-tg' + (k === "memos" ? " nx-memo" : "") + '">' + sub + "</span></a>" +
            '<span class="sn-tp">' + end + "</span></li>";
        }).join("") + "</ul>";
    };
    var top = opt("shTop", "tabs"), KINDS = ["stars", "marks", "memos"], status = '<p class="nx-status" aria-live="polite"></p>';
    var on = function (k) { return layout === "tabs" && tab === k; };
    var latest = function (k) {
      var ids = k === "stars" ? stars : k === "marks" ? marks : memos; if (!ids.length) return "아직 없음";
      var rec = (k === "stars" ? S.stars : k === "marks" ? S.marks : S.memos)[ids[0]];
      return esc(paper(ids[0]).alias) + " · " + md(k === "memos" ? rec.updatedAt : rec.at);
    };
    var body = layout === "tabs" ? table(tab) : KINDS.map(function (k) { return '<section class="nx-sec" id="nx-' + k + '">' + table(k) + "</section>"; }).join("");
    var head;
    if (top === "line") head = line(ICON.shelf, "서재 보기", items, menu) + bar;
    else if (top === "tiles") head = '<div class="nx-tiles' + (layout === "tabs" ? " is-tabs" : "") + '">' + KINDS.map(function (k) {
        return '<button type="button" class="nx-tile" data-nx-tab="' + k + '" aria-pressed="' + on(k) + '"><span class="nx-ti">' + ICON[k] + '</span><span class="nx-tn"><b>' + NAME[k] + '</b><span class="nx-cnt">' + N[k] + '</span></span><span class="nx-tl">' + latest(k) + "</span></button>";
      }).join("") + "</div>" + (acts === "menu" ? '<div class="nx-tools">' + menu + "</div>" : bar);
    else if (top === "seg") head = '<div class="nx-segrow"><div class="nx-seg" role="group" aria-label="서재 보기">' + KINDS.map(function (k) {
        return '<button type="button" data-nx-tab="' + k + '" aria-pressed="' + on(k) + '">' + ICON[k] + "<b>" + NAME[k] + '</b><span class="nx-cnt">' + N[k] + "</span></button>";
      }).join("") + "</div>" + menu + "</div>" + bar;
    else if (top === "side") head = "";
    else if (top === "merged") head = "";
    else head = '<div class="nx-utabs" role="tablist" aria-label="서재 보기">' + KINDS.map(function (k) {
        return '<button type="button" role="tab" data-nx-tab="' + k + '" aria-selected="' + on(k) + '">' + ICON[k] + "<b>" + NAME[k] + '</b><span class="nx-cnt">' + N[k] + "</span></button>";
      }).join("") + '<span class="nx-sp"></span>' + menu + "</div>" + bar;
    if (top === "side") {
      root.innerHTML = '<div class="nx-sidegrid"><nav class="nx-side-nav" aria-label="서재 보기">' + KINDS.map(function (k) {
        return '<button type="button" data-nx-tab="' + k + '" aria-pressed="' + on(k) + '">' + ICON[k] + "<b>" + NAME[k] + '</b><span class="nx-cnt">' + N[k] + "</span></button>";
      }).join("") + '<div class="nx-side-acts"><button type="button" data-nx-act="json">JSON 내보내기</button><button type="button" data-nx-act="md">마크다운 내보내기</button><button type="button" data-nx-act="import">가져오기</button></div></nav><div class="nx-side-body">' + status + body + "</div></div>";
      return;
    }
    if (top === "merged") {
      var kindF = window.__nxKind || "all", rows = [];
      KINDS.forEach(function (k) {
        var map = k === "stars" ? S.stars : k === "marks" ? S.marks : S.memos;
        Object.keys(map || {}).forEach(function (id) { rows.push({ k: k, id: id, rec: map[id], at: (k === "memos" ? map[id].updatedAt : map[id].at) || "" }); });
      });
      rows.sort(function (a, b) { return b.at.localeCompare(a.at); });
      var shown = rows.filter(function (r) { return kindF === "all" || r.k === kindF; });
      var chipsK = '<div class="nx-kinds" role="group" aria-label="종류로 거르기"><button type="button" data-nx-kind="all" aria-pressed="' + (kindF === "all") + '"><b>전체</b><span class="nx-cnt">' + rows.length + "</span></button>" +
        KINDS.map(function (k) { return '<button type="button" data-nx-kind="' + k + '" aria-pressed="' + (kindF === k) + '">' + ICON[k] + "<b>" + NAME[k] + '</b><span class="nx-cnt">' + N[k] + "</span></button>"; }).join("") + '<span class="nx-sp"></span>' + menu + "</div>";
      var tbl = '<div class="sn-lh nx-cols-mg" aria-hidden="true"><span>날짜</span><span>종류</span><span>논문 · 남긴 것</span><span>연구 축</span></div><ul class="sn-rows sn-tbl">' + shown.map(function (r) {
        var p = paper(r.id), sub = r.k === "stars" ? esc(p.tagline) : r.k === "marks" ? '<span class="nx-mk">' + esc(r.rec.label) + "</span>" : esc(r.rec.body);
        var end = r.k === "memos" ? '<span class="nx-tag' + (r.rec.published ? " is-pub" : "") + '">' + (r.rec.published ? "게시됨" : "초안") + "</span>" : p.pillars.map(chip).join("");
        return '<li class="sn-tr nx-cols-mg"><span class="sn-tid">' + esc(r.at.slice(5, 10)) + '</span><span class="nx-kind k-' + r.k + '" title="' + NAME[r.k] + '">' + ICON[r.k] + "</span>" +
          '<a class="sn-tmain" href="' + link(r.id, r.k === "marks" ? r.rec.anchor : "") + '"><span class="sn-tt">' + esc(p.title) + readTag(r.id) + '</span><span class="sn-tg' + (r.k === "memos" ? " nx-memo" : "") + '">' + sub + '</span></a><span class="sn-tp">' + end + "</span></li>";
      }).join("") + "</ul>";
      root.innerHTML = chipsK + bar + status + (shown.length ? tbl : '<p class="nx-empty">아직 남긴 것이 없습니다.</p>');
      return;
    }
    root.innerHTML = head + status + body;
  }

  function draw() { if (KIND === "cmp") drawCmp(); else drawShelf(); }
  window.pgRedraw = draw;
  document.addEventListener("click", function (e) {
    var t = e.target.closest("[data-nx-pick]");
    if (t) { var v = t.getAttribute("data-nx-pick"); pick = pick === v ? "" : v; draw(); return; }
    var kd = e.target.closest("[data-nx-kind]");
    if (kd) { window.__nxKind = kd.getAttribute("data-nx-kind"); draw(); return; }
    var tb = e.target.closest("[data-nx-tab]");
    if (tb) {
      var k = tb.getAttribute("data-nx-tab");
      if (opt("shLayout", "tabs") === "tabs") { tab = k; draw(); } else { var s = document.getElementById("nx-" + k); if (s) s.scrollIntoView({ behavior: "smooth", block: "start" }); }
      return;
    }
    var mb = e.target.closest("[data-nx-more]"), menu = document.querySelector(".nx-menu");
    if (mb && menu) { menu.hidden = !menu.hidden; mb.setAttribute("aria-expanded", String(!menu.hidden)); return; }
    var act = e.target.closest("[data-nx-act]");
    if (act) { var st = document.querySelector(".nx-status"); if (st) st.textContent = act.textContent + " — 시안에서는 동작만 보여 줍니다."; }
    if (menu && !e.target.closest(".nx-more")) { menu.hidden = true; var b = document.querySelector("[data-nx-more]"); if (b) b.setAttribute("aria-expanded", "false"); }
  });
  draw();
})();
