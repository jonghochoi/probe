/* 번짐 drafts: glApply(null) is the page as built (주장만). */
window.gwApply = function (s) {
  var H = document.documentElement;
  if (!s) H.removeAttribute("data-gw"); else H.setAttribute("data-gw", s.glow);
};
