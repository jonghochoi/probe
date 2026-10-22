# .claude/vendor/html-plan/

The runtime of the `html-plan` plugin from
[anthropics/claude-plugins-community](https://github.com/anthropics/claude-plugins-community/tree/main/html-plan),
copied at upstream commit `06ec7b6`. `/ideate` packs its answer page with it
(`.claude/prompts/ideate.txt` step 8); a cloud session loads no plugin, so the
repo carries the files. The plugin's skill text is not here — what goes on the
page is `ideate.txt`'s and `.claude/prompts/ideate-page.html`'s.

| File | Role |
|---|---|
| `htmlplan.js` | The page runtime — claim tree, decisions, comments, the response sheet. Its reader-facing labels are Korean; the response markdown it builds is upstream's |
| `htmlplan.css` | The runtime's stylesheet and color tokens, light and dark — upstream as is |
| `pack.mjs` | Lints a page and inlines the two files above into one portable HTML — upstream as is |
| `LICENSE` | The upstream repository's Apache License 2.0 |

To take an upstream release, copy the three files over these and re-apply the
labels: every string `htmlplan.js` shows the reader, not the markdown it puts
in the response.
