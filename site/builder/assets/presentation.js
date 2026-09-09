/* 발표 mode — the presentation, one slide at a time, on a screen.
 *
 * The 발표 tab reads as a scroll: every slide with its speaker essay under it,
 * which is what rehearsing and sharing want. Presenting wants the opposite —
 * one slide filling the screen, nothing else on it, and the essay somewhere
 * only the presenter can see. Same markup, two readings, and this file is the
 * switch between them.
 *
 * Three pieces:
 *
 *   The stage. `data-presenting` on the presentation hides every slide but one and
 *   drops the essays; `presentation.css` does the rest. Nothing is cloned or rebuilt,
 *   so a slide on the stage is the same element the page already validated.
 *
 *   The keys. → ← Space PageDown PageUp Home End Esc, plus a click on the
 *   right or left half. A presenter's hand is on a clicker that sends PageUp
 *   and PageDown, so those are not an afterthought.
 *
 *   Three tools for the three things that go wrong in front of a room. 목록 (O)
 *   answers the question that names a slide four beats back. 레이저 (L) points
 *   at a number, on the one kind of slide type cannot point at — the paper's
 *   own figure. Zoom (+ − 0, Ctrl-wheel, drag to pan) makes that figure legible
 *   from the back row. The last is a repair for a frame `presentation/AUTHORING.md` §3
 *   is meant to fill at authoring time, so reaching for it often is the
 *   signal that a slide, not the room, is what needs fixing.
 *
 *   The notes window. A second window carrying the current slide's essay, the
 *   next slide's title and a clock. It reads its content out of this document
 *   through `opener`, so the two never disagree about what is on screen, and
 *   the index travels over a `BroadcastChannel` both directions — a presenter
 *   who advances from the notes window moves the stage.
 *
 * Without this file the tab is still the whole presentation, read by scrolling. The
 * control bar the build prints stays `hidden` and no key does anything, which
 * is the site's rule: a control removes itself rather than sitting inert.
 */

(function () {
  "use strict";

  var stage = document.querySelector("[data-pres-stage]");
  var presentation = document.querySelector(".prs-presentation");
  var bar = document.querySelector("[data-pres-bar]");
  if (!stage || !presentation || !bar) return;

  var slides = [].slice.call(presentation.querySelectorAll(".prs-slide"));
  if (!slides.length) return;

  var startBtn = bar.querySelector("[data-pres-start]");
  var notesBtn = bar.querySelector("[data-pres-notes]");
  var listBtn = bar.querySelector("[data-pres-list]");
  var laserBtn = bar.querySelector("[data-pres-laser]");
  var zoomOut = bar.querySelector("[data-pres-zoom]");
  var at = 0;
  var notes = null;
  var chan = null;
  var startedAt = 0;
  var laser = null;                    // the overlay, built the first time
  var dot = null;
  var z = { k: 1, x: 0, y: 0 };
  var ZMAX = 4;

  bar.hidden = false;

  try {
    chan = new BroadcastChannel("probe-presentation");
    chan.onmessage = function (e) {
      var d = e.data || {};
      // A notes window that outlived its stage would otherwise drive a presentation it
      // is not showing, so every message names the presentation it belongs to.
      if (d.presentation !== presentation.dataset.presentationOf) return;
      if (d.type === "go") show(d.at);
      if (d.type === "who") send();
    };
  } catch (err) {
    chan = null;                       // notes still open; they just cannot sync
  }

  function send() {
    if (!chan) return;
    chan.postMessage({
      presentation: presentation.dataset.presentationOf, type: "at", at: at,
      total: slides.length, startedAt: startedAt,
    });
  }

  function presenting() { return stage.hasAttribute("data-presenting"); }
  function listing() { return stage.hasAttribute("data-overview"); }

  function show(i) {
    at = Math.max(0, Math.min(slides.length - 1, i));
    // A new slide is read whole first, and the slide being left goes back to
    // 100% with it — otherwise stepping back lands on someone else's zoom.
    z = { k: 1, x: 0, y: 0 };
    slides.forEach(function (s, n) {
      s.classList.toggle("prs-on", n === at);
      s.style.removeProperty("--prs-z");
      s.style.removeProperty("--prs-x");
      s.style.removeProperty("--prs-y");
    });
    zoomOut.textContent = "100%";
    if (!presenting() || listing()) {
      slides[at].scrollIntoView({ block: listing() ? "nearest" : "center" });
    }
    send();
  }

  function start() {
    stage.setAttribute("data-presenting", "");
    // The root carries the flag too, so the page behind stops scrolling and
    // takes its scrollbar gutter with it — the stage is then the whole width.
    document.documentElement.setAttribute("data-presenting", "");
    startedAt = Date.now();
    show(at);
    if (stage.requestFullscreen) {
      // A browser that refuses fullscreen (a permission policy, an older
      // engine) still gets the stage — it just keeps the browser chrome.
      stage.requestFullscreen().catch(function () {});
    }
  }

  function stop() {
    setList(false);
    setLaser(false);
    setZoom(1);
    stage.removeAttribute("data-presenting");
    document.documentElement.removeAttribute("data-presenting");
    if (document.fullscreenElement && document.exitFullscreen) {
      document.exitFullscreen().catch(function () {});
    }
    slides[at].scrollIntoView({ block: "center" });
  }

  document.addEventListener("fullscreenchange", function () {
    // Esc leaves fullscreen without telling us, so the stage follows the
    // browser rather than the other way round.
    if (!document.fullscreenElement && presenting()) stop();
  });

  startBtn.addEventListener("click", function () {
    presenting() ? stop() : start();
  });

  /* ── 목록 ──────────────────────────────────────────────────────────── */

  function setList(on) {
    stage.toggleAttribute("data-overview", on);
    listBtn.setAttribute("aria-pressed", on ? "true" : "false");
    if (on) { setLaser(false); setZoom(1); slides[at].scrollIntoView({ block: "nearest" }); }
  }

  listBtn.addEventListener("click", function () { setList(!listing()); });

  slides.forEach(function (s, n) {
    s.addEventListener("click", function (e) {
      if (!listing()) return;
      e.stopPropagation();
      show(n);
      setList(false);
    });
  });

  /* ── 레이저 ────────────────────────────────────────────────────────── */

  function setLaser(on) {
    if (on && !laser) {
      // The overlay takes the click as well as the pointer: pointing at a
      // number must not advance past the slide the number is on.
      laser = document.createElement("div");
      laser.className = "prs-laser";
      dot = document.createElement("div");
      dot.className = "prs-dot";
      dot.style.left = "-100px";
      laser.addEventListener("mousemove", function (e) {
        dot.style.left = e.clientX + "px";
        dot.style.top = e.clientY + "px";
      });
      laser.addEventListener("click", function (e) {
        e.stopPropagation(); e.preventDefault();
      });
      stage.appendChild(laser);
      stage.appendChild(dot);
    }
    if (laser) {
      laser.style.display = on ? "block" : "none";
      dot.style.display = on ? "block" : "none";
    }
    laserBtn.setAttribute("aria-pressed", on ? "true" : "false");
  }

  laserBtn.addEventListener("click", function () {
    setLaser(laserBtn.getAttribute("aria-pressed") !== "true");
  });

  function lasing() { return laserBtn.getAttribute("aria-pressed") === "true"; }

  /* ── zoom and pan ──────────────────────────────────────────────────── */

  function paint() {
    var s = slides[at];
    var w = s.offsetWidth, h = s.offsetHeight;
    // The slide always covers its own box, so a pan can never expose the ground
    // behind it: x ∈ [w(1−k), 0] per axis.
    z.x = Math.min(0, Math.max(w * (1 - z.k), z.x));
    z.y = Math.min(0, Math.max(h * (1 - z.k), z.y));
    s.style.setProperty("--prs-z", z.k);
    s.style.setProperty("--prs-x", z.x + "px");
    s.style.setProperty("--prs-y", z.y + "px");
    zoomOut.textContent = Math.round(z.k * 100) + "%";
  }

  function setZoom(k, cx, cy) {
    var s = slides[at];
    if (!s) return;
    k = Math.max(1, Math.min(ZMAX, k));
    var r = s.getBoundingClientRect();
    // The layout box is the visual rect with the current translation taken back
    // out; the point under the cursor is then in the slide's own coordinates,
    // and it is that point the new scale is pinned to.
    var l0 = r.left - z.x, t0 = r.top - z.y;
    if (cx == null) { cx = r.left + r.width / 2; cy = r.top + r.height / 2; }
    var px = (cx - r.left) / z.k, py = (cy - r.top) / z.k;
    z.k = k;
    z.x = k === 1 ? 0 : cx - l0 - px * k;
    z.y = k === 1 ? 0 : cy - t0 - py * k;
    paint();
  }

  presentation.addEventListener("wheel", function (e) {
    if (!presenting() || listing()) return;
    if (!e.ctrlKey && !e.metaKey) return;
    e.preventDefault();
    setZoom(z.k * Math.exp(-e.deltaY * 0.0022), e.clientX, e.clientY);
  }, { passive: false });

  var drag = null, swallow = false;
  presentation.addEventListener("mousedown", function (e) {
    if (!presenting() || listing() || z.k === 1 || e.button !== 0) return;
    drag = { x: e.clientX, y: e.clientY, moved: false };
  });
  window.addEventListener("mousemove", function (e) {
    if (!drag) return;
    z.x += e.clientX - drag.x;
    z.y += e.clientY - drag.y;
    drag.x = e.clientX; drag.y = e.clientY; drag.moved = true;
    paint();
    e.preventDefault();
  });
  window.addEventListener("mouseup", function () {
    // A pan is not also a page turn.
    swallow = !!(drag && drag.moved);
    drag = null;
  });

  /* ── keys and clicks ───────────────────────────────────────────────── */

  document.addEventListener("keydown", function (e) {
    if (!presenting()) return;
    if (e.metaKey || e.ctrlKey || e.altKey) return;
    var k = e.key;
    if (k === "ArrowRight" || k === "PageDown" || k === " " || k === "Spacebar") {
      listing() ? setList(false) : show(at + 1);
    } else if (k === "ArrowLeft" || k === "PageUp" || k === "Backspace") {
      show(at - 1);
    } else if (k === "Home") {
      show(0);
    } else if (k === "End") {
      show(slides.length - 1);
    } else if (k === "o" || k === "O") {
      setList(!listing());
    } else if (k === "l" || k === "L") {
      setLaser(!lasing());
    } else if (k === "+" || k === "=") {
      setZoom(z.k * 1.25);
    } else if (k === "-" || k === "_") {
      setZoom(z.k / 1.25);
    } else if (k === "0") {
      setZoom(1);
    } else if (k === "Escape") {
      // Esc unwinds one layer at a time: the list, then the pointer, then the
      // stage. A presenter who wanted out of the overview does not want out of
      // the talk.
      if (listing()) setList(false);
      else if (lasing()) setLaser(false);
      else if (z.k > 1) setZoom(1);
      else stop();
    } else {
      return;
    }
    e.preventDefault();
  });

  presentation.addEventListener("click", function (e) {
    if (!presenting() || listing()) return;
    if (swallow) { swallow = false; return; }
    show(at + (e.clientX < window.innerWidth / 2 ? -1 : 1));
  });

  notesBtn.addEventListener("click", function () {
    openNotes();
  });

  /* ── the notes window ─────────────────────────────────────────────── */

  function openNotes() {
    if (notes && !notes.closed) { notes.focus(); return; }
    notes = window.open("", "probe-presentation-notes",
                        "width=620,height=780,menubar=no,toolbar=no");
    if (!notes) {                      // popup blocked — say so where it was asked
      notesBtn.textContent = "팝업이 막혀 있습니다";
      return;
    }
    notes.document.write(NOTES_HTML.replace("__PRESENTATION__", presentation.dataset.presentationOf));
    notes.document.close();
  }

  window.addEventListener("pagehide", function () {
    if (notes && !notes.closed) notes.close();
  });

  show(0);

  /* The notes window's whole document. It is written rather than fetched
     because it is one screen of markup that has no meaning outside a running
     presentation, and a file on the server would be a page a reader could
     land on with nothing in it.

     It reads the slides out of `opener` instead of being sent their text: the
     essay it shows is then literally the element on the stage, and the two
     cannot drift. */
  var NOTES_HTML = [
    '<!DOCTYPE html><html lang="ko"><head><meta charset="utf-8">',
    '<title>발표자 노트 · PROBE</title><style>',
    ':root{color-scheme:dark}',
    'body{margin:0;background:#14110f;color:#e8ded7;',
    ' font:15px/1.75 -apple-system,BlinkMacSystemFont,"Pretendard Variable",Pretendard,sans-serif;',
    ' display:grid;grid-template-rows:auto minmax(0,1fr) auto;height:100vh;word-break:keep-all}',
    'header{padding:16px 20px 12px;border-bottom:1px solid #2f2721;display:grid;gap:8px}',
    '.row{display:flex;align-items:baseline;justify-content:space-between;gap:12px}',
    '.n{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:12px;color:#a08d81}',
    '.clock{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:22px;',
    ' font-weight:600;color:#f0a183;font-variant-numeric:tabular-nums}',
    'h1{margin:0;font-size:21px;font-weight:800;line-height:1.3;color:#fff}',
    'main{overflow:auto;padding:16px 20px}',
    'main p{margin:0 0 11px}main p:last-child{margin:0}',
    'main b{color:#fff;font-weight:700}',
    'main .m{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-style:normal;font-size:.94em}',
    '.next{padding:12px 20px 14px;border-top:1px solid #2f2721;color:#a08d81;font-size:13px}',
    '.next b{color:#e8ded7;font-weight:600}',
    '.keys{padding:0 20px 14px;display:flex;gap:8px}',
    'button{flex:1;padding:10px;border:1px solid #3a302a;border-radius:7px;',
    ' background:#1d1815;color:#e8ded7;font:inherit;font-size:13px;cursor:pointer}',
    'button:hover{background:#261f1b}',
    '</style></head><body>',
    '<header><div class="row"><span class="n" id="n">—</span>',
    '<span class="clock" id="clock">0:00</span></div><h1 id="title">—</h1></header>',
    '<main id="script"></main>',
    '<p class="next" id="next"></p>',
    '<div class="keys"><button id="prev">← 이전</button><button id="nxt">다음 →</button></div>',
    '<script>(function(){',
    'var PRESENTATION="__PRESENTATION__",started=0,at=0;',
    'var c=null;try{c=new BroadcastChannel("probe-presentation")}catch(e){}',
    'function slides(){try{return [].slice.call(',
    '  opener.document.querySelectorAll(".prs-presentation .prs-slide"))}catch(e){return []}}',
    'function scripts(){try{return [].slice.call(',
    '  opener.document.querySelectorAll(".prs-presentation .prs-script"))}catch(e){return []}}',
    'function txt(el){if(!el)return "";var c=el.cloneNode(true);',
    ' [].forEach.call(c.querySelectorAll("br"),function(b){',
    '   b.parentNode.replaceChild(document.createTextNode(" "),b)});',
    ' return c.textContent.trim()}',
    'function paint(){',
    ' var ss=slides(),sc=scripts(),s=ss[at];if(!s)return;',
    ' var h=s.querySelector("h3")||s.querySelector(".prs-say");',
    ' document.getElementById("n").textContent=(at+1)+" / "+ss.length+"  ·  "+',
    '   (s.dataset.act||"")+" · "+txt(s.querySelector(".prs-act"));',
    ' document.getElementById("title").textContent=txt(h);',
    ' var body=document.getElementById("script");body.innerHTML="";',
    ' var e=sc[at];',
    ' if(e){[].forEach.call(e.querySelectorAll("p"),function(p){',
    '   body.appendChild(document.importNode(p,true))})}',
    ' else{body.innerHTML="<p style=\\"color:#7d6c62\\">이 슬라이드에는 발표 에세이가 없습니다.</p>"}',
    ' var nx=ss[at+1],nh=nx&&(nx.querySelector("h3")||nx.querySelector(".prs-say"));',
    ' document.getElementById("next").innerHTML=nx?',
    '   ("다음 &nbsp;<b>"+txt(nh)+"</b>"):"마지막 장입니다.";',
    '}',
    'function tick(){if(!started)return;var s=Math.floor((Date.now()-started)/1000);',
    ' document.getElementById("clock").textContent=',
    '   Math.floor(s/60)+":"+String(s%60).padStart(2,"0")}',
    'if(c){c.onmessage=function(e){var d=e.data||{};if(d.presentation!==PRESENTATION)return;',
    ' if(d.type==="at"){at=d.at;started=d.startedAt;paint();tick()}};',
    ' c.postMessage({presentation:PRESENTATION,type:"who"})}',
    'function go(i){at=i;paint();if(c)c.postMessage({presentation:PRESENTATION,type:"go",at:i})}',
    'document.getElementById("prev").onclick=function(){go(Math.max(0,at-1))};',
    'document.getElementById("nxt").onclick=function(){go(Math.min(slides().length-1,at+1))};',
    'document.addEventListener("keydown",function(e){',
    ' if(e.key==="ArrowRight"||e.key==="PageDown"||e.key===" ")go(Math.min(slides().length-1,at+1));',
    ' else if(e.key==="ArrowLeft"||e.key==="PageUp")go(Math.max(0,at-1));else return;',
    ' e.preventDefault()});',
    'setInterval(tick,1000);paint();',
    '})();<\/script></body></html>',
  ].join("\n");
})();
