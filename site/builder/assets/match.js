/* The one rule both search surfaces match a query with.
 *
 * Two surfaces ask the same question of the same corpus — the landing's filter
 * box (`filter.js`) and the ⌘K palette (`palette.js`). The rule that decides
 * whether a query matches a paper lives here rather than in either of them: a
 * query that finds a paper on the landing and nothing in the palette is not two
 * behaviours, it is one bug.
 *
 * `window.ProbeMatch` rather than an export — the site ships classic scripts,
 * so shared state travels on `window`, and this file is loaded before every
 * script that reads it.
 */

(function () {
"use strict";

/* The build compacts its haystacks with one rule (`corpus.compact`): lowercase,
 * then drop everything that is not a letter, a digit, or the `·` that fences one
 * fragment off from the next. A query goes through the same mill — minus the
 * `·`, which is the haystack's barrier and never a reader's word — so "힘 제어"
 * finds text that spells it "힘제어" and the other way round. Korean spacing is
 * not stable enough to match on, and neither is ours; nor is a hyphen, which is
 * how "spatial temporal" reaches the tag `spatial-temporal`.
 */
const DROP = /[^0-9a-z가-힣ㄱ-ㅎㅏ-ㅣ]+/g;

function compact(s) {
  return String(s == null ? "" : s).toLowerCase().normalize("NFC").replace(DROP, "");
}

/* A query is typed as speech — "액션청킹은", "지연을", "그리퍼로" — while the text
 * spells the word bare. Strip one trailing particle and try both forms; longest
 * first, so "으로" never loses to "로". The guard keeps a short word whole: "은" is
 * a particle, "가치" is not.
 */
const PARTICLES = [
  "으로부터", "로부터", "에서는", "에게서", "이라는", "으로는", "까지", "부터",
  "처럼", "보다", "에서", "에게", "한테", "이나", "으로", "라는", "라고", "이란",
  "은", "는", "이", "가", "을", "를", "의", "에", "와", "과", "로", "도", "만", "랑",
].sort((a, b) => b.length - a.length);

function bare(term) {
  for (const p of PARTICLES) {
    if (term.length > p.length + 1 && term.endsWith(p)) return term.slice(0, -p.length);
  }
  return term;
}

/* One query → `[{t, b}]`, the compacted term and the same term with a particle
 * taken off. Both forms are tried at the match site, which is what lets
 * "양자화를" find text that spells it "양자화하고".
 */
function parse(q) {
  return String(q || "").split(/\s+/).map(compact).filter(Boolean)
    .map((t) => ({ t, b: bare(t) }));
}

/** Does one compacted fragment carry this term, in either of its two forms? */
function inFragment(fragment, term) {
  return fragment.includes(term.t) || (term.b !== term.t && fragment.includes(term.b));
}

/** …and does any fragment in a list? */
function inAny(fragments, term) {
  return fragments.some((f) => inFragment(f, term));
}

window.ProbeMatch = { compact, bare, parse, inFragment, inAny };
})();
