# docs/voice/

Snapshot of the authoring voice that `/readable-paper` writes in. Vendored,
not linked: PROBE must build and generate without `revoice` present, and a
voice that changed underneath a running prompt would silently change 92 papers'
worth of output. This mirrors `revoice`'s own `voice_version: git:<sha>`
convention — the voice is pinned, and updating it is a deliberate act.

## Pinned source

| Field | Value |
|---|---|
| Source repository | `https://github.com/jonghochoi/revoice` |
| Pinned commit | `341d3c088e52300e1fa63fa50384052f87105255` |
| Commit date | 2026-06-22 |
| Commit subject | `voice: quick 어미=폴라이트(반말 금지) 로컬 명시 + 반말 부정 앵커` |
| Source path | `style/voices/base/` |

| File | sha256 |
|---|---|
| `base/voice.md` | `d3a8a200dd87fce56e50daf3db7c1b632cc4f5c20bb8440e6e2a70e8b573368c` |
| `base/examples.md` | `45a46bd69220392da5f6a330de13a261f1c4dfa829a03abae88e0ec7be7b94b7` |

## Read-only

Both files are byte-identical copies. Do not hand-edit them — an edit here
diverges from the upstream voice with no record of how, and the sha256 rows
above stop meaning anything. Fix the voice in `revoice`, then refresh.

## Refreshing

```bash
git -C ../revoice pull
cp ../revoice/style/voices/base/{voice,examples}.md docs/voice/base/
git -C ../revoice rev-parse HEAD          # → update the Pinned commit row
sha256sum docs/voice/base/*.md            # → update the file rows
```

Then re-read `.claude/prompts/readable.txt` against the diff: a voice change
can invalidate the prompt's own examples. Existing `analysis/<id>/readable.md`
files are **not** regenerated — they record the voice they were written
against, and rewriting 92 documents because an 어미 rule moved is not an
improvement.

## What the prompt takes, and what it does not

`readable.txt` adopts the **불변 DNA (9조)** and deep mode's **복원 하한**
(restoration floor). It deliberately does **not** adopt two things from
`voice.md`'s deep overlay:

- **개조식 전용 골격.** The readable layer's structure is fixed by
  `docs/style.md` §5-9 (four acts, per-section quizzes, inline term anchors).
  Deep mode's outline-only skeleton would fight it.
- **The `` ``` ``-wrapped section bodies.** That is a workaround for
  github.com collapsing line breaks in rendered markdown. `readable.md` is
  rendered by `scripts/build-site.py`, which preserves structure natively —
  wrapping bodies in fences here would publish them as literal code blocks.
