# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

PROBE is a research-scouting agent for hand-centric dexterous manipulation. A
human owns the static research context; a scheduled Claude routine reads it and
writes decision-grade reports. See `README.md` for the full motivation,
pipeline, and operations guide; this file is the contributor-facing reference
for **commit hygiene and document style** so the repo stays consistent.

## Repository map

| Path | Owner | Role |
|---|---|---|
| `context/MASTER.md` | human | Global anchor — cross-cutting content only: Identity, Purpose, Long-term Context, Hardware, Pillars overview (P0–P5), Venue, Cross-pollination |
| `context/P{0..5}.md` | human | Per-pillar **owners** of the Decision Log, Tracked Literature, Anti-topics, and Curated Lists (identical §1–§6 skeleton). The pipeline reads one `P#.md`. Six pillars P0–P5 (P0 data, P1–P4 architecture core, P5 World Model). Decision allocation: P1 D1–D7, P2 D8–D12, P3 D13–D18, P4 D19–D23, P0 D24–D27, P5 D28–D32. New pillar: copy `context/_TEMPLATE.md` and walk "When adding a new pillar" below |
| `scouting/` | agent | Scouting Reports (`P#/YYYY-MM-DD.md`, per pillar, on a scheduled cadence) |
| `scouting/AUTHORING.md` | human | **Single source of truth for the `scouting/` output format** (emoji, links, Korean authoring) — the sibling of `site/AUTHORING.md`, each contract sitting with the track it governs. The reading-site track is NOT covered: `analysis/<id>.md` is governed by `site/AUTHORING.md`. `scouting/templates/` holds the report skeleton it describes |
| `analysis/` | agent | The site's corpus — one `<arxiv-id>.md` per paper (flat, no per-paper folder), from `/analyze`. A Korean re-telling written from the paper's **arXiv HTML original**, carrying its own metadata in front matter (`analysis_of`, title, authors, pillars, tags, links, summary). Contract: `site/AUTHORING.md` — not `scouting/AUTHORING.md`, which governs `scouting/` only |
| `analysis_legacy/` | frozen | Legacy corpus — one `<arxiv-id>/analysis.md` per paper, in a format nothing else in the repo uses. **Read by nothing** (prompt, site build and every lint skip it) and never regenerated; kept until those papers are re-written under `analysis/`. Its `README.md` is a static index of what the folder holds |
| `.claude/prompts/**` | human | Externalized, durable agent prompts (the repo's real asset) |
| `.claude/commands/**` | human | Slash-command wrappers |
| `SETUP.md` | human | Operator guide for the scheduled scouting routine — RemoteTrigger form, network allowlist, `SEMANTIC_SCHOLAR_API_KEY`, first-run verification. Scouting only; the on-demand commands need no routine setup |
| `site/` | human | **Everything the reading site is made of** — `AUTHORING.md` (the format contract for `analysis/<id>.md`: front matter, body rules R1–R15, render traps, what the build enforces), `build-site.py` + `builder/` (the static-site generator: a landing briefing, a memo hub, plus one page per rewrite), and `requirements.txt`. Nothing but `analysis/` is published and `analysis_legacy/` is not read at all. `site/builder/arxiv.py` (LaTeXML extraction of an arXiv original — body **and appendix** sections, figures including the `<object>`-embedded SVGs, tables; raises `Unavailable` when a paper has no HTML edition, which is `/analyze`'s stop condition) and `site/builder/mdext/probefence.py` (the ` ```probe-* ` fences and their validation) serve the prompt rather than the build. `--check` lints and writes nothing, `--strict` fails on any warning, `--serve` previews locally under the deployed path. Generated HTML is **never committed** — `.github/workflows/deploy-site.yml` builds it fresh (PRs build without deploying). Folder map: `site/README.md` |
| `linters/check-doc-links.py` | human | Linter verifying local path references in `CLAUDE.md` / `README.md` / `SETUP.md` / `context/*.md` resolve; wired into CI by `.github/workflows/check-doc-links.yml`. Automates the "no orphan / no dangling path" step of "When adding a new top-level doc" below |
| `linters/check-decision-refs.py` | human | Linter verifying every `D#` citation in `analysis/` / `scouting/` outputs exists in the per-pillar Decision Log and that explicit `P# / D#` ties match the owning pillar; wired into CI by `.github/workflows/check-decision-refs.yml` |
| `linters/check-commit-style.py` | human | Linter validating commit subjects / PR titles against the "Commit message style" grammar below (type set, casing, length, non-imperative first words, generated-routine formats); the PR-title gate is `.github/workflows/check-commit-style.yml` (squash-merge makes the PR title the landing subject). Local use: `git log --format=%s main..HEAD \| python3 linters/check-commit-style.py -` |

`context/` is read-only to the agent — it may *propose* changes in a report,
never edit the source. Per-pillar content (Decision Log, Tracked Literature,
Anti-topics, Curated Lists) is **owned by
the relevant `P#.md`**; `MASTER.md` is a thin global anchor holding only
cross-cutting content. Edit the `P#.md` for pillar content; edit `MASTER.md`
only for global content.

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
   synonym): `add`, `fix`, `remove`, `drop`, `rename`, `move`, `refactor`,
   `switch`, `migrate`, `restructure`, `clarify`, `re-align`, `unify`,
   `standardize`, `allow`.
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
   (e.g. `Human Universal Grasping` → `HUG`); (3) otherwise omitted — a plain
   descriptive title with neither a colon codename nor a self-defined acronym
   gets no alias, and one is never invented.)
3. **`<scope>`** — lowercase, matches a folder or module in the repo:
   `scout`/`scouting`, `analysis`, `context`,
   `prompts`, `config`, `style`, `docs`, `site`, `CLAUDE.md`. Omit the scope
   only for repo-wide changes.
4. **Description** — lowercase first letter (after the colon), no trailing
   period, ≲ 72 chars including the type/scope prefix. State *what* the commit
   does, not why (the why goes in the body).
5. **Do NOT include `(#NN)` in the local commit subject** — GitHub appends the
   PR number automatically on squash-merge; adding it manually duplicates it.
6. **Write the commit message in English** — subject *and* body — even when
   describing Korean-authored content, so `git log` stays uniformly grep-able.

Good (from this repo's history):

```
feat(analysis): add math-formatting checker + PR auto-fix CI
refactor(scouting): re-shelve reports per pillar (P#/YYYY-MM-DD.md)
docs(style): codify arXiv figure URL + KaTeX math substitution rules
feat(catalogs): add P4 prior-preservation reference + rename lineage corpus
refactor: streamline guide docs — renames, compression, cross-updates
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

## Document Markdown style

Probe docs fall into two families. The rule **codifies the existing
convention** — it does not strip emoji.

### Narrative / onboarding docs

`README.md`. The H1 may carry **one leading thematic emoji**, placed at the
start of the header text after the `#` and a space (`# 🛸 …`). Exactly one
emoji, at the start — never at the end, never inside body text. One H1 per
document.

**Internal consistency per level (hard rule).** Each header level used in a
document must be uniformly emoji or uniformly plain — no mixing within the
same level in the same doc. The canonical narrative pattern in this repo is
**emoji at H1 only, plain at H2 and below**, used by `README.md`. If you add a
new H2/H3, it stays plain; outliers must be brought into line, not left as
exceptions.

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
      reference in `CLAUDE.md` / `README.md` / `SETUP.md` must resolve. This
      lint is wired into CI (`.github/workflows/check-doc-links.yml`) and is
      the automated backstop for the dangling-path half of this checklist.
      (Pass the prompts or the two `AUTHORING.md` files as explicit args to
      scan them too; they are off the default set because they carry
      illustrative example paths.)

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

- `README.md` — motivation, pipeline, agent stack + setup, references.
- `scouting/AUTHORING.md` — the output format for the `scouting/` track (this
  file governs commits and *contributor* docs, not output).
- `site/AUTHORING.md` — the output format for the reading-site track
  (`analysis/<id>.md`); `site/README.md` maps the generator around it.
- `SETUP.md` — deploying the scouting routine (RemoteTrigger form, network
  allowlist, first-run verification); the track itself is described in
  `README.md` → Pipeline.
