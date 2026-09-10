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
| `probe-scouting.svg`, `probe-analysis.svg`, `probe-comparison.svg`, `probe-presentation.svg` | The four track icons filling the agent's cells in that same column |
| `tagline.svg` (880×88) | The tagline banner closing Why PROBE |
| `flow.svg` (880×348) | The How-it-works flow diagram — `context/` dropping into the run, the day's arXiv narrowing through the filter into the mark, and out to the scouting card and the on-demand card |
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

**Rectangles are files and only files.** Nothing else earns a box — a stage is
drawn as a funnel, an act as a wire.

**Every card sits on the same ground, and the accent draws the edge a reader
meets first.** The three cards the README embeds — `reading-site.svg`,
`tagline.svg` and `flow.svg` — share one fill (`#FFFCFA` light, `#211C19` dark)
and one outline, the accent (`#D97757`, `#E8916F`) that the reading-site card's
own arrow already carries. A card tinted toward the accent reads as a different
kind of object rather than a louder one, so the ground never carries the
emphasis — the edge does. What the edge marks is depth rather than affordance: a
card standing on the README's own page takes the accent, and a card drawn inside
one of those images does not, so three outlines read as one set of panels rather
than three unrelated boxes. Every card inside `flow.svg` keeps the neutral
`#E8CDBD` / `#3D3129`, where a border is a card's boundary and says nothing
else; the paler `WASH` is the funnel's, not a card's.

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
lines lit and the eyes turned to it), and `probe-presentation.svg` presents (a screen
standing behind, up and to the right so the character is beside it rather than
under it, its bands lighting one after another as a talk advances, and one
listener in front on the left — cut by the bottom edge, the way a front row
is).

Two things about that icon are worth stating, because both are departures.

**Its outline is what does the work.** At the 22 px a table cell gives these,
the only thing that survives is the **shape below the face** — one page for the
read, two with a gap for the weighing, none for the sweep. A tilt, an inner
rule or a pupil direction is gone at that size, so a fourth track needs a
fourth outline: here the screen breaks the silhouette upward on the right and
the listener breaks it downward on the left, and neither is a variation on the
block the other three share. Nothing hangs under the chin at all, which is what
makes this one legible beside `probe-analysis.svg` in a column.

**It is the one icon with a second character**, and that is the point rather
than an exception: reading and weighing are things one character does alone,
and presenting is not. The listener is `human.svg` scaled — the same head
radius over the same semicircle torso — rather than a new shape, so the room
this track speaks to is the same human `human.svg` stands for in the
Who-owns-what table. It breathes on that file's own cycle, and only the character bobs: a
screen that moved with the presenter would read as held rather than stood in
front of, which is the one thing this icon is not saying. The moving pages are what tell the
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

Its right column is two shapes, one per cadence — the scheduled card and the
on-demand card — and both are built by one `card()`: a header naming the
cadence, then the paths that share it. A fourth track is a fourth path; a
fifth cadence is what would earn a third card. Nothing is ruled between the
paths, because a divider inside an output card groups or ranks, and the only
thing these share is the cadence already named above them. The `context/`
card is the one that keeps a divider, and there it separates two documents a
run reads for different reasons.

That card is also the palest thing in the drawing. It is the one card the
agent may not write, and reading as a quieter ground than the outputs is how
the picture says so before any label does — which is also why the two output
cards clear it by more than the gap between their own edges. They overlap it
horizontally, so a thin gap would read as one stack of three boxes rather
than an input and two outputs.

The drawing ends at those two cards. It runs arXiv to files and stops: what a
reader does with a report is a decision rather than a file, and a wire drawn
back into `context/` would end the agent's own arrow at the one folder the
agent may not write.

A path on a card is set in two registers, because it is two things. The folder
is the track a reader is scanning for, and the rest is a filename pattern; set
alike they read as one wall of bold, so the track takes the size and the ink
and the pattern drops to the weight of a note. That pattern is always a `<…>`
placeholder rather than a specimen filename, since the face is a system stack
and a wide substitution needs somewhere to go before it leaves the card through
its right edge.

A card gets no subtitle, because a note under one card and not the others reads
as that output mattering more, when the only difference is the cadence its
header already states.

Before pushing a change here: `python3 assets/build-flow.py --check`.
