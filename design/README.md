# design/

The working set for the reading-site redesign: what has been decided and the
playground it was decided in. It lives on the redesign branch until the site
carries the decisions.

| Path | What it is |
|---|---|
| `DECISIONS.md` | Every setting decided so far, page by page, and the code changes the port needs (Korean, in the playground's own option names) |
| `playground/playground.html` | The playground: frames the built site, injects the chosen settings, and copies them out as a dump |
| `playground/gen-pages.py` | Writes the mock pages the playground adds — the new first screen, scouting, comparison and shelf pages, and the pillar pages |
| `playground/scout-new.css`, `playground/scout-new.js` | Style and script of the new scouting page; the stylesheet also carries the new comparison and shelf pages |
| `playground/next-pages.js` | Script of the new comparison and shelf pages, each drawn in the variants the playground switches between |
| `playground/fetch-figs.py` | Picks each paper's main figure — an overview or architecture figure over a results chart — and fetches a small copy for the hover previews: from the rewrites for the analysis list, from arXiv HTML for the scouting page's recommended papers |
| `playground/row-links.json` | Each paper's link icons, keyed by arXiv id, for the list rows |
| `playground/build.sh` | Builds the site at this checkout, lays the mock pages and assets on top, and writes one playground copy per page |
| `playground/pillar/` | The pillar-page playground — `gen-pillar.py` writes one draft page per axis and an overview with every variant's markup, `pl.css` and `pl.js` switch the variants, `playground-pillar.html` is the option panel, and `build.sh <checkout>` builds it over a checkout whose `site/` carries the redesign |

To open it, run `design/playground/build.sh`, then
`python3 -m http.server -d design/playground/out 8000` and open
`/playground-home.html` (or `-front`, `-paper`, `-scout`, `-scout2`, `-cmp`,
`-cmp2`, `-shelf2`).
The output folder is ignored by git. Title fonts other than Gowun Dodum
fall back to the system font, since the decision no longer needs them.
