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
| `context/MASTER.md` | human | Global anchor — cross-cutting content only: Identity, Purpose, Long-term Context, Hardware, Pillars overview (P0–P5), Venue, Cross-pollination. No longer holds per-pillar Decision Log / Tracked Literature |
| `context/P{0..5}.md` | human | Per-pillar **owners** of the Decision Log, Tracked Literature, Anti-topics, and Curated Lists (identical §1–§6 skeleton). The pipeline reads one `P#.md`. Six pillars P0–P5 (P0 data, P1–P4 architecture core, P5 World Model). Decision allocation: P1 D1–D7, P2 D8–D12, P3 D13–D18, P4 D19–D23, P0 D24–D27, P5 D28–D32 |
| `scouting/` | agent | Scouting Reports (`P#/YYYY-MM-DD.md`, per pillar, on a scheduled cadence) |
| `analysis/` | agent | One subfolder per paper (`<arxiv-id>/`); the auto-generated deep-dive **index** now lives at `catalogs/analyses.md` (slash-command invocation + rules live in the root `README.md` → Pipeline). Per-paper schema, filled as artifacts are produced: deep-dive analysis (`analysis.md`), Layer 1 Design (`design.md`), foundry-specific impl guides (`impl/<foundry>/impl.{md,patch}` + `test_*.py`), and verification reports (`validation/<foundry>.md`), plus an optional paper↔code audit (`audit.md`, from `/audit-paper` — a reproducibility gate checking the paper against its *own* official repo, distinct from `/validate-impl`'s Design↔foundry audit). Most folders today hold only `analysis.md` + `design.md`. A paper that proposes no foundry-portable method (pure dataset / benchmark / survey / tooling) is **Design 비대상**: its `analysis.md` 📄 메타 carries a `Design 적용 | 🚫 비대상 (<사유>)` row and its `design.md` is a two-block stub (📄 메타 + 🚫 Design 비대상), not the 9-section Layer 1 form — `/implement-design` short-circuits it to `UNMAPPABLE.md` (rule in `.claude/prompts/analysis.md` DESIGN APPLICABILITY gate + `docs/STYLE.md` §6) |
| `hypotheses/` | agent | Output of the `/hypothesize` synthesis track — one `<slug>/` per run holding `hypotheses.md` (ranked, `D#`-anchored, falsifiable hypotheses + a 합의·불일치 매트릭스) + `hypotheses.provenance.md` (corpus accounting + tension→hypothesis lineage + per-hypothesis verification state). Read-only synthesis over the accumulated `analysis/` DB; ships every hypothesis labeled `inferred`/`unverified` (no experiment is run — the empirical rung is human). `--compare-only` runs emit just `compare.md`. See `docs/new-capabilities.md` |
| `catalogs/` | agent (hand-curated) | Cross-paper reference material — a top-level sibling of `analysis/`, separated from per-paper `<arxiv-id>/` deep-dives. Four files, **no H1** in any of them. The three **hand-curated** files (`models.md` / `datasets.md` / `benchmarks.md`) open directly on the first emoji `##` section header — no top badge; `analyses.md` is the **auto-generated** deep-dive index (one plain `## P#` table per primary Pillar, body between `<!-- ANALYSIS_INDEX -->` markers — see "Automatically-maintained indexes"). `models.md` is an awesome-list-style curation of VLA and open-weight VLM entries — one bullet per entry (name + paper title + arXiv badge + GitHub/HF badge), grouped under emoji `##` section headers (🤖 VLA / 🌐 WAM / 🧠 Open-weight VLM) into **lineage `###` series subsections** (e.g. `### π (Physical Intelligence)`, `### Being-H`, `### Qwen-VL`; non-lineage entries under `### Standalone`), reverse-chronological within each series. A leading `📝` badge is *auto-injected* at the **front** of any bullet whose arXiv id has an `analysis/<id>/` folder by arXiv-id matching (see "Automatically-maintained indexes"). A paper also opts a **bullet** in via its analysis `카탈로그` (`models/group/series/handle`) meta: the script inserts a skeleton bullet once at the top of that `### series` subsection (`group` = `vla`/`vlm`/`wam`; `series` = an existing `###` lineage), never re-adding a listed arXiv id — the lineage grouping and ordering stay hand-owned thereafter. `datasets.md` (VLA further-pretrain datasets) and `benchmarks.md` (P0 D26 output — VLA eval harnesses / simulators / dexterous benchmarks) are **hand-curated rich tables**: `datasets.md` columns `# / Dataset / Links / Source / Facts / Embodiment / License / Refreshed / Analysis` (sections 🤖 Robot Action / 👤 Human Video / 🔀 Mixed); `benchmarks.md` columns `# / Benchmark / Links / Source / Details / Type / License / Refreshed / Analysis` (sections 🧪 Eval Harness / 🎮 Simulator / ✋ Dexterous). The per-row `Refreshed` cell carries the date each row was last hand-curated (so there is no file-level `Updated` badge). A paper opts a row in via its analysis `카탈로그` (`target/section/handle`) meta: the script **creates the skeleton row once** (Links / Refreshed / `📝` Analysis auto-filled, the rich Source/Facts/… columns seeded `❓`) and never overwrites it again — a human backfills the `❓` cells. Quarterly rebalance; the only script-maintained surface is entry *creation* (skeleton row / bullet) + the `Analysis` column + the `models.md` leading badge — every rich cell once filled, per-row `Refreshed`, entry curation, and lineage grouping are hand-owned |
| `vendor/lerobot/` | external | Read-only pinned `lerobot` snapshot — 7 baseline policies (incl. `vla_jepa`) + `rtc` + configs + processor + `datasets/` (standard LeRobotDataset format) + `transforms/` + `utils/`; the v0 foundry (target of every `foundry=lerobot` impl patch). Refresh procedure in its own `README.md` |
| `.codegraph/` | generated | Local CodeGraph knowledge graph over `vendor/lerobot/`. Only `config.json` (scope definition) + `.gitignore` are committed; the DB is built on demand by `scripts/ensure-codegraph.sh` (see the "CodeGraph" section below) |
| `.foundry-runtime/` | generated | Per-checkout *executable* foundry runtime (full upstream clone at the pinned commit + venv), built on demand by `scripts/ensure-foundry-runtime.sh` so `/validate-impl §🧬` can RUN a foundry's smoke test. Gitignored, multi-GB, never committed (see the "Foundry runtime" section below) |
| `.claude/prompts/**` | human | Externalized, durable agent prompts (the repo's real asset) |
| `.claude/commands/**` | human | Slash-command wrappers |
| `docs/STYLE.md` | human | **Single source of truth for agent output format** (emoji, links, Korean authoring) |
| `docs/new-capabilities.md` | human | Korean reader-facing overview of the research capabilities added on top of scouting + analysis: the `/hypothesize` synthesis track (`hypotheses/`), the `/audit-paper` reproducibility gate (`analysis/<id>/audit.md`), and the strengthened scouting scoring axes (Reproducibility + Methodology). Orientation doc, not a format spec |
| `scripts/refresh-analysis-index.py` | human | Regenerator for the `catalogs/analyses.md` deep-dive index (one table per primary Pillar); also maintains the catalog-side cross-link marks (`📝` leading badge in `catalogs/models.md` by arXiv-id matching + `카탈로그`-routed skeleton creation: a bullet in `models.md`, a row in `datasets.md` / `benchmarks.md` with the `Analysis` column). The cross-link is one-directional (catalog → deep-dive); the index `Links` cell carries no reverse `catalog` badge. Invoked post-merge on `main` by `.github/workflows/refresh-analysis-index.yml` (PR-side regeneration was retired to eliminate parallel-PR conflicts on the generated block) |
| `scripts/check-analysis-math.py` | human | Linter/auto-fixer enforcing the GitHub-KaTeX math-formatting rules in `docs/STYLE.md` §5-6 across `analysis/<id>/{analysis,design}.md` + `impl/<foundry>/impl.md`; also wired into CI |
| `scripts/ensure-codegraph.sh` | human | On-demand builder for the `.codegraph/` index; invoked by `/implement-design` before its first codegraph call (see the "CodeGraph" section below) |
| `scripts/ensure-foundry-runtime.sh` | human | On-demand builder for the `.foundry-runtime/` execution runtime; invoked by `/validate-impl` (§🧬) and `/implement-design` (§G) to install a foundry at its pinned commit and run impl smoke tests (see the "Foundry runtime" section below) |
| `scripts/check-doc-links.py` | human | Linter verifying local path references in `CLAUDE.md` / `README.md` resolve; wired into CI by `.github/workflows/check-doc-links.yml`. Automates the "no orphan / no dangling path" step of "When adding a new top-level doc" below |

`context/` is read-only to the agent — it may *propose* changes in a report,
never edit the source. Per-pillar content (Decision Log, Tracked Literature,
Anti-topics, Curated Lists) is **owned by
the relevant `P#.md`**; `MASTER.md` is a thin global anchor holding only
cross-cutting content. Edit the `P#.md` for pillar content; edit `MASTER.md`
only for global content. (The earlier "MASTER is SSOT, regenerate the extracts
from it" model no longer holds.)

`vendor/lerobot/` is read-only to **both** the agent and contributors. It is
a byte-stable snapshot of upstream `lerobot` at a pinned commit, and the v0
foundry — the target of every `foundry=lerobot` impl patch under
`analysis/<id>/impl/lerobot/impl.patch`. Hand-editing files inside it would
silently invalidate existing patches and break attribution. The only way it
changes is the wholesale refresh procedure in `vendor/lerobot/README.md`;
nothing else.

## CodeGraph

`vendor/lerobot/` is indexed by
[CodeGraph](https://github.com/colbymchenry/codegraph) over MCP. The index
(`.codegraph/codegraph.db`) is built **on demand, not at session start** —
only commands that read `vendor/lerobot/` (today `/implement-design`) need it.
They run `scripts/ensure-codegraph.sh` before their first codegraph call:
builds the DB if missing (~3s for 120 `.py` files), no-op otherwise, then the
MCP file watcher keeps it fresh. Only `.codegraph/config.json`
(`scope=vendor/lerobot`) is committed; the DB is per-checkout and gitignored.

- **Gotcha** — the build cannot be a plain `codegraph index`: `init` is required first and overwrites `config.json` with a default that drops `vendor/`. The script backs up and restores the committed config across `init`. Run it by hand to (re)build outside `/implement-design`.
- **Prefer MCP tools over reading full `.py` files** when grounding a Design row in `file:line` — `codegraph_search`/`codegraph_node` (exact spans), `codegraph_context` (min surface for a change), `codegraph_callers`/`codegraph_callees` (binding site), `codegraph_impact` (cross-file consumers).
- MCP server unreachable (no `npx`, offline)? Fall back to direct reads — `/implement-design` still completes.

## Foundry runtime

The vendored `vendor/lerobot/` snapshot is *partial, read-only* (its `.py`
files import non-vendored modules, so it cannot run). To check an impl patch is
not just textually applicable but *correct*, `/validate-impl` runs the impl's
sibling smoke test against the **whole** upstream package at the pinned commit.
`scripts/ensure-foundry-runtime.sh <foundry>` builds that runtime on demand:

1. Parse the pinned-commit SHA from `vendor/<foundry>/README.md` (the same provenance row `/implement-design` and `/validate-impl` cite).
2. Clone the source at that SHA (depth-1) into `.foundry-runtime/<foundry>/src`.
3. venv + `pip install -e .[test]` — plain `pip`, not `uv pip install` (lerobot's `pyproject.toml` pins torch to a cu128 index with a version gap in some environments; pip resolves from the default index).
4. Touch a `.ready` marker holding the SHA so re-runs are a no-op.

- Prints the venv python on its last stdout line; exits non-zero (reason on stderr) when it can't build — offline, install failure, unknown foundry.
- **Degrades gracefully** — runtime unavailable → `/validate-impl §🧬` records `skipped`, never a fabricated pass; static verdicts (📚/🔍/🧪/📐) still stand. torch is the one-time cost; the marker makes re-runs free.
- Committed surface stays the vendored snapshot only — `.foundry-runtime/` is gitignored, never staged. The patch is authored against `vendor/<foundry>/` paths; `/validate-impl` translates the prefix to the upstream layout (`git apply -p3 --directory=src/lerobot`).
- Adding a foundry = one `case` arm (clone URL) + a `vendor/<name>/` snapshot with the same `Pinned commit` row; nothing else changes.

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
   `deps`. Don't invent new types. (The bare `scout:` / `analysis:` prefixes
   are *generated routine commits*, not human commits — do not imitate them when
   authoring code/doc changes. Their canonical formats are:
   `scout: P{N} report YYYY-MM-DD` and `analysis: add <arxiv-id> deep-dive + design`
   for a first-time analysis (`update` instead of `add` when re-running
   `/analyze-paper` on an `<arxiv-id>` that already had a folder).)
3. **`<scope>`** — lowercase, matches a folder or module in the repo:
   `scout`/`scouting`, `analysis`, `catalogs`, `context`,
   `prompts`, `config`, `style`, `docs`, `brand`, `CLAUDE.md`. Omit the scope
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

`CLAUDE.md`, `docs/STYLE.md`. Plain headers, **no emoji**.
Numbered headers (`## N.`, `### N-M.`) are allowed and match the existing
`STYLE.md`. A folder README's H1 is the folder name (e.g. `# vendor/lerobot/`).

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
- Agent-generated output and its templates — `scouting/templates/report.md`,
  `analysis/templates/*.md`, dated reports, `analysis/<id>/analysis.md`.
  These follow `docs/STYLE.md`'s own emoji system (one emoji on each `##`
  header, `###` and below plain) plus its Korean / math conventions.
- **Math / formula rendering** — the GitHub-KaTeX `$`-wrapping and substitution
  rules are an *output* convention, not a contributor-doc one, so they live in
  `docs/STYLE.md` §5-6 (enforced by `scripts/check-analysis-math.py`), not here.

Path correctness is **not** exempt: when a path moves, references inside
prompts and context files are still updated even though their formatting is
not governed here.

## Document language convention

PROBE is a Korean-first repository — most outputs are decision-grade Korean
prose for an internal team — but the contributor-facing surface stays in
English so `git log`, PR threads, and external collaborators read uniformly.
Use this rule as the single source of truth for "which language should a
new doc be in?":

- **Default — Korean (한글).** All agent outputs (`scouting/`, `analysis/`)
  and the deep-dive index (`catalogs/analyses.md`) are Korean. Templates that
  those folders ship (`analysis/templates/`, `scouting/templates/`) are Korean
  as well.
- **Exception 1 — Contributor / style docs in English.** `CLAUDE.md`,
  `docs/STYLE.md`. The audience is anyone reading PRs or
  history; English keeps that surface grep-able and consistent with the
  enforced English commit-message rule.
- **Exception 2 — Project front door in English.** `README.md`. The
  GitHub-rendered top page is the public-facing entry, and the
  hand-tuned Korean onboarding lives one click away at
  `docs/probe_guide.html`.
- **Exception 3 — Catalog tables in English.** `catalogs/datasets.md`
  + `catalogs/benchmarks.md`. Every cell (headers, source, facts,
  embodiment, license, lineage/use) is authored in English so the tables stay
  uniform and grep-able; they carry no H1 and no top badge — they open
  directly on the first emoji `##` section header. (`models.md` keeps its
  awesome-list bullet form.)

**No `_KO` / `_EN` filename suffix.** Location (the folder rule above) plus
the H1 on line 1 are sufficient — `head -1 <file>` tells you the language
in one command. Do not add a language suffix to a new document just to
disambiguate; if the rule above does not place the doc unambiguously, the
doc is in the wrong folder.

## When adding a new top-level doc

Probe has no cross-link automation — every doc reference is hand-maintained.
A new doc that is only added to the filesystem without updating the index
becomes a silent orphan (the last restructure produced one before this
checklist existed). Walk this list every time:

- [ ] **Classify the doc** — narrative/onboarding (H1 emoji allowed) or
      reference/structural (plain headers). Pick one consistently per the
      table above and do not mix levels.
- [ ] **Pick the location** — the deep-dive index is `catalogs/analyses.md`;
      onboarding / formatting guides live under `docs/`; contributor /
      governance docs sit at the repo root next to `CLAUDE.md`.
- [ ] **Add a row to the "Repository map" table in this file (`CLAUDE.md`).**
      That table is the canonical path index; the root `README.md` links only
      the headline docs in prose, so wire a new doc in here.
- [ ] **If it pins paths that live elsewhere** (templates, prompts, output
      files), grep the new doc against the current layout — every
      referenced path must resolve after the latest restructure.
- [ ] **Run a final `grep -rn '<new-doc-basename>' .`** — at least one
      inbound link must exist. Zero inbound links = orphan.
- [ ] **Run `python3 scripts/check-doc-links.py`** — every local path
      reference in `CLAUDE.md` / `README.md` must resolve. This lint is wired
      into CI (`.github/workflows/check-doc-links.yml`) and is the automated
      backstop for the dangling-path half of this checklist. (Pass the prompts
      or `docs/STYLE.md` as explicit args to scan them too; they are off the
      default set because they carry illustrative example paths.)

## Automatically-maintained indexes

One intentional exception to "no cross-link automation": the deep-dive index
in `catalogs/analyses.md`. The rows there key off bare arXiv ids (`2511.00139`),
so the title-to-id mapping drifts if hand-maintained —
`scripts/refresh-analysis-index.py` regenerates it. The script reads each
analysis's `논문 메타` table (load-bearing rows in `docs/STYLE.md` §5-7 —
including the `관련 Pillar` classification row) plus up to 5 English
`기술 키워드` bullet heads (math-bearing/non-English heads excluded, rendered
as single-color 노란 shields.io badges — same badge style for the `arXiv` cell),
inspects the filesystem for the vendor-neutral `impl` column (lerobot-pathed:
`impl.md` vs `UNMAPPABLE.md`), and rewrites the block between
`<!-- ANALYSIS_INDEX:START -->` / `<!-- ANALYSIS_INDEX:END -->` as one table
**per primary Pillar** (P0…P5/미분류; primary = first
`관련 Pillar` entry — the index taxonomy covers the six pillars P0–P5; a `P#`
outside that range is dropped at generation).
Everything outside the markers stays hand-maintained — the short folder intro above the index block.

The same script also maintains the **catalog cross-links** between `catalogs/`
and the index, never the curation (full spec in `docs/STYLE.md` §5-7). The link
is one-directional (catalog → deep-dive); the index `Links` cell carries no
reverse badge back:

1. **`models.md`.** *(a)* A bullet whose arXiv id has an
   `analysis/<id>/` folder gets a `📝` badge spliced in at the **front** of the
   bullet (idempotent strip-then-readd, so a deleted folder drops the badge).
   *(b)* A `models/group/series/handle` `카탈로그` token inserts a skeleton bullet
   once at the top of its `### series` subsection; an already-listed arXiv id is
   never re-added, and a missing `### series` is warned and skipped.
2. **`datasets.md` / `benchmarks.md` (`카탈로그` routing).** A paper's
   `카탈로그` (`target/section/handle`) meta opts it into a section's table: the
   script appends a **skeleton row once** (Links / Refreshed / `📝` Analysis
   auto-filled, the rich columns seeded `❓`) and renumbers `#`. A row that
   already carries the paper's arXiv id is never overwritten — only its trailing
   `Analysis` cell is kept fresh (`📝` / `—`).

Only these script-owned marks are automated — adding/removing catalog entries
(the curation judgement), every rich `datasets.md` / `benchmarks.md` cell once a
human fills its `❓`, each row's `Refreshed` date, and the `models.md` lineage
`###` grouping stay hand-owned, so the script never conflates "human curated"
with "cross-link refreshed".

- **Where it runs** — post-merge on `main` only, via `.github/workflows/refresh-analysis-index.yml` (triggers on pushes touching `analysis/**/analysis.md|impl/**|validation/**`, `catalogs/*.md`, or the script), committing the refresh as a `chore(analysis): refresh index + catalog cross-links` bot commit (stages `catalogs/analyses.md` + `catalogs/models.md` + `catalogs/datasets.md` + `catalogs/benchmarks.md`). PR branches and the per-command prompts (`/analyze-paper`, `/implement-design`, `/validate-impl`) do NOT stage these files or invoke the script — PR-side regeneration produced an unresolvable conflict on the generated block whenever two analysis PRs landed in parallel; concentrating it on `main` removes that, at the cost of a brief stale window.
- **Don't hand-edit the script-owned marks** — the `ANALYSIS_INDEX` block in `catalogs/analyses.md` (between markers) and the catalog `Analysis` column / `models.md` leading badge are overwritten on the next run. Everything else in the catalogs is yours. Running it by hand (`python3 scripts/refresh-analysis-index.py`) is safe and idempotent for inspection — just don't commit the result on a feature branch.

## Where to read more

- `README.md` — motivation, pipeline, agent stack + setup, references.
- `docs/probe_guide.html` — Korean onboarding + operations manual.
- `docs/STYLE.md` — the single source of truth for agent **output**
  format (this file governs commits and *contributor* docs, not output).
- `catalogs/analyses.md` — the auto-generated deep-dive index. The scouting
  track is described in `README.md` → Pipeline and `docs/AGENT_SETUP.md`.
- `docs/new-capabilities.md` — Korean overview of the added research
  capabilities: the `/hypothesize` synthesis track, the `/audit-paper`
  reproducibility gate, and the strengthened scouting scoring axes.
