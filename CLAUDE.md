# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

PROBE is a research-scouting agent for dexterous manipulation. A human owns
the static research context in `context/`; two agent tracks read it and
write decision-grade Korean output — a scheduled per-pillar routine into
`scouting/`, and on-demand `/analyze` into `analysis/`, which the reading site
publishes. See `README.md` for the motivation and the pipeline; this file is
the contributor-facing reference for **commit hygiene and document style** so
the repo stays consistent.

## Repository map

| Path | Owner | Role |
|---|---|---|
| `README.md` | human | Project front door — motivation, the pipeline, and which track to trigger for what. It links the headline docs in prose; **this table is the full path index** |
| `SETUP.md` | human | Operator guide for the scheduled scouting routine — RemoteTrigger form, network allowlist, `SEMANTIC_SCHOLAR_API_KEY`, first-run verification. Scouting only; on-demand `/analyze` needs no routine setup |
| `context/MASTER.md` | human | Global anchor — cross-cutting content only: Identity, Purpose, Long-term Context, Hardware, Pillars overview (P0–P5), Venue, Cross-pollination |
| `context/P{0..5}.md` | human | Per-pillar **owners** of the Decision Log, Tracked Literature, Anti-topics, and Curated Lists (identical §1–§6 skeleton). A run reads one `P#.md`. Six pillars P0–P5 (P0 data, P1–P4 architecture core, P5 World Model). Decision allocation: P1 D1–D7, P2 D8–D12, P3 D13–D18, P4 D19–D23, P0 D24–D27, P5 D28–D32. New pillar: copy `context/_TEMPLATE.md` and walk "When adding a new pillar" below |
| `scouting/` | agent | Scouting Reports (`P#/YYYY-MM-DD.md`, per pillar, on a scheduled cadence). `scouting/templates/report.md` is the skeleton they fill |
| `scouting/AUTHORING.md` | human | Format contract for the `scouting/` track — emoji system, the Reference Legend and its pillar palette (§3-1), link rules, Korean authoring principles |
| `analysis/` | agent | The site's corpus — one `<arxiv-id>.md` per paper (flat, no per-paper folder), from `/analyze`. A Korean re-telling written from the paper's **arXiv HTML original**, carrying its own metadata in front matter. One file publishes as **two tabs** — a one-screen 요약 (`::: glance`, the tab a reader lands on) and the body — both written in the same run from the same reading of the original. Contract: `site/AUTHORING.md`, never `scouting/AUTHORING.md` |
| `site/AUTHORING.md` | human | Format contract for `analysis/<id>.md` — front matter (§1), body rules R1–R15 (§2), what publishes as literal text including the KaTeX math forms (§3), the 요약 tab G1–G7 (§4), enforcement (§5) |
| `analysis_legacy/` | frozen | Legacy corpus — one `<arxiv-id>/analysis.md` per paper, in a format nothing else in the repo uses. **Read by nothing** (prompt, site build and every lint skip it) and never regenerated; kept until those papers are re-written under `analysis/`. Its `README.md` is a static index of what the folder holds |
| `.claude/prompts/**` | human | Externalized, durable agent prompts (the repo's real asset) — `scouting.txt` (the scheduled routine, one instance per pillar via the `<PILLAR>` token) and `analyze.txt` (`/analyze`) |
| `.claude/commands/**` | human | Slash-command wrappers — `analyze.md`, which only points `/analyze` at its prompt and at `site/AUTHORING.md` |
| `assets/` | human | Images the root `README.md` embeds, plus the one script that bakes a pair of them — the brand lockup (`wordmark.svg`) that **is** the README's H1, the reading-site banner (`reading-site.svg`), the two state icons heading the Why-PROBE comparison columns — `probe-lost.svg` (out of it: dimmed hull, drooping beacon, crossed-out eyes) and `probe-locked.svg` (on target: clay hull, a beacon under signal arcs, smiling eyes) — and the How-it-works flow diagram (`flow.svg`, 880×336: the day's arXiv narrowing through the filter into the mark, out to the two output chips, and back through the human to `context/`) — each as a light/dark pair (`-dark.svg`) selected by `<picture>` + `prefers-color-scheme`. Every one of them is SVG whose text is live `<text>`, so the fonts are stacks (`ui-monospace`, `system-ui`) and the layout is left-aligned to tolerate the substitution. Rectangles are files and only files — the human rides the return wire as a bare label, never a card. The flow diagram is the one image generated rather than hand-edited: `build-flow.py` writes both files from one set of coordinates (`--check` fails when they drift from it), because moving any of its twenty-odd elements drags the wires, arrowheads and keyframes pointing at it. Its picking cycle runs 9 s — a scan band marks six papers as it crosses their column, three are culled inside the filter (each greys and fades out, still a circle), three land in the kept column — and its durations are literal rather than `var()`, since a `:root` custom property resolves only while the SVG is its own document and an unresolved duration drops the animation. The lockup, both state icons and the flow diagram redraw `site/builder/components.py`'s `mark()` with their animation inlined, since a README image carries no external stylesheet — the lockup runs the full cycle (bob, signal, blink, wink and the mood swap between round pupils and smiling arcs), each icon one fixed mood; keep the drawings in step. The site's own images live under `site/builder/assets/` and are unrelated |
| `site/` | human | The reading site's generator — `build-site.py` + `builder/` (a landing briefing, a memo hub, plus one page per rewrite) and `requirements.txt`. Only `analysis/` is published; `analysis_legacy/` is not read. `--check` lints and writes nothing, `--strict` fails on any warning, `--serve` previews locally under the deployed path. Generated HTML is **never committed**. A rewrite publishes as two tabs and the short one has its own module — `site/builder/glance.py` (요약), which refuses any `D#` on its surface. Two modules serve the prompt rather than the build: `site/builder/arxiv.py` (LaTeXML extraction of an arXiv original — body **and appendix** sections, figures including the `<object>`-embedded SVGs, tables; raises `Unavailable` when a paper has no HTML edition, which is `/analyze`'s stop condition) and `site/builder/mdext/probefence.py` (the ` ```probe-* ` fences and their validation). Folder map: `site/README.md` |
| `site/search/` | human | Semantic search for the reading site — `chunks.py` (cuts `analysis/` into retrievable passages: sections, term panels, figure captions; offline), `schema.sql` (the InsForge migration: pgvector HNSW + tsvector, plus the `SECURITY DEFINER` RPCs that are the only way into either table — `probe_search` fusing both arms, and the two query-cache accessors), `indexer.py` (embeds and uploads; stdlib only) and `function/search.ts` (the public endpoint, which reads a query into search terms before embedding it — `플로우매칭` finds `flow matching`). Indexes the published corpus and nothing else. Enhancement only: a build without `--search-api` emits no script and the site makes no request. Folder map: `site/search/README.md` |
| `linters/check-doc-links.py` | human | Linter verifying local path references resolve in `CLAUDE.md`, `README.md`, `SETUP.md`, `context/MASTER.md` and `context/P#.md` (`_TEMPLATE.md` is skipped — it is placeholders). Automates the "no orphan / no dangling path" step of "When adding a new top-level doc" below |
| `linters/check-decision-refs.py` | human | Linter verifying every `D#` citation in `analysis/*.md` / `scouting/P*/*.md` exists in the per-pillar Decision Log and that explicit `P# / D#` ties match the owning pillar |
| `linters/check-scouting-format.py` | human | Linter validating `scouting/P#/YYYY-MM-DD.md` against the `scouting/AUTHORING.md` output contract — metadata block (§6), emoji system and section order (§2), the scoring contract (§5: five rubric bullets, no self-contradicting Reproducibility score, code label, `★★★` ceiling) and one-paper-per-row tables (§7-3). Binds reports dated on or after the linter's `_CONTRACT_EFFECTIVE`; earlier reports are the record of runs under the contract of their day. Scouting reports reach `main` without a PR, so the **blocking** gate is the routine's own pre-commit self-check (`.claude/prompts/scouting.txt` → SELF-CHECK, which refuses to commit a report the lint rejects) and CI is the backstop behind it |
| `linters/check-commit-style.py` | human | Linter validating commit subjects / PR titles against the "Commit message style" grammar below (type set, casing, length, non-imperative first words, generated-routine formats). Local use: `git log --format=%s main..HEAD \| python3 linters/check-commit-style.py -` |
| `.github/workflows/` | human | Five gates. The four lints above run PR-time (`check-doc-links`, `check-decision-refs`, `check-scouting-format`, `check-commit-style` — the last reads the **PR title**, since squash-merge makes it the landing subject). `check-scouting-format` also fires on `push` to `main`, the path scouting reports actually take. `deploy-site.yml` builds the site on every PR touching `analysis/` or `site/` and deploys to Pages only from `main`, where it also refreshes the semantic index when the InsForge secrets exist |

`context/` is read-only to the agent — it may *propose* changes in a report,
never edit the source. Per-pillar content (Decision Log, Tracked Literature,
Anti-topics, Curated Lists) is **owned by the relevant `P#.md`**; `MASTER.md`
is a thin global anchor holding only cross-cutting content. Edit the `P#.md`
for pillar content, `MASTER.md` only for global content.

**Decision-Log entry format.** Every entry in a `P#.md` §3 Decision Log has
exactly this shape (used 32× across the six pillars; the scouting / analyze
prompts and lint tooling pattern-match on it, so it is load-bearing, not
cosmetic):

```
#### [D<n>] <Decision title> (P<m>)
- **v1**: <current first-attempt choice — **bold** the chosen alternative;
  tracked/deferred alternatives named inline; `OPEN` decisions append
  ` — **OPEN**` to the title line and mark the bullet `(working, not settled)`>
```

One `####` heading + one `- **v<k>**:` bullet per decision. `D<n>` stays
within the pillar's allocated range and is never renumbered; superseding a
choice bumps the bullet to `**v2**:` (etc.) in place — the old version's
rationale lives outside the context file, not as a second bullet.

## Commit message style

All commits follow a single, consistent style — derived from this repo's own
history (`git log`), not a generic "Conventional Commits" template. Match the
patterns below exactly; don't invent a new shape per commit.

### Subject line

```
<type>(<scope>): <verb> <description>
<type>: <verb> <description>           # scope optional when the change is repo-wide
```

Hard rules:

1. **Always start the description with an imperative verb** — the most
   important rule and the one that drifts most easily. The first word after the
   colon must be a verb in imperative mood. Past tense (`added`, `fixed`),
   gerunds (`adding`), and noun-first phrases (`new mode for X`) are forbidden.
   Verbs already used in this repo's history (use one of these or a close
   synonym): `add`, `drop`, `remove`, `prune`, `move`, `rename`, `restructure`,
   `reduce`, `compress`, `tighten`, `retire`, `restore`, `recover`, `keep`,
   `render`, `codify`, `re-align`, `re-cut`.
2. **`<type>`** — one of `feat`, `fix`, `refactor`, `docs`, `chore`, `style`,
   `deps`. Don't invent new types. (The bare `scout:` / `analysis:`
   prefixes are *generated routine commits*, not human
   commits — do not imitate them when authoring code/doc changes. Their
   canonical formats, one per generating prompt:
   `scout: P{N} report YYYY-MM-DD`, and
   `analysis: add <arxiv-id> rewrite (<alias>)` for `/analyze`
   (`update` instead of `add` when redoing an existing rewrite). The trailing
   `(<alias>)` is the paper's codename, resolved in priority order: (1) the
   prefix before the first colon in the paper's own title
   (e.g. `LaST-HD`, `Being-H0.7`, `T-Rex`); (2) failing a colon, an acronym
   the paper explicitly defines for itself as `ACRONYM (Full Expansion)` in
   the title / abstract / intro whose expansion initials spell the acronym
   (e.g. `Human Universal Grasping` → `HUG`); (3) failing both, the name the
   authors give their own method in the paper's own prose — introduced as
   "we propose X" / "we call it X" / "our X" and used as the method's
   designator from there on — **even when the paper never expands it**
   (e.g. `DQ-RISE`). It qualifies only if it reads as a proper name: capitals,
   digits or a hyphenated compound, not a descriptive noun phrase, so
   "our quantized hand state policy" yields nothing; (4) otherwise omitted —
   a plain descriptive title whose method is never given a name of its own
   gets no alias, and one is never invented.)
3. **`<scope>`** — lowercase, naming the folder or track the change touches:
   `site`, `scouting`, `analysis`, `context`, `prompts`, `linters`,
   `ci` (`.github/workflows/`), `config`. Omit the scope for repo-wide
   changes — a docs pass across several tracks is `docs: …`, never
   `docs(docs): …`.
4. **Description** — lowercase first letter (after the colon), no trailing
   period, ≲ 72 chars including the type/scope prefix. State *what* the commit
   does, not why (the why goes in the body).
5. **Do NOT include `(#NN)` in the local commit subject** — GitHub appends the
   PR number automatically on squash-merge; adding it manually duplicates it.
6. **Write the commit message in English** — subject *and* body — even when
   describing Korean-authored content, so `git log` stays uniformly grep-able.

Good (from this repo's history):

```
feat(site): add callout, tagline and parts-state rules
fix(site): recover the appendix and the SVG figures from arXiv originals
refactor(site): drop five helpers left without callers
chore(ci): add the GitHub Pages deploy workflow
docs: codify the body H1 as the rewrite's thesis line
```

Bad (don't do this):

```
Added analysis mode                            # past tense, no type, capitalized
feat: new deep-dive mode.                       # noun-first, trailing period
docs(README): Updates the structure section.   # 3rd-person, capitalized, period
update prompts                                  # no type, vague verb "update"
```

### Body

Optional for trivial one-liners; required for any commit that touches more than
one logical area or needs context to be reviewable. When present:

1. **Blank line** between subject and body.
2. **Wrap at ~72 columns**. Prose and bullets wrap; URLs and code blocks may
   exceed.
3. **Lead with the *why*** — one short paragraph stating the problem or
   motivation before listing the *what*.
4. **Lists for multiple changes** — `-` bullets for parallel small changes;
   `1.` `2.` numbered items when sequenced or referenced by number.
5. **Per-file groupings** for larger commits: file path on its own line ending
   with `:`, then an indented bullet list of changes for that file.
6. **Unicode dividers** for the largest commits (a `feat`/`refactor` touching
   many files, or a repo-wide `docs:` pass). Use `─` (U+2500) — never `-` or
   `=` — padded so the line ends near column 72:

   ```
   ── 1. Path migration ─────────────────────────────────────────────────
   ```

7. **Em dash `—` (U+2014)**, not ` - `, when joining a label to its
   explanation in body prose.
8. **Backticks** around paths (`context/MASTER.md`), identifiers, CLI flags
   (`--dry-run`), and shell commands.

## Local checks

CI runs each of these on the PR. Run the ones your change touches before
pushing, so a red gate is not the first you hear of it.

| Change touches | Command |
|---|---|
| any doc in the index set | `python3 linters/check-doc-links.py` |
| `analysis/`, `scouting/`, `context/` | `python3 linters/check-decision-refs.py` |
| anything (the PR title is the landing subject) | `git log --format=%s main..HEAD \| python3 linters/check-commit-style.py -` |
| `analysis/` or `site/` | `python3 site/build-site.py --check --strict` |
| `assets/build-flow.py` | `python3 assets/build-flow.py --check` |

The site build is the only one with dependencies:
`pip install -r site/requirements.txt`.

## Document Markdown style

Probe docs fall into two families. The rule **codifies the existing
convention** — it does not strip emoji.

### Narrative / onboarding docs

`README.md`. The H1 is the **brand lockup** — the `<picture>` pair in
`assets/` on one line inside the `#`, with the project name as the image's
`alt` so the heading still reads as text everywhere the image does not. A
narrative doc with no lockup of its own may instead carry **one leading
thematic emoji**, placed at the start of the header text after the `#` and a
space (`# 🛸 …`) — exactly one, at the start, never at the end and never
inside body text. One H1 per document.

**Internal consistency per level (hard rule).** Each header level used in a
document must be uniformly marked or uniformly plain — no mixing within the
same level in the same doc. The canonical narrative pattern in this repo is
**the mark at H1 only, plain at H2 and below**, used by `README.md`. If you
add a new H2/H3, it stays plain; outliers must be brought into line, not left
as exceptions.

### Reference / structural docs

`CLAUDE.md`, `SETUP.md`, `scouting/AUTHORING.md`, `site/AUTHORING.md`,
`site/README.md`. Plain headers, **no emoji**.
Numbered headers (`## N.`, `### N-M.`) are allowed and match the existing
`scouting/AUTHORING.md`. A folder README's H1 is the folder name
(e.g. `# analysis/`).

### Shared rules (both families)

- One H1 per document.
- Backticks around paths, identifiers, CLI flags, shell commands.
- Em dash `—` (U+2014), not ` - `, when joining a label to its explanation.
- Hyphen-minus `-` stays for compound words and CLI flags only.

### What this rule does NOT govern

This document-style rule is about Markdown **formatting only**. It does **not**
apply to:

- `context/MASTER.md`, `context/P{0..5}.md` — human-owned research input with
  its own `[STABLE]` / `[AGENT-INPUT]` section schema.
- `.claude/prompts/**`, `.claude/commands/**` — agent prompts, free-form.
- Agent-generated output and its templates — `scouting/templates/report.md`
  and the dated reports. These follow `scouting/AUTHORING.md`'s own emoji system (one
  emoji on each `##` header, `###` and below plain) plus its Korean
  conventions.
- `analysis/<id>.md` and the reading site — a separate track with its own
  contract in `site/AUTHORING.md` (four-act spine, ` ```probe-* ` fences, GFM
  alert callouts), enforced by `site/build-site.py`.
- **Math / formula rendering** — the GitHub-KaTeX `$`-wrapping and substitution
  rules are an *output* convention, not a contributor-doc one, so they live in
  `site/AUTHORING.md` §3-1 (enforced by the site build), not here.

Path correctness is **not** exempt: when a path moves, references inside
prompts and context files are still updated even though their formatting is
not governed here.

## Document language convention

PROBE is a Korean-first repository — most outputs are decision-grade Korean
prose for an internal team — but the contributor-facing surface stays in
English so `git log`, PR threads, and external collaborators read uniformly.
Use this rule as the single source of truth for "which language should a
new doc be in?":

- **Default — Korean (한글).** All agent outputs — the per-paper rewrites
  `analysis/<id>.md` and the `scouting/` reports — are Korean. Templates that
  those folders ship (`scouting/templates/`) are Korean as well.
- **Exception 1 — Contributor / style / operator docs in English.**
  `CLAUDE.md`, `SETUP.md`, `scouting/AUTHORING.md`, `site/AUTHORING.md`,
  `site/README.md`. The audience is anyone reading PRs or history; English
  keeps that surface grep-able and consistent with the enforced English
  commit-message rule.
- **Exception 2 — Project front door in English.** `README.md`. The
  GitHub-rendered top page is the public-facing entry and the single
  onboarding surface for a newcomer.
- **Exception 3 — The legacy folder index in English.**
  `analysis_legacy/README.md` — a static index of that folder (English paper
  titles + keyword/pillar badges) above a short structural intro. A folder
  README whose H1 is the folder name (`# analysis_legacy/`).

**No `_KO` / `_EN` filename suffix.** Location (the folder rule above) plus
the H1 on line 1 are sufficient — `head -1 <file>` tells you the language
in one command. Do not add a language suffix to a new document just to
disambiguate; if the rule above does not place the doc unambiguously, the
doc is in the wrong folder.

## No change history in code or guides

Code comments, docstrings and guides describe **what the repo is now**. When a
requirement changes, the text that stated the old requirement is rewritten to
state the new one — not annotated with what it used to say. `git log`, the PR
thread and the commit body are where the change lives; a comment that also
carries it goes stale the next time the rule moves, and a reader cannot tell
which half is current.

What this rules out, in a comment, a docstring, a rule in
`scouting/AUTHORING.md` / `site/AUTHORING.md`, or a prompt:

- **Past forms** — "X used to be Y", "this was previously a Z", "no longer
  holds", "the earlier trigger did …".
- **Change narration** — "renamed from", "moved out of", "added in the
  restructure", "kept for now".
- **Incident logs** — "three separate bugs came from this", "which is how one
  rewrite ended up redrawing a figure". The failure mode is worth stating; its
  history is not. Write it in the present, as the thing that happens: "a rule
  like `.X b{display:block}` catches body emphasis and breaks the line".

Rationale is not history and stays. "This is a barrier because stage N needs
every stage N-1 result" explains a live design; "this used to be a pipeline"
explains nothing a reader can act on. When a rule's reason is a failure mode,
state the failure mode in the present tense and drop the date it happened.

Dead code and dead rules are deleted, not commented out or marked deprecated —
the same rule, applied to the code itself.

## When adding a new top-level doc

Probe has no cross-link automation — every doc reference is hand-maintained.
A new doc that is only added to the filesystem without updating the index
becomes a silent orphan. Walk this list every time:

- [ ] **Classify the doc** — narrative/onboarding (H1 emoji allowed) or
      reference/structural (plain headers). Pick one consistently per the
      table above and do not mix levels.
- [ ] **Pick the location** — a doc governing one track lives in that track's
      folder (`scouting/AUTHORING.md`, `site/AUTHORING.md`); repo-wide
      contributor, governance and operator docs sit at the repo root next to
      `CLAUDE.md`. Those two are the only options — a doc that fits neither
      belongs in one of them rewritten, not in a new folder.
- [ ] **Add a row to the "Repository map" table in this file (`CLAUDE.md`).**
      That table is the canonical path index; the root `README.md` links only
      the headline docs in prose, so wire a new doc in here.
- [ ] **If it pins paths that live elsewhere** (templates, prompts, output
      files), grep the new doc against the current layout — every
      referenced path must resolve.
- [ ] **Run a final `grep -rn '<new-doc-basename>' .`** — at least one
      inbound link must exist. Zero inbound links = orphan.
- [ ] **Run `python3 linters/check-doc-links.py`** — every local path
      reference in the index set (`CLAUDE.md`, `README.md`, `SETUP.md`,
      `context/MASTER.md`, `context/P#.md`) must resolve. This lint is the
      automated backstop for the dangling-path half of this checklist. Pass
      the prompts or either `AUTHORING.md` as explicit args to scan them too;
      they are off the default set because they carry illustrative example
      paths.

## When adding a new pillar (P6+)

The six existing pillars share an identical §1–§6 skeleton, and several
surfaces key off the pillar set — none of them update automatically. Walk
this list end to end; a half-added pillar silently drops out of the index
and the lints:

- [ ] **Copy `context/_TEMPLATE.md` to `context/P<N>.md`** and fill every
      `<placeholder>`. Keep the §1–§6 section spine and the
      `[STABLE]`/`[LIVING]`/`[AGENT-INPUT]` markers exactly — the pipeline
      pattern-matches on them.
- [ ] **Allocate a fresh, contiguous Decision range** (`D33+` — never reuse
      or renumber an existing `D#`). Record the allocation in three places:
      the new `P<N>.md` §3 header, the `context/P{0..5}.md` row of this
      file's Repository map, and `context/MASTER.md` §5's pillar table.
- [ ] **Add the pillar overview** to `context/MASTER.md` §5 (scope, identity
      tie, tracked items — mirror the existing §5.N blocks).
- [ ] **Create `scouting/P<N>/`** and deploy a scouting routine instance for
      it (replace every `<PILLAR>` token in `.claude/prompts/scouting.txt`
      per `SETUP.md`).
- [ ] **Extend the pillar-keyed tooling**: `PILLAR_NAMES` / `PILLAR_ORDER` /
      `PILLAR_RE` in `site/builder/corpus.py` (an out-of-range `P#` lands
      the paper in 미분류 on the site) and the §3-1 palette table in
      `scouting/AUTHORING.md` (the palette's source of truth). The lints pick
      the new pillar up on their own — both glob `context/P*.md`.
- [ ] **Run `python3 linters/check-doc-links.py`** — the new file's path
      references (and every doc now referencing it) must resolve.

## Where to read more

- `README.md` — motivation, the pipeline, and which track to trigger for what.
- `scouting/AUTHORING.md` — the output format for the `scouting/` track (this
  file governs commits and *contributor* docs, not output).
- `site/AUTHORING.md` — the output format for the reading-site track
  (`analysis/<id>.md`); `site/README.md` maps the generator around it.
- `SETUP.md` — deploying the scouting routine (RemoteTrigger form, network
  allowlist, first-run verification); the track itself is described in
  `README.md` → Pipeline.
