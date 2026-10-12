# assets/CLAUDE.md

Rules for the images the root `README.md` embeds. The site's own images live
under `site/builder/assets/` and are unrelated to this folder. Repo-wide rules
are in the root `CLAUDE.md`.

## What is in here

Every image is a light/dark pair (`<name>.svg` + `<name>-dark.svg`) selected by
`<picture>` + `prefers-color-scheme`, and the two files of a pair differ only in
their colours.

| File | Role |
|---|---|
| `hero.svg` (880×330) | The front door, and the link to the reading site. The headline, the claim and the button on the left; on the right, one 25 s cycle in two scenes — the flood, then the reader |
| `own.svg` (880×204) | The picture under How it works — who writes what: you and `context/`, the probe that reads it, and the four folders it writes |
| `probe-scouting.svg`, `probe-analysis.svg`, `probe-comparison.svg`, `probe-presentation.svg`, `probe-ideation.svg` | The five track icons, each above its track's name in the How-it-works table |
| `build-art.py` | Generates `hero` and `own`. The five track icons are hand-authored |

## Drawing rules

**Text is live `<text>`.** Every file is SVG whose text is real text, so the
fonts are stacks (`ui-monospace`, `system-ui`) and every run is anchored with
room to spare, so a wider substituted face grows into space rather than into
its neighbour. An image that carries text repeats it in `aria-label` and in the
`alt` the README embeds it with.

**Rectangles are files.** A card in the feed is a paper, a row in `own.svg` is a
folder, a frame holds files. The one rounded shape that is not a file is the
hero's button, and it is a pill so it cannot be read as one.

**The accent draws the edge a reader meets first.** A frame standing on the
README's own page — the hero's card, the two frames in `own.svg` — takes the
accent (`#D97757`, `#E8916F`) over the shared card ground (`#FFFCFA`,
`#211C19`). A shape inside a frame keeps the neutral border (`#E8CDBD`,
`#3D3129`). `context/`'s frame also carries a hairline just inside its edge:
the one set of files the agent may not write, held in a matte.

**The character's parts carry meaning, so they are not mixed.** Eyes belong to
the probe alone, and so does the sprout on its head — a stem and two leaves
that sway about the stem's root on a 3.2 s cycle, off the bob's beat. The
person in `own.svg` — and the listener in `probe-presentation.svg`, the same
glyph scaled — is the probe's clay and shadow with no face and no sprout, and
breathes on its own 4.6 s cycle rather than the probe's bob. The out-of-it
probe is the same character dimmed, its sprout wilted and its eyes crossed; the
only thing its eyes do is pulse, the two a half beat apart. A prop is placed or
worn, never gripped: a handless probe holds nothing, so the page rides under
its eyes, the mug stands on the ground beside it, the scouter hangs from the
hull's edge, the deerstalker sits on its head with the reading stone lying on
the page, and the bulb hangs over it where a thought would.

**Each track icon shows its track working, and its outline is what does the
work.** At the 64 px a table cell gives them, the only thing that survives is
the shape around the face: `probe-scouting.svg` takes a reading (a scouter over
the right eye — a round green lens in a purple ring, the earpiece on the hull's
edge, and on its antenna a green Wi-Fi mark of a dot and two arcs that never
touch and light in turn — whose dial, dots in the ring's purple, fills one by
one until the lens flashes, the scouter shakes and both pupils shrink),
`probe-analysis.svg` reads like a detective (a tweed deerstalker whose ear
flaps hang at the hull's sides, one wide page under the eyes and a reading
stone sliding along its first line, until the stone stops, the flaps spring
up and a red `!` pops over the cap), `probe-comparison.svg` rallies (two
pages standing at the hull's sides bat a yellow ball back and forth, faster
each time, the pupils chasing it, until it hits the top of the head — the
probe reels, a red bump swells where it hit and the ball dribbles to a stop
at its feet), `probe-presentation.svg` presents (a screen up and to the
right whose bands light as a talk advances, one listener in front on the
left, cut by the bottom edge, until the bands glitch and the screen crashes
to a blue `:(` — the presenter freezes and sweats with shrunken pupils, the
listener tilts its head, and the slide comes back), and `probe-ideation.svg`
has an idea (pupils up at a bulb over the head that flickers like a tired
tube, catches, and glows so bright the probe squints). A new track needs a
new outline, not a variation on one of these.

**Every track icon builds to one beat.** The scouter's dial is the model:
something mounts over the cycle and a single beat releases it — the flash,
the `!`, the bump, the crash, the glare — so each icon lands a punchline
rather than idling in a loop. Hues outside the clay come only with a prop
and stay on it: the scouter's green and purple, which no other icon uses,
the deerstalker's tweed, the ball's and the bulb's yellow, the crashed
screen's blue, and the red of the `!` and the bump. A blue sweat drop is
the probe's one sign of strain that is not a prop. With motion off, an icon
rests before its beat — the ball between the pages, the screen lit, the eyes
open.

**An icon shares its track's cell, never a column of its own.** A table
column that holds only an image has no minimum width — GitHub caps every image
at `max-width: 100%` — so when the page is narrower than the table, the
browser squeezes that column first and the icons shrink to nothing. Stacked
above the track's name, the name holds the cell open.

**Animation is inlined and stays in step with the site.** A README image
carries no external stylesheet, so every motion lives in the file's own
`<style>`, and `prefers-reduced-motion` stops all of it. The character is
`site/builder/components.py`'s `mark()` redrawn: change `mark()` and these
change with it.

## The hero

The right half runs one 25 s cycle in two scenes, so the contrast the Why
table draws is on the first screen.

- **The flood, 0–34 %.** The out-of-it probe, while loose papers fall where
  the feed will stand — never on the probe — under the label
  `arXiv · 50–100 A DAY`.
- **The reader, 40–96 %.** The probe reading with its coffee, and the feed,
  under `PROBE · 3–5 A WEEK`. The feed fades in with the reader, so nothing
  is picked while the probe is out of it.

A card is marked where it crosses a reading line, with nothing drawn at the
line itself. Which rows are marked follows from the geometry, so moving the
line, the rows or the speed moves the keyframes — which is why the hero is
generated (`build-art.py` comments carry the constraints). The count lives in
each scene's label, never in a line under both: that would show the result
while the probe is still drowning.

## Who writes what

`own.svg` is one row: you, the `context/` frame, the probe, and the frame of
four folders, symmetric about the two frames. The one wire is `context/` into
the probe, labelled *reads*. Nothing is drawn from the probe to its folders —
the PROBE WRITES label says it — and nothing back into `context/`, which the
agent never writes; the caption says a change comes to you as a proposal. The
frame names `P#.md`, never a count of pillars, so adding one does not date the
picture.

## Generating

`hero` and `own` are written by `build-art.py` from one source per image,
light and dark from the same markup. Edit the script, never the SVG. Before
pushing a change here: `python3 assets/build-art.py --check`.
