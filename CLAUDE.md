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
| `scouting/` | agent | Weekly Scouting Reports (`YYYY-MM-DD-P#.md`, Mon/Thu, per pillar) |
| `synthesis/` | agent | Monthly per-pillar narrative briefs (`P#_BRIEF.md`) |
| `analysis/` | agent | On-demand single-paper deep-dives (`<arxiv-id>.md`), Layer 1 Designs (`<arxiv-id>_design.md`), foundry-specific impl guides (`<arxiv-id>_impl/<foundry>/impl.{md,patch}`), and verification reports (`<arxiv-id>_audit/<foundry>.md`) |
| `vendor/lerobot/` | external | Read-only pinned `lerobot` snapshot — 6 baseline policies + configs + processor; the v0 foundry (target of every `foundry=lerobot` impl patch). Refresh procedure in its own `README.md` |
| `.codegraph/` | generated | Local CodeGraph knowledge graph over `vendor/lerobot/`. Only `config.json` (scope definition) is committed; the DB is built on demand by `scripts/ensure-codegraph.sh` (see the "CodeGraph" section below) |
| `.claude/prompts/**` | human | Externalized, durable agent prompts (the repo's real asset) |
| `.claude/commands/**` | human | Slash-command wrappers |
| `docs/STYLE.md` | human | **Single source of truth for agent output format** (emoji, links, Korean authoring) |
| `scripts/refresh-analysis-index.py` | human | Regenerator for the `analysis/README.md` 📑 Index table; invoked by `/analyze-paper`, `/foundry`, `/audit` |
| `scripts/ensure-codegraph.sh` | human | On-demand builder for the `.codegraph/` index; invoked by `/foundry` before its first codegraph call (see the "CodeGraph" section below) |

`context/` is read-only to the agent — it may *propose* changes in a report,
never edit the source. Edit `MASTER.md`; regenerate the `P#` extracts from it,
never the reverse.

`vendor/lerobot/` is read-only to **both** the agent and contributors. It is
a byte-stable snapshot of upstream `lerobot` at a pinned commit, and the v0
foundry — the target of every `foundry=lerobot` impl patch under
`analysis/<id>_impl/lerobot/impl.patch`. Hand-editing files inside it would
silently invalidate existing patches and break attribution. The only way it
changes is the wholesale refresh procedure in `vendor/lerobot/README.md`;
nothing else.

## CodeGraph

`vendor/lerobot/` is indexed by
[CodeGraph](https://github.com/colbymchenry/codegraph) and exposed to every
session over MCP. The index (`.codegraph/codegraph.db`) is built **on
demand, not at session start** — only the commands that actually read
`vendor/lerobot/` need it (today just `/foundry`), so paying the build cost
on every session would be waste. Those commands run
`scripts/ensure-codegraph.sh` before their first codegraph call: it builds
the DB if missing (~3s for the current 58 vendored `.py` files) and is a
no-op when it already exists, after which the file watcher inside the MCP
server keeps it fresh. Only `.codegraph/config.json` (defining
`scope=vendor/lerobot`) is committed; the DB is per-checkout and gitignored.

The build cannot be a plain `codegraph index` — codegraph requires `init`
first, and `init` overwrites `config.json` with a default template whose
exclude list drops `vendor/`. `scripts/ensure-codegraph.sh` backs up the
committed config across `init` and restores it before indexing; run it by
hand from the repo root if you ever need to (re)build outside `/foundry`.

For any `/foundry` run, or any time you need to ground a Design row in
`file:line` coordinates inside `vendor/lerobot/`, prefer the MCP tools over
reading full `.py` files:

- `codegraph_search <symbol>` / `codegraph_node <id>` — exact spans without
  manual line-counting.
- `codegraph_context <task>` — minimum file:line surface for the change set.
- `codegraph_callers` / `codegraph_callees` — confirm the binding site before
  patching.
- `codegraph_impact` — surface cross-file consumers a patch would break.

If the MCP server is unreachable (sandbox without `npx`, offline clone), fall
back to direct file reads — `/foundry` should still complete.

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
   in older history are *generated routine commits*, not human commits — do not
   imitate them when authoring code/doc changes.)
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
  `analysis/_TEMPLATE.md`, dated reports, `*_BRIEF.md`, `analysis/<id>.md`.
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
the 📑 Index table at the top of `analysis/README.md`. Filenames there
are bare arXiv ids (e.g. `2511.00139.md`), so a reader cannot tell
which paper is which without opening the file. Maintaining that
mapping by hand drifts immediately, so it is regenerated by
`scripts/refresh-analysis-index.py` from the GIT step of
`/analyze-paper`, `/foundry`, and `/audit`. The script reads each
analysis's 📄 논문 메타 table (the load-bearing rows are documented in
`docs/STYLE.md` §5-7), inspects the filesystem for foundry
artifacts (`<id>_impl/<foundry>/impl.md` vs `UNMAPPABLE.md`), and
rewrites only the block between

```
<!-- ANALYSIS_INDEX:START -->
<!-- ANALYSIS_INDEX:END -->
```

in `analysis/README.md`. Everything outside those markers stays
hand-maintained. Manual edits inside the markers are overwritten on
the next slash-command run, so do not put information there that
isn't already extractable from the meta table or the foundry folder
contents — extend the script or the meta-table spec instead. Re-run
the script by hand from the repo root with
`python3 scripts/refresh-analysis-index.py`; it is idempotent.

## Where to read more

- `README.md` — motivation, repository structure, full Stage 1–3 agent setup.
- `docs/INTRO.md` — Korean onboarding + operations manual.
- `docs/STYLE.md` — the single source of truth for agent **output**
  format (this file governs commits and *contributor* docs, not output).
- `scouting/README.md`, `synthesis/README.md`, `analysis/README.md` — what
  each output track is and how it is produced.
