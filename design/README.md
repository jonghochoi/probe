# design/

The working set for the reading-site redesign: what has been decided and the
playground it was decided in. It lives on the redesign branch until the site
carries the decisions.

| Path | What it is |
|---|---|
| `DECISIONS.md` | Every setting decided so far, page by page, and the code changes the port needs (Korean, in the playground's own option names) |
| `playground/playground.html` | The playground: frames the built site, injects the chosen settings, and copies them out as a dump |
| `playground/gen-pages.py` | Writes the mock pages the playground adds — the new first screen, the new scouting page and the pillar pages |
| `playground/scout-new.css`, `playground/scout-new.js` | Style and script of the new scouting page |
| `playground/row-links.json` | Each paper's link icons, keyed by arXiv id, for the list rows |
| `playground/build.sh` | Builds the site at this checkout, lays the mock pages and assets on top, and writes one playground copy per page |

To open it, run `design/playground/build.sh`, then
`python3 -m http.server -d design/playground/out 8000` and open
`/playground-home.html` (or `-front`, `-paper`, `-scout`, `-scout2`, `-cmp`).
The output folder is ignored by git. Title fonts other than Gowun Dodum
fall back to the system font, since the decision no longer needs them.
