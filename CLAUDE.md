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
| `context/MASTER.md` | human | Single source of truth — Identity, Pillars, Decision Log, Tracked Literature (all P1–P5) |
| `context/P{1..4}.md` | human | Per-pillar history-free extracts (identical §1–§9 skeleton) — the pipeline reads one, never the full doc |
| `scouting/` | agent | Weekly Scouting Reports (`P#/YYYY-MM-DD.md`, Mon/Thu, per pillar) |
| `synthesis/` | agent | Monthly per-pillar narrative briefs (`P#_BRIEF.md`) |
| `analysis/` | agent | One subfolder per paper (`<arxiv-id>/`). Each contains: deep-dive analysis (`analysis.md`), Layer 1 Design (`design.md`), foundry-specific impl guides (`impl/<foundry>/impl.{md,patch}` + `test_*.py`), and verification reports (`validation/<foundry>.md`) |
| `analysis/_catalogs/` | agent (hand-curated) | Cross-paper lineage catalogs, separated from per-paper `<arxiv-id>/` deep-dives. `README.md` defines the common column standard (License + commercial marker / Access icon / `hf:`/`gh:`/`web` link prefix / 🤖-👤-🔀 데이터 유형 / 🟢-🟡-🔴-❓ source-check) + the decision-4-field rule for the scan marker; `vlm.md` enumerates open-weight VLM candidates as a flat table, `vla.md` and `lineage_corpus.md` both use the *scan table + per-row `<details>` cards* hybrid (vla 8 H4: Architecture / Training data / Action representation / Inference / Eval / Open-weight / Source check / Sources · lineage_corpus 8 H4: Observations / Actions / Embodiment / Annotation / Scale / Lineage / Source check / Sources). The folder also hosts pillar-level methodology references (e.g. `vlm-prior-preservation.md` — P4 forgetting / carve-out orthogonal planes + θ_VLM path-intervention A~D + 4-stage recipe + forward-KL measurement protocol); methodology docs are not facts-tables but design references and cross-link to the catalog rows. Quarterly rebalance; not in `INDEX.md` auto-regeneration scope |
| `vendor/lerobot/` | external | Read-only pinned `lerobot` snapshot — 6 baseline policies + `rtc` + configs + processor + `datasets/` (standard LeRobotDataset format) + `transforms/` + `utils/`; the v0 foundry (target of every `foundry=lerobot` impl patch). Refresh procedure in its own `README.md` |
| `.codegraph/` | generated | Local CodeGraph knowledge graph over `vendor/lerobot/`. Only `config.json` (scope definition) is committed; the DB is built on demand by `scripts/ensure-codegraph.sh` (see the "CodeGraph" section below) |
| `.foundry-runtime/` | generated | Per-checkout *executable* foundry runtime (full upstream clone at the pinned commit + venv), built on demand by `scripts/ensure-foundry-runtime.sh` so `/validate §🧬` can RUN a foundry's smoke test. Gitignored, multi-GB, never committed (see the "Foundry runtime" section below) |
| `.claude/prompts/**` | human | Externalized, durable agent prompts (the repo's real asset) |
| `.claude/commands/**` | human | Slash-command wrappers |
| `docs/STYLE.md` | human | **Single source of truth for agent output format** (emoji, links, Korean authoring) |
| `scripts/refresh-analysis-index.py` | human | Regenerator for the `analysis/INDEX.md` deep-dive table; invoked post-merge on `main` by `.github/workflows/refresh-analysis-index.yml` (PR-side regeneration was retired to eliminate parallel-PR conflicts on the generated block) |
| `scripts/ensure-codegraph.sh` | human | On-demand builder for the `.codegraph/` index; invoked by `/implement` before its first codegraph call (see the "CodeGraph" section below) |
| `scripts/ensure-foundry-runtime.sh` | human | On-demand builder for the `.foundry-runtime/` execution runtime; invoked by `/validate` (§🧬) and `/implement` (§G) to install a foundry at its pinned commit and run impl smoke tests (see the "Foundry runtime" section below) |
| `scripts/foundry-ablation/` | human | Reusable experiment harness for attributing `/implement` output quality (H_context vs H_verify vs H_null) — controlled a1/a2 prompt generator + an append-only sample ledger with cross-paper aggregation. Spec in its own `PROTOCOL.md` |

`context/` is read-only to the agent — it may *propose* changes in a report,
never edit the source. Edit `MASTER.md`; regenerate the `P#` extracts from it,
never the reverse.

`vendor/lerobot/` is read-only to **both** the agent and contributors. It is
a byte-stable snapshot of upstream `lerobot` at a pinned commit, and the v0
foundry — the target of every `foundry=lerobot` impl patch under
`analysis/<id>/impl/lerobot/impl.patch`. Hand-editing files inside it would
silently invalidate existing patches and break attribution. The only way it
changes is the wholesale refresh procedure in `vendor/lerobot/README.md`;
nothing else.

## CodeGraph

`vendor/lerobot/` is indexed by
[CodeGraph](https://github.com/colbymchenry/codegraph) and exposed to every
session over MCP. The index (`.codegraph/codegraph.db`) is built **on
demand, not at session start** — only the commands that actually read
`vendor/lerobot/` need it (today just `/implement`), so paying the build cost
on every session would be waste. Those commands run
`scripts/ensure-codegraph.sh` before their first codegraph call: it builds
the DB if missing (~3s for the current 108 vendored `.py` files) and is a
no-op when it already exists, after which the file watcher inside the MCP
server keeps it fresh. Only `.codegraph/config.json` (defining
`scope=vendor/lerobot`) is committed; the DB is per-checkout and gitignored.

The build cannot be a plain `codegraph index` — codegraph requires `init`
first, and `init` overwrites `config.json` with a default template whose
exclude list drops `vendor/`. `scripts/ensure-codegraph.sh` backs up the
committed config across `init` and restores it before indexing; run it by
hand from the repo root if you ever need to (re)build outside `/implement`.

For any `/implement` run, or any time you need to ground a Design row in
`file:line` coordinates inside `vendor/lerobot/`, prefer the MCP tools over
reading full `.py` files:

- `codegraph_search <symbol>` / `codegraph_node <id>` — exact spans without
  manual line-counting.
- `codegraph_context <task>` — minimum file:line surface for the change set.
- `codegraph_callers` / `codegraph_callees` — confirm the binding site before
  patching.
- `codegraph_impact` — surface cross-file consumers a patch would break.

If the MCP server is unreachable (sandbox without `npx`, offline clone), fall
back to direct file reads — `/implement` should still complete.

## Foundry runtime

The vendored `vendor/lerobot/` snapshot is a *partial, read-only* copy for
diffing and `file:line` grounding — its `.py` files import from non-vendored
modules, so it cannot be imported or run. To verify that an impl patch is not
just textually applicable but *actually correct*, `/validate` runs the impl's
sibling smoke test against the **whole** upstream package installed at the
pinned commit. `scripts/ensure-foundry-runtime.sh <foundry>` builds that
runtime on demand:

1. Parse the pinned-commit SHA from `vendor/<foundry>/README.md` (the same
   provenance row `/implement` and `/validate` cite — single source of truth).
2. Clone the source repo at that SHA (depth-1) into
   `.foundry-runtime/<foundry>/src`.
3. Create a venv and `pip install -e .[test]` into it. (Plain `pip`, not
   `uv pip install` — lerobot's `pyproject.toml` pins torch to a cu128 index
   via `[tool.uv.sources]` that has a version gap in some environments; pip
   resolves torch from the default index instead.)
4. Touch a `.ready` marker holding the SHA, so re-runs are a no-op.

It prints the venv python path on its last stdout line and exits non-zero
(with a one-line reason on stderr) when the runtime cannot be built — offline,
install failure, unknown foundry. The execution check **degrades gracefully**:
when the runtime is unavailable, `/validate §🧬` records `skipped`, never a
fabricated pass, and the static verdicts (📚/🔍/🧪/📐) still stand. torch is
the dominant one-time cost (a few minutes); after that the marker makes it
free.

The committed surface stays the vendored snapshot only — `.foundry-runtime/`
is per-checkout and gitignored, and nothing under it is ever staged. The impl
patch is authored against `vendor/<foundry>/` paths; `/validate` translates that
prefix to the upstream layout (`vendor/lerobot/` → `src/lerobot/`) when
applying it to the runtime checkout (`git apply -p3 --directory=src/lerobot`).

Adding a new foundry is a one-line `case` arm in the script (its clone URL)
plus a `vendor/<name>/` snapshot with the same `Pinned commit` provenance row;
nothing else in the script changes.

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
   `deps`. Don't invent new types. (The bare `scout:` / `synthesis:` prefixes
   are *generated routine commits*, not human commits — do not imitate them
   when authoring code/doc changes. Their canonical formats are:
   `scout: P{N} report YYYY-MM-DD` and `synthesis: P{N} brief YYYY-MM`.)
3. **`<scope>`** — lowercase, matches a folder or module in the repo:
   `scout`/`scouting`, `synthesis`, `analysis`, `context`, `prompts`,
   `config`, `docs`, `brand`, `CLAUDE.md`. Omit the scope only for repo-wide
   changes.
4. **Description** — lowercase first letter (after the colon), no trailing
   period, ≲ 72 chars including the type/scope prefix. State *what* the commit
   does, not why (the why goes in the body).
5. **Do NOT include `(#NN)` in the local commit subject** — GitHub appends the
   PR number automatically on squash-merge; adding it manually duplicates it.
6. **Write the commit message in English** — subject *and* body. Document
   content (`.md`, prompts, reports) is Korean or English per
   `docs/STYLE.md`, but the commit message itself is always English so
   `git log` stays uniformly grep-able and consistent with this repo's
   history. Do not switch to Korean even when the body explains
   Korean-authored content; describe it in English.

Good (from this repo's history):

```
feat(analysis): add on-demand single-paper deep-dive mode
refactor(scout): per-pillar dated Korean reports
docs: repo-wide consistency overhaul + cited-code reference legend
chore(config): allow Edit/Write under .claude/ without prompting
feat: history-free research context + per-pillar P2–P4 extracts
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

### Audit checklist before committing

- [ ] First word after `<type>(<scope>):` is an imperative verb (not a noun,
      not past tense).
- [ ] Description is lowercase, ≲ 72 chars, no trailing period.
- [ ] No `(#NN)` PR-number suffix in the subject.
- [ ] Subject and body are in English (regardless of the language of the
      files being changed).
- [ ] Body (if any) leads with *why*, wraps at ~72, uses `─` dividers (not
      `-`/`=`) for big commits, and uses em dash `—` for label/explanation
      joins.

## Document Markdown style

Probe docs fall into two families. The rule **codifies the existing
convention** — it does not strip emoji.

### Narrative / onboarding docs

`README.md`, `docs/INTRO.md`. Headers may carry **one leading thematic
emoji**, placed at the start of the header text, after the `#`s and a space
(`# 🛸 …`, `## 📌 …`, `### 🪜 …`). Exactly one emoji, at the start — never at
the end, never inside body text. One H1 per document.

**Internal consistency per level (hard rule).** Each header level used in a
document must be uniformly emoji or uniformly plain — no mixing within the
same level in the same doc. The canonical narrative pattern in this repo is
**emoji at H1 and H2, plain at H3 and below**, used by both `README.md` and
`docs/INTRO.md`. If you add a new H3 to either, it stays plain; outliers
must be brought into line, not left as exceptions.

### Reference / structural docs

`CLAUDE.md`, `docs/STYLE.md`, `scouting/README.md`,
`synthesis/README.md`, `analysis/README.md`. Plain headers, **no emoji**.
Numbered headers (`## N.`, `### N-M.`) are allowed and match the existing
`STYLE.md`. A folder README's H1 is the folder name (`# scouting/`).

### Shared rules (both families)

- One H1 per document.
- Backticks around paths, identifiers, CLI flags, shell commands.
- Em dash `—` (U+2014), not ` - `, when joining a label to its explanation.
- Hyphen-minus `-` stays for compound words and CLI flags only.

### What this rule does NOT govern

This document-style rule is about Markdown **formatting only**. It does **not**
apply to:

- `context/MASTER.md`, `context/P{1..4}.md` — human-owned research input with
  its own `[STABLE]` / `[AGENT-INPUT]` section schema.
- `.claude/prompts/**`, `.claude/commands/**` — agent prompts, free-form.
- Agent-generated output and its templates — `scouting/_TEMPLATE.md`,
  `analysis/_TEMPLATE.md`, dated reports, `*_BRIEF.md`,
  `analysis/<id>/analysis.md`.
  These follow `docs/STYLE.md`'s own emoji system (emoji on `##`/`###`
  headers is *required* there — the opposite of structural docs).

Path correctness is **not** exempt: when a path moves, references inside
prompts and context files are still updated even though their formatting is
not governed here.

## Document language convention

PROBE is a Korean-first repository — most outputs are decision-grade Korean
prose for an internal team — but the contributor-facing surface stays in
English so `git log`, PR threads, and external collaborators read uniformly.
Use this rule as the single source of truth for "which language should a
new doc be in?":

- **Default — Korean (한글).** All agent outputs (`scouting/`, `synthesis/`,
  `analysis/`) and the folder READMEs that describe them
  (`scouting/README.md`, `synthesis/README.md`, `analysis/README.md`) are
  Korean. Templates that those folders ship (`_TEMPLATE*.md`) are Korean
  as well.
- **Exception 1 — Contributor / style docs in English.** `CLAUDE.md`,
  `docs/STYLE.md`. The audience is anyone reading PRs or
  history; English keeps that surface grep-able and consistent with the
  enforced English commit-message rule.
- **Exception 2 — Project front door in English.** `README.md`. The
  GitHub-rendered top page is the public-facing entry, and the
  hand-tuned Korean onboarding lives one click away at
  `docs/INTRO.md` + `docs/probe_guide.html`.
- **Korean onboarding docs stay Korean.** `docs/INTRO.md` is Korean even
  though it sits alongside the English contributor docs — its folder
  location plus the Korean H1 on line 1 are enough to identify it.

**No `_KO` / `_EN` filename suffix.** Location (the folder rule above) plus
the H1 on line 1 are sufficient — `head -1 <file>` tells you the language
in one command. When `docs/` ends up holding both `STYLE.md` (en) and
`INTRO.md` (ko), that mix is intentional and documented here. Do not add a
language suffix to a new document just to disambiguate; if the rule above
does not place the doc unambiguously, the doc is in the wrong folder.

## When adding a new top-level doc

Probe has no cross-link automation — every doc reference is hand-maintained.
A new doc that is only added to the filesystem without updating the index
becomes a silent orphan (the last restructure produced one before this
checklist existed). Walk this list every time:

- [ ] **Classify the doc** — narrative/onboarding (emoji headers allowed) or
      reference/structural (plain headers). Pick one consistently per the
      table above and do not mix levels.
- [ ] **Pick the location** — folder READMEs sit next to what they describe
      (`scouting/README.md`, `synthesis/README.md`, `analysis/README.md`);
      onboarding / formatting guides live under `docs/`; contributor /
      governance docs sit at the repo root next to `CLAUDE.md`.
- [ ] **Add it to `README.md` → "Further Reading" table.** This is the only
      index in the repo. Match the existing row format (`[`path`](path) |
      one-line description`).
- [ ] **If it is a folder README**, confirm the three output-track READMEs
      (`scouting/`, `synthesis/`, `analysis/`) and the new one remain
      structurally symmetric — each opens with `# foldername/`, names its
      file convention, its generator, and what it reads from `context/`.
- [ ] **If it introduces a new top-level path**, add a row to the
      "Repository map" table in this file (`CLAUDE.md`).
- [ ] **If it pins paths that live elsewhere** (templates, prompts, output
      files), grep the new doc against the current layout — every
      referenced path must resolve after the latest restructure.
- [ ] **Run a final `grep -rn '<new-doc-basename>' .`** — at least one
      inbound link (typically Further Reading) must exist. Zero inbound
      links = orphan.

## Automatically-maintained indexes

The "no cross-link automation" rule above has one intentional exception:
the deep-dive table in `analysis/INDEX.md`. Filenames there
are bare arXiv ids (e.g. `2511.00139.md`), so a reader cannot tell
which paper is which without opening the file. Maintaining that
mapping by hand drifts immediately, so it is regenerated by
`scripts/refresh-analysis-index.py`. The script reads each
analysis's 📄 논문 메타 table (the load-bearing rows are documented in
`docs/STYLE.md` §5-7), inspects the filesystem for foundry
artifacts (`<id>/impl/<foundry>/impl.md` vs `UNMAPPABLE.md`), and
rewrites only the block between

```
<!-- ANALYSIS_INDEX:START -->
<!-- ANALYSIS_INDEX:END -->
```

in `analysis/INDEX.md`. Everything outside those markers stays
hand-maintained — the table lives in its own file so the static
`analysis/README.md` narrative does not interleave with the
auto-generated block.

**Where the script runs.** Post-merge on `main` only, via
`.github/workflows/refresh-analysis-index.yml`. The workflow triggers
on pushes to `main` that touch `analysis/**/analysis.md`,
`analysis/**/impl/**`, `analysis/**/validation/**`, or the script
itself, then commits the refreshed `analysis/INDEX.md` back to `main`
as a `chore(analysis): refresh INDEX.md` bot commit. PR branches and
the per-command prompts (`/analyze-paper`, `/implement`, `/validate`)
deliberately do NOT stage `analysis/INDEX.md` and do NOT invoke the
script — the prior PR-side regeneration produced an unresolvable
text conflict on the generated block every time two analysis PRs
landed in parallel. Concentrating regeneration on `main` eliminates
the conflict surface at the cost of a brief stale window between
merge and the bot commit.

Manual edits inside the markers are overwritten on the next workflow
run, so do not put information there that isn't already extractable
from the meta table or the foundry folder contents — extend the
script or the meta-table spec instead. Running the script by hand
from the repo root with `python3 scripts/refresh-analysis-index.py`
is still safe and idempotent for ad-hoc inspection; just do not
commit the result on a feature branch.

## Where to read more

- `README.md` — motivation, repository structure, full Stage 1–3 agent setup.
- `docs/INTRO.md` — Korean onboarding + operations manual.
- `docs/STYLE.md` — the single source of truth for agent **output**
  format (this file governs commits and *contributor* docs, not output).
- `scouting/README.md`, `synthesis/README.md`, `analysis/README.md` — what
  each output track is and how it is produced.
