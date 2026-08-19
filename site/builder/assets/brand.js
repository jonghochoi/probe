/* The mark's pupils follow the pointer. Loaded on every page, since the nav
   carries the mark everywhere; the idle bob, the blink, the mood swap and the
   beacon's signal are pure CSS and run without this file. */

(function () {
  "use strict";
  var pupils = [].slice.call(document.querySelectorAll(".probe-mark .pupil"));
  if (!pupils.length) return;
  // A touch device has no pointer to follow, and a reader who asked for less
  // motion asked for this too.
  if (!matchMedia("(pointer: fine)").matches) return;
  if (matchMedia("(prefers-reduced-motion: reduce)").matches) return;

  var frame = null;

  function look(e) {
    if (frame) return;
    frame = requestAnimationFrame(function () {
      frame = null;
      pupils.forEach(function (pupil) {
        var box = pupil.ownerSVGElement.getBoundingClientRect();
        if (!box.width) return;
        var dx = e.clientX - (box.left + box.width / 2);
        var dy = e.clientY - (box.top + box.height / 2);
        var d = Math.sqrt(dx * dx + dy * dy) || 1;
        // viewBox units, and capped: each eye is r 11 around a pupil of r 5, so
        // 4.5 across and 3.5 down keeps the pupil inside its own eye even on
        // the diagonal. `k` keeps a pointer resting near the mark from pinning
        // the eyes wide.
        var k = Math.min(d / 220, 1);
        pupil.style.translate =
          (dx / d * 4.5 * k).toFixed(2) + "px " + (dy / d * 3.5 * k).toFixed(2) + "px";
      });
    });
  }

  window.addEventListener("pointermove", look, { passive: true });
})();
