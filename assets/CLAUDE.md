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
| `wordmark.svg` | The brand lockup opening the README — the probe reading its one paper with a coffee beside it, until it nods off over the page |
| `rule.svg` | The accent hairline under the lockup — one brand gradient fading out at both ends, and the only divider between the lockup and the three lines |
| `claim.svg` | The middle of the front door's three lines, set in the accent |
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
tolerate the substitution. `claim.svg` is the one that centres instead: the
README centres the image, so the sentence is anchored at the middle of a box
wide enough to absorb a wider face and grows evenly into it.

**The accent carries one line, and the README carries the rest as text.**
Markdown cannot colour a word, so the front door's claim is an image while the
hook above it and the invitation below it stay live text — which is also what
keeps the emphasis single. A second coloured line would leave the trio with no
middle. `claim.svg` repeats its sentence in `aria-label` and in the `alt` the
README embeds it with, so the line still reads where the image does not.

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
pupils and the lit lines do the same thing in both. The lockup reads too — the
same page, the same lit lines — and what separates it from `probe-analysis.svg`
is the mug and what the front door does with it: the coffee belongs there alone,
where the invitation is to take the read at a coffee's pace, and so does the
doze it ends in — closed lids, the snore bubble and the `z`s. A track icon shows
its track working; only the front door is allowed to lose the fight with the
paper. Neither the mug nor the doze follows the character into a table cell.

**Marking is done by the gaze, never by a prop.** In `tagline.svg` the sentence
sits beside a field of the day's papers where three take a crosshair in turn, so
the picture performs the marking the words claim; the smile swaps to a pair of
reticles while the three land and returns once they are all up. A handless probe
holds nothing — a prop is placed, not gripped: the page rides under the eyes and
the mug stands on the ground beside the hull, outside the bob that lifts the
character off it.

**Animation is inlined and stays in step with the site.** The lockup, the two
state icons, the three track icons, the tagline banner and the flow diagram
redraw `site/builder/components.py`'s `mark()` with their animation inlined,
since a README image carries no external stylesheet. The lockup runs the full
cycle — bob, and a mood swap between reading and dozing off: pupils down and
scanning the page's lines as they light in turn, then closed lids, a snore
bubble at the nose and three `z`s drifting off the hull. The blink lives in the
same 14 s cycle, keyed to the reading half, so nothing squashes an eye that is
already shut, and the mug steams outside it — the coffee goes cold at the same
rate whether the reader is awake or not. Signal arcs belong to the images that
hail (`probe-scouting.svg`, `probe-locked.svg`, the banner) and not to the front
door, which shows one thing: the read. A beacon hailing over a sleeping reader
reads as an alarm going off. Every icon holds one mood instead: the state pair
fixed, the track trio moving through the one thing its own track does. Change
`mark()` and these change with it, second mood apart: the site smiles, the
lockup dozes.

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
