# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

PROBE is a research-scouting agent for dexterous manipulation. A human owns
the static research context in `context/`; agent tracks read it and write
decision-grade Korean output — a scheduled per-pillar routine into `scouting/`,
on-demand `/analyze` into `analysis/` and `/compare` into `comparison/`, the
last two published by the reading site. `README.md` carries the motivation and
the pipeline; this file is the contributor-facing reference for **commit
hygiene and document style** so the repo stays consistent.

## Where the rules live

Repo-wide rules — commit hygiene, contributor-doc style, the local checks —
are in this file and bind every change. A rule that binds one folder lives in
that folder's own `CLAUDE.md`, next to the code it governs:

| Rule file | Binds |
|---|---|
| `CLAUDE.md` (this file) | the whole repo — commits, contributor docs, the checks |
| `context/CLAUDE.md` | `context/` — who may edit it, the Decision-Log entry format, adding a pillar |
| `assets/CLAUDE.md` | `assets/` — the README images, the character and its moods, `build-flow.py` |
| `site/CLAUDE.md` | `site/` — the generator's invariants and the surfaces keyed to the pillar set |

Output format is a third thing, one contract per track, owned by the track and
never restated in a prompt: `scouting/AUTHORING.md`, `analysis/AUTHORING.md`,
`comparison/AUTHORING.md`. A folder's `README.md` maps what is in it
(`site/README.md`, `site/search/README.md`) and states no rules.

## Repository map

This table is the canonical path index — the root `README.md` links only the
headline docs in prose. One line per path; anything that needs more than a line
belongs in that folder's own rule file or README, which the row points at.

| Path | Owner | Role |
|---|---|---|
| `README.md` | human | Project front door — motivation, the pipeline, and which track to trigger for what |
| `SETUP.md` | human | Operator guide for the scheduled scouting routine — RemoteTrigger form, network allowlist, `SEMANTIC_SCHOLAR_API_KEY`, first-run verification. Scouting only; `/analyze` and `/compare` need no routine setup |
| `context/MASTER.md` | human | Global anchor — cross-cutting content only: Identity, Purpose, Long-term Context, Hardware, Pillars overview (P0–P5), Venue, Cross-pollination |
| `context/P{0..5}.md` | human | Per-pillar **owners** of the Decision Log, Tracked Literature, Anti-topics and Curated Lists (identical §1–§6 skeleton). A run reads one `P#.md` |
| `context/_TEMPLATE.md` | human | The §1–§6 skeleton a new pillar is copied from |
| `context/CLAUDE.md` | human | Rules for `context/` — the read-only boundary, the Decision-Log entry format and its pillar allocation, the "adding a new pillar" checklist |
| `scouting/` | agent | Scouting Reports (`P#/YYYY-MM-DD.md`, per pillar, on a scheduled cadence). `scouting/templates/report.md` is the skeleton they fill |
| `scouting/AUTHORING.md` | human | Format contract for the `scouting/` track — emoji system, the Reference Legend and its pillar palette (§3-1), link rules, Korean authoring principles |
| `analysis/` | agent | The site's corpus — one `<arxiv-id>.md` per paper (flat), from `/analyze`: a Korean re-telling written from the paper's **arXiv HTML original**, carrying its own front matter. One file publishes as **two tabs** — a one-screen 요약 (`::: glance`, where a reader lands) and the body — both written in the same run from the same reading |
| `analysis/AUTHORING.md` | human | Format contract for `analysis/<id>.md` — front matter (§1), body rules R1–R15 (§2), what publishes as literal text including the KaTeX math forms (§3), the 요약 tab G1–G7 (§4), enforcement (§5) |
| `comparison/` | agent | Comparisons — one `<slug>.md` per comparison, holding two or three papers under one question; the slug is the question, never the ids joined together. **Only papers with a rewrite in `analysis/` may be compared** |
| `comparison/AUTHORING.md` | human | Format contract for `comparison/<slug>.md` — the one rule and its consequences (§1), front matter, the four-act spine, the fence allow-list and the length ceiling (§2), `probe-matrix` (§3), enforcement (§4) |
| `.claude/prompts/**` | human | Externalized, durable agent prompts (the repo's real asset) — `scouting.txt` (the scheduled routine, one instance per pillar via the `<PILLAR>` token), `analyze.txt` and `compare.txt`. Each owns a **procedure** — which papers, where the facts come from, how to verify, how to commit — and delegates every format rule to its track's `AUTHORING.md`; a rule restated in a prompt is a second source of truth that drifts the next time the contract moves |
| `.claude/commands/**` | human | Slash-command wrappers — `analyze.md` and `compare.md`, which only point their command at its prompt and at its track's `AUTHORING.md` |
| `assets/` | human | The images the root `README.md` embeds — the brand lockup that **is** its H1, the state and track icons, the tagline banner and the generated flow diagram — each a light/dark SVG pair, plus `build-flow.py` |
| `assets/CLAUDE.md` | human | Rules for `assets/` — what each image is, the drawing and animation rules, the generated flow diagram |
| `site/` | human | The reading site's generator — `build-site.py` + `builder/`, publishing `analysis/` and `comparison/` and nothing else. Folder map: `site/README.md` |
| `site/CLAUDE.md` | human | Rules for `site/` — the invariants a build change must not break, and the surfaces keyed to the pillar set |
| `site/search/` | human | Semantic search over the rewrites — chunker, InsForge schema, indexer, the public endpoint and the operator's `verify.py`. `comparison/` is published but not chunked. Enhancement only: a build without `--search-api` emits no script. Folder map: `site/search/README.md` |
| `linters/check-doc-links.py` | human | Verifies local path references resolve across the index set — this file, every `CLAUDE.md`, `README.md`, `SETUP.md` and the `context/` files (`_TEMPLATE.md` is skipped — it is placeholders). Automates the "no orphan / no dangling path" step below |
| `linters/check-decision-refs.py` | human | Verifies every `D#` citation in `analysis/*.md` / `scouting/P*/*.md` / `comparison/*.md` exists in the per-pillar Decision Log and that explicit `P# / D#` ties match the owning pillar |
| `linters/check-scouting-format.py` | human | Validates `scouting/P#/YYYY-MM-DD.md` against the `scouting/AUTHORING.md` contract — metadata block, emoji system and section order, the scoring contract (§5) and one-paper-per-row tables (§7-3). Binds reports dated on or after its `_CONTRACT_EFFECTIVE`. Scouting reports reach `main` without a PR, so the **blocking** gate is the routine's own pre-commit self-check (`.claude/prompts/scouting.txt` → SELF-CHECK) and CI is the backstop |
| `linters/check-commit-style.py` | human | Validates commit subjects / PR titles against the "Commit message style" grammar below. Local use: `git log --format=%s main..HEAD \| python3 linters/check-commit-style.py -` |
| `.github/workflows/` | human | Six gates. The four lints above run PR-time (`check-commit-style` reads the **PR title**, since squash-merge makes it the landing subject); `check-scouting-format` also fires on `push` to `main`, the path scouting reports actually take. `check-search-function` parses `site/search/function/search.ts`, which no build reads. `deploy-site.yml` builds the site on every PR touching `analysis/` or `site/` and deploys to Pages only from `main`, where it also refreshes the semantic index when the InsForge secrets exist |

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
   `deps`. Don't invent new types.
3. **`<scope>`** — lowercase, naming the folder or track the change touches:
   `site`, `scouting`, `analysis`, `comparison`, `context`, `prompts`,
   `linters`, `ci` (`.github/workflows/`), `config`. `comparison` covers the
   track's contract and its documents; the build code that publishes them is
   `site`. Omit the scope for repo-wide changes — a docs pass across several
   tracks is `docs: …`, never `docs(docs): …`.
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

### Generated routine commits

The bare `scout:` / `analysis:` / `compare:` prefixes belong to the generating
prompts, not to human commits — do not imitate them when authoring code or doc
changes. One canonical format per prompt:

```
scout: P{N} report YYYY-MM-DD
compare: add <slug>                       # the slug is the question, so no alias
analysis: add <arxiv-id> rewrite (<alias>)
```

`update` replaces `add` when redoing an existing rewrite or comparison. The
trailing `(<alias>)` is the paper's codename, resolved in priority order:

1. The prefix before the first colon in the paper's own title (`LaST-HD`,
   `Being-H0.7`, `T-Rex`).
2. Failing a colon, an acronym the paper explicitly defines for itself as
   `ACRONYM (Full Expansion)` in the title / abstract / intro, whose expansion
   initials spell the acronym (`Human Universal Grasping` → `HUG`).
3. Failing both, the name the authors give their own method in the paper's own
   prose — introduced as "we propose X" / "we call it X" / "our X" and used as
   the method's designator from there on — **even when the paper never expands
   it** (`DQ-RISE`). It qualifies only if it reads as a proper name: capitals,
   digits or a hyphenated compound, not a descriptive noun phrase, so "our
   quantized hand state policy" yields nothing.
4. Otherwise omitted — a plain descriptive title whose method is never given a
   name of its own gets no alias, and one is never invented.

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
| `analysis/`, `scouting/`, `comparison/`, `context/` | `python3 linters/check-decision-refs.py` |
| anything (the PR title is the landing subject) | `git log --format=%s main..HEAD \| python3 linters/check-commit-style.py -` |
| `analysis/`, `comparison/` or `site/` | `python3 site/build-site.py --check --strict` (a comparison's fence and length rules are checked while the page renders, so add `--out /tmp/probe-check`) |
| `assets/build-flow.py` | `python3 assets/build-flow.py --check` |
| `site/search/function/` | `npx esbuild@0.28.2 site/search/function/search.ts --loader:.ts=ts --outfile=/dev/null` |

The site build is the only one with dependencies:
`pip install -r site/requirements.txt`.

## Document Markdown style

Probe docs fall into two families. The rule **codifies the existing
convention** — it does not strip emoji.

**Narrative / onboarding** — `README.md`. Its H1 is the **brand lockup**: the
`<picture>` pair from `assets/` on one line inside the `#`, with the project
name as the image's `alt` so the heading still reads as text everywhere the
image does not. A narrative doc with no lockup of its own may instead carry
**one leading thematic emoji** right after the `#` and a space (`# 🛸 …`) —
exactly one, at the start, never at the end and never inside body text.

**Reference / structural** — every `CLAUDE.md`, `SETUP.md`, the three
`AUTHORING.md` contracts, `site/README.md` and `site/search/README.md`. Plain
headers, **no emoji**. Numbered headers (`## N.`, `### N-M.`) are allowed and
match the existing `scouting/AUTHORING.md`. A folder README's H1 is the folder
name (e.g. `# analysis/`).

Shared by both families:

- One H1 per document.
- **Internal consistency per level (hard rule).** Each header level is
  uniformly marked or uniformly plain — no mixing within one level in one doc.
  The canonical narrative pattern here is the mark at H1 only, plain at H2 and
  below. A new H2/H3 stays plain; outliers are brought into line, not kept as
  exceptions.
- Backticks around paths, identifiers, CLI flags, shell commands.
- Em dash `—` (U+2014), not ` - `, when joining a label to its explanation.
  Hyphen-minus `-` stays for compound words and CLI flags only.

This rule is about Markdown **formatting** and governs contributor docs only.
It does not reach the human-owned research input (`context/MASTER.md`,
`context/P{0..5}.md` and their `[STABLE]` / `[AGENT-INPUT]` schema), the
free-form prompts under `.claude/`, or any agent output — `scouting/` and its
template follow `scouting/AUTHORING.md`'s own emoji system, `analysis/<id>.md`
and `comparison/<slug>.md` follow their contracts, and the GitHub-KaTeX math
forms live in `analysis/AUTHORING.md` §3-1 because they are an output
convention. Path correctness is **not** exempt: when a path moves, references
inside prompts and context files are updated even though their formatting is
not governed here.

## Document language convention

PROBE is a Korean-first repository — most outputs are decision-grade Korean
prose for an internal team — but the contributor-facing surface stays in
English so `git log`, PR threads and external collaborators read uniformly.
This is the single source of truth for "which language should a new doc be
in?":

- **Default — Korean (한글).** All agent outputs — `analysis/<id>.md`,
  `comparison/<slug>.md` and the `scouting/` reports — are Korean, and so are
  the templates those folders ship (`scouting/templates/`).
- **English — contributor, style and operator docs.** Every `CLAUDE.md`,
  `SETUP.md`, the three `AUTHORING.md` contracts and the folder READMEs. The
  audience is anyone reading PRs or history.
- **English — the project front door.** `README.md`, the GitHub-rendered top
  page and the single onboarding surface for a newcomer.

**No `_KO` / `_EN` filename suffix.** Location plus the H1 on line 1 are
sufficient — `head -1 <file>` tells you the language in one command. If the
rule above does not place a doc unambiguously, the doc is in the wrong folder.

## No change history in code or guides

Code comments, docstrings and guides describe **what the repo is now**. When a
requirement changes, the text that stated the old requirement is rewritten to
state the new one — not annotated with what it used to say. `git log`, the PR
thread and the commit body are where the change lives; a comment that also
carries it goes stale the next time the rule moves, and a reader cannot tell
which half is current.

What this rules out, in a comment, a docstring, a rule in any `AUTHORING.md`,
or a prompt:

- **Past forms** — "X used to be Y", "this was previously a Z", "no longer
  holds", "the earlier trigger did …".
- **Change narration** — "renamed from", "moved out of", "added in the
  restructure", "kept for now".
- **Incident logs** — "three separate bugs came from this". The failure mode is
  worth stating; its history is not. Write it in the present, as the thing that
  happens: "a rule like `.X b{display:block}` catches body emphasis and breaks
  the line".

Rationale is not history and stays. "This is a barrier because stage N needs
every stage N-1 result" explains a live design; "this used to be a pipeline"
explains nothing a reader can act on. Dead code and dead rules are deleted, not
commented out or marked deprecated — the same rule, applied to the code itself.

## When adding a new doc

Probe has no cross-link automation — every doc reference is hand-maintained, so
a new doc that only lands on the filesystem becomes a silent orphan. Walk this
list every time:

- [ ] **Classify it.** Narrative or reference, per "Document Markdown style"
      above, and consistent per header level.
- [ ] **Place it.** A rule binding one folder is that folder's `CLAUDE.md`; an
      output contract is that track's `AUTHORING.md`; a map of what is in a
      folder is its `README.md`; repo-wide contributor, governance and operator
      docs sit at the root next to this file. A doc that fits none of those
      belongs in one of them rewritten, not in a new file.
- [ ] **Add a row to the Repository map above** — one line, pointing at the
      doc for anything longer.
- [ ] **Resolve its paths.** Grep any path the new doc pins against the current
      layout.
- [ ] **Prove it is reachable** — `grep -rn '<new-doc-basename>' .` must return
      at least one inbound link. Zero = orphan.
- [ ] **Run `python3 linters/check-doc-links.py`** — the automated backstop for
      the dangling-path half of this list. It scans this file, every folder
      `CLAUDE.md`, `README.md`, `SETUP.md` and the `context/` files; pass a
      prompt or an `AUTHORING.md` as an explicit arg to scan it too (they are
      off the default set because they carry illustrative example paths).
