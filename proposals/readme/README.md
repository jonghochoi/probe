# proposals/readme/

Five alternative front doors for the root `README.md`, each keeping the brand
lockup, the accent rule, the claim line and the character icons from `assets/`
and changing only how the page talks. `trailer.mp4` walks through the current
README and options A–D, light and dark.

| File | Direction | Leads with |
|---|---|---|
| [`A-track-gallery.md`](A-track-gallery.md) | Track Gallery — the five tracks as a row of 64 px icons | the characters themselves |
| [`B-a-day-with-probe.md`](B-a-day-with-probe.md) | A Day with PROBE — one day told in five timed scenes | the workflow as a story |
| [`C-manifesto.md`](C-manifesto.md) | Manifesto — three statements, everything else folded | a one-screen pitch |
| [`D-terminal-quickstart.md`](D-terminal-quickstart.md) | Terminal Quickstart — a console transcript and a cheat sheet | the commands |
| [`E-one-stage.md`](E-one-stage.md) | One Stage — today's text, with every character but the lockup gathered into one picture | the pipeline, cast included |

Option E keeps the current README's wording and drops the seven inline
icons from its tables and turns the reading-site banner into a text link. Each character instead stands in `stage.svg` at the
spot that carries its meaning — the human beside `context/`, the lost probe at
the arXiv pile, the locked probe at the filter, and each track icon beside the
path it writes. `build-stage.py` generates `stage.svg` and `stage-dark.svg`
from `assets/build-flow.py`'s geometry, inlining the icons from `assets/`.

Once one is picked, its text replaces the root `README.md` and this folder is
deleted.
