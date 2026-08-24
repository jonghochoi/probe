# assets/CLAUDE.md

Rules for the images the root `README.md` embeds. The site's own images live
under `site/builder/assets/` and are unrelated to this folder. Repo-wide rules
are in the root `CLAUDE.md`.

## What is in here

Every image is a light/dark pair (`<name>.svg` + `<name>-dark.svg`) selected by
`<picture>` + `prefers-color-scheme`, and the two files of a pair differ only in
their `<style>` block.

| File | Role |
|---|---|
| `wordmark.svg` | The brand lockup, which **is** the README's H1 |
| `reading-site.svg` | The reading-site banner |
| `probe-lost.svg`, `probe-locked.svg` | The two state icons heading the Why-PROBE comparison columns — out of it (dimmed hull, drooping beacon, crossed-out eyes) and on target (clay hull, a beacon under signal arcs, smiling eyes) |
| `human.svg` | The author bust standing for the human in the *Written by* column of the Who-owns-what table |
| `probe-scouting.svg`, `probe-analysis.svg`, `probe-comparison.svg` | The three track icons filling the agent's cells in that same column |
| `tagline.svg` (880×88) | The tagline banner closing Why PROBE |
| `flow.svg` (880×336) | The How-it-works flow diagram — the day's arXiv narrowing through the filter into the mark, out to the two output chips, and back through the human to `context/` |
| `build-flow.py` | Generates both flow files from one set of coordinates |

## Drawing rules

**Text is live `<text>`.** Every file is SVG whose text is real text, so the
fonts are stacks (`ui-monospace`, `system-ui`) and the layout is left-aligned to
tolerate the substitution.

**Rectangles are files and only files.** The human rides the return wire as a
bare label, never a card.

**A mark cell is the mark alone.** In the Who-owns-what table the word a cell
stands for rides in the image's `alt`, so the column still reads where the
images do not.

**The character's parts carry meaning, so they are not mixed.** Eyes belong to
the character alone — `human.svg` is the same clay and the same shadow with no
face and no beacon. Each track icon shows one character doing that track's own
work: `probe-scouting.svg` sweeps (signal arcs pinging over the beacon, a scan
band crossing the hull, the pupils tracking it), `probe-analysis.svg` reads (no
arcs, one wide page held under the eyes, its lines lighting one after another
and the pupils down on them), `probe-comparison.svg` weighs (two narrower pages
riding up and down against each other like the pans of a scale, the raised one's
lines lit and the eyes turned to it). The moving pages are what tell the
weighing apart from the read at the size a table cell gives them, since the
pupils and the lit lines do the same thing in both.

**Marking is done by the gaze, never by a prop.** In `tagline.svg` the sentence
sits beside a field of the day's papers where three take a crosshair in turn, so
the picture performs the marking the words claim; the smile swaps to a pair of
reticles while the three land and returns once they are all up. A handless probe
holds nothing.

**Animation is inlined and stays in step with the site.** The lockup, the two
state icons, the three track icons, the tagline banner and the flow diagram
redraw `site/builder/components.py`'s `mark()` with their animation inlined,
since a README image carries no external stylesheet. The lockup runs the full
cycle — bob, signal, blink, wink and the mood swap between round pupils and
smiling arcs — while every icon holds one mood: the state pair fixed, the track
trio moving through the one thing its own track does. Change `mark()` and these
change with it.

## The flow diagram

`flow.svg` is the one image generated rather than hand-edited. `build-flow.py`
writes both files from one set of coordinates and `--check` fails when they
drift from it, because moving any of its twenty-odd elements drags the wires,
arrowheads and keyframes pointing at it. Edit the script, never the SVG.

Its picking cycle runs 9 s: a scan band marks six papers as it crosses their
column, three are culled inside the filter (each greys and fades out, still a
circle), three land in the kept column. The durations are literal rather than
`var()` — a `:root` custom property resolves only while the SVG is its own
document, and an unresolved duration drops the animation.

Before pushing a change here: `python3 assets/build-flow.py --check`.
