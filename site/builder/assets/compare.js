/* 비교 — one paper lit across the comparison page, and its figure in the frame.

   A compared paper stands in several places at once: its card, its matrix
   column head and every cell under it, its mark on a stops strip. Pointing at
   any of them (or tabbing to a card or a head) sets the other papers' places
   back, so the reader follows one paper down the page by its mark instead of
   counting columns.

   A ```probe-figs block holds one figure per paper in one frame. Its tabs pick
   which one is on screen, and pointing at a paper's card turns every frame to
   that paper's figure.

   Every place carries `data-paper`; nothing here is computed but which
   elements to set back and which figure to show. Without this file the page
   is the same page, every paper at full strength and every figure stacked. */

(function () {
  "use strict";
  var places = Array.prototype.slice.call(document.querySelectorAll("[data-paper]"));
  if (!places.length) return;

  var frames = Array.prototype.slice.call(document.querySelectorAll("[data-figs]")).map(function (box) {
    var tabs = Array.prototype.slice.call(box.querySelectorAll("[data-figs-tab]"));
    var panels = Array.prototype.slice.call(box.querySelectorAll("[data-figs-panel]"));
    box.querySelector(".figs-tabs").hidden = false;
    box.classList.add("is-live");
    function show(id) {
      if (!tabs.some(function (t) { return t.getAttribute("data-figs-tab") === id; })) return;
      tabs.forEach(function (t) { t.setAttribute("aria-selected", String(t.getAttribute("data-figs-tab") === id)); });
      panels.forEach(function (p) { p.hidden = p.getAttribute("data-figs-panel") !== id; });
    }
    tabs.forEach(function (t, i) {
      t.addEventListener("click", function () { show(t.getAttribute("data-figs-tab")); });
      t.addEventListener("keydown", function (e) {
        if (e.key !== "ArrowRight" && e.key !== "ArrowLeft") return;
        var n = tabs[(i + (e.key === "ArrowRight" ? 1 : tabs.length - 1)) % tabs.length];
        show(n.getAttribute("data-figs-tab")); n.focus();
      });
    });
    show(tabs[0].getAttribute("data-figs-tab"));
    return show;
  });

  function light(id) {
    places.forEach(function (el) {
      el.classList.toggle("is-dim", !!id && el.getAttribute("data-paper") !== id);
    });
  }

  places.forEach(function (el) {
    var id = el.getAttribute("data-paper");
    var card = el.classList.contains("cmp-card");
    function on() { light(id); if (card) frames.forEach(function (show) { show(id); }); }
    el.addEventListener("mouseenter", on);
    el.addEventListener("mouseleave", function () { light(""); });
    el.addEventListener("focusin", on);
    el.addEventListener("focusout", function () { light(""); });
  });
})();
