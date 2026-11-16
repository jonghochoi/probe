/* Pillar-popup drafts: every axis chip opens the axis's introduction —
 * names, description, the decisions it covers. The playground's choices
 * (localStorage) pick the shape. */
(function () {
  "use strict";
  var KEY = "probe.pg.pop.v1";
  var DEF = { desk: "pop", phone: "sheet", head: "tint", desc: "show", decs: "titles", dname: "problems",
              dcode: "small", link: "on", open: "click" };
  function opt() { var s = {}; try { s = JSON.parse(localStorage.getItem(KEY) || "{}") || {}; } catch (e) {} return Object.assign({}, DEF, s); }
  var D = window.PL_POP || {};
  var esc = function (t) { return String(t == null ? "" : t).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); };
  var X = '<svg viewBox="0 0 16 16" width="14" height="14" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" aria-hidden="true"><path d="m4 4 8 8M12 4l-8 8"/></svg>';
  // the site root, from this script's own address
  var me = document.currentScript, ROOT = me ? me.src.replace(/assets\/plpop\.js(\?.*)?$/, "") : "";

  var box = document.createElement("div"); box.className = "pp"; box.hidden = true;
  document.body.appendChild(box);
  var cur = null, timer = 0;

  function body(code, o) {
    var d = D[code]; if (!d) return "";
    var title = o.dname === "problems" ? "다루는 문제" : "결정";
    var decs = o.decs === "none" ? "" :
      '<section class="pp-decs"><h3>' + title + '<span>' + d.decisions.length + "</span></h3><ul>" +
      d.decisions.map(function (x) {
        return "<li><span class=\"pp-dt\">" + esc(x.title) + "</span>" + (x.open ? '<span class="pp-open">미결</span>' : "") +
          (o.dcode === "hide" ? "" : '<span class="pp-dc">' + x.id + "</span>") + "</li>";
      }).join("") + "</ul></section>";
    return '<div class="pp-p" role="dialog" aria-label="' + esc(code + " " + d.label) + '" style="--pc:var(--' + code.toLowerCase() + ');--pci:var(--' + code.toLowerCase() + '-ink)">' +
      '<header class="pp-h"><span class="chip pillar" data-p="' + code + '">' + code + "</span>" +
      '<div class="pp-names"><b>' + esc(d.label) + "</b><span>" + esc(d.name) + "</span></div>" +
      '<button type="button" class="pp-x" data-pp-close aria-label="닫기">' + X + "</button></header>" +
      (o.desc === "show" ? '<p class="pp-desc">' + esc(d.desc) + '<span class="pp-draft">초안</span></p>' : "") +
      decs +
      (o.link === "on" ? '<p class="pp-more"><a href="' + ROOT + "p/index.html#p=" + code + '">이 축의 분석 보기 →</a></p>' : "") +
      "</div>";
  }

  function place(chip, mode) {
    var p = box.querySelector(".pp-p"); if (!p) return;
    if (mode !== "pop") { p.style.left = p.style.top = ""; return; }
    var r = chip.getBoundingClientRect(), w = p.offsetWidth, h = p.offsetHeight;
    var left = Math.min(Math.max(12, r.left), innerWidth - w - 12);
    var top = r.bottom + 8; if (top + h > innerHeight - 12) top = Math.max(12, r.top - h - 8);
    p.style.left = left + "px"; p.style.top = top + "px";
  }

  function open(chip) {
    var o = opt(), code = chip.getAttribute("data-p");
    if (!D[code]) return;
    var phone = matchMedia("(max-width: 720px)").matches, mode = phone ? o.phone : o.desk;
    box.className = "pp pp-" + mode + " pp-head-" + o.head;
    box.innerHTML = '<div class="pp-bg" data-pp-close></div>' + body(code, o);
    box.hidden = false; cur = chip;
    document.documentElement.classList.toggle("pp-lock", mode !== "pop");
    place(chip, mode);
  }
  function close() { box.hidden = true; box.innerHTML = ""; cur = null; document.documentElement.classList.remove("pp-lock"); }

  // The chip opens the popup and nothing else: a chip inside a card or a
  // row's link would otherwise also open that.
  document.addEventListener("click", function (e) {
    if (e.target.closest("[data-pp-close]")) { close(); return; }
    var chip = e.target.closest(".chip.pillar[data-p]");
    if (chip && !box.contains(chip)) {
      e.preventDefault(); e.stopPropagation();
      if (cur === chip) close(); else open(chip);
      return;
    }
    if (!box.hidden && !box.contains(e.target)) close();
  }, true);
  document.addEventListener("keydown", function (e) { if (e.key === "Escape" && !box.hidden) close(); });
  addEventListener("scroll", function () { if (cur && box.className.indexOf("pp-pop") >= 0) place(cur, "pop"); }, { passive: true });
  // hover, desktop only, when chosen
  document.addEventListener("mouseover", function (e) {
    if (opt().open !== "hover" || matchMedia("(max-width: 720px)").matches) return;
    var chip = e.target.closest(".chip.pillar[data-p]");
    if (!chip || box.contains(chip) || chip === cur) return;
    clearTimeout(timer); timer = setTimeout(function () { open(chip); }, 250);
  });
  document.addEventListener("mouseout", function (e) {
    if (opt().open !== "hover") return;
    var chip = e.target.closest(".chip.pillar[data-p]"); if (chip) clearTimeout(timer);
  });
  document.documentElement.classList.add("pp-ready");
  window.ppClose = close;
})();
