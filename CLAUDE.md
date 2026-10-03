# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

PROBE is a research-scouting agent for dexterous manipulation. A human owns
the research context in `context/`; agent tracks read it and write
decision-grade Korean output — a scheduled scouting routine into `scouting/`,
and on demand `/analyze`, `/compare` and `/present` into `analysis/`,
`comparison/` and `presentation/`. The reading site publishes all four.
`/distinguish` writes only outside the repo and `/ideate` writes nothing.
`README.md` carries the motivation; this file is the contributor reference for
**commit hygiene and document style**.

## Where the rules live

Repo-wide rules — commits, contributor-doc style, the local checks — are in
this file. A rule that binds one folder lives in that folder's own `CLAUDE.md`.
Output format is one contract per track, its `AUTHORING.md`, and is never
restated in a prompt. A folder's `README.md` maps what is in it and states no
rules. The map below names every one of them.

## Repository map

The canonical path index. One line per path; anything longer belongs in the
file the row points at.

| Path | Owner | Role |
|---|---|---|
| `README.md` | human | Project front door — motivation, the pipeline, which track to run for what |
| `context/MASTER.md` | human | Global anchor — cross-cutting content only |
| `context/P{0..4}.md` | human | One per pillar — its Decision Log, Tracked Literature and Anti-topics. A run reads one |
| `context/_TEMPLATE.md` | human | The skeleton a new pillar is copied from — the pillar section spine |
| `context/CLAUDE.md` | human | Rules for `context/` — the read-only boundary, the Decision-Log entry format, adding a pillar |
| `scouting/` | agent | One run per date — a report per pillar, `P#/YYYY-MM-DD.md`, and the run file `runs/YYYY-MM-DD.md`, filling `scouting/templates/` — the site merges a run into one page |
| `scouting/AUTHORING.md` | human | Format contract for scouting reports |
| `scouting/SETUP.md` | human | Operator guide for the scheduled scouting routine |
| `analysis/` | agent | The site's corpus — one `<arxiv-id>.md` per paper from `/analyze`, a Korean rewrite of the arXiv HTML original |
| `analysis/AUTHORING.md` | human | Format contract for `analysis/<id>.md` |
| `comparison/` | agent | One `<slug>.md` per comparison from `/compare` — two or three rewritten papers under one question |
| `comparison/AUTHORING.md` | human | Format contract for `comparison/<slug>.md` |
| `presentation/` | agent | One `<arxiv-id>.md` per talk from `/present` — a rewritten paper as slides with a speaker essay each |
| `presentation/AUTHORING.md` | human | Format contract for `presentation/<arxiv-id>.md` |
| `distinction/AUTHORING.md` | human | Format contract for what `/distinguish` writes into the operator's **private folder**, never into this repo |
| `distinction/SETUP.md` | human | Operator guide for the private folder and the local distinction routine |
| `distinction/templates/` | human | `BASKET.md` and `METHOD.md` skeletons for the private folder |
| `.claude/prompts/**` | human | The agent prompts — one per track. Each owns a **procedure** and delegates every format rule to its track's `AUTHORING.md` |
| `.claude/commands/**` | human | Slash-command wrappers pointing each command at its prompt |
| `assets/` | human | The README images and `build-art.py` |
| `assets/CLAUDE.md` | human | Rules for `assets/` |
| `site/` | human | The reading site's generator. Folder map: `site/README.md` |
| `site/query.py` | human | The agent's standard-library query CLI over a checkout |
| `site/CLAUDE.md` | human | Rules for `site/` — the invariants a build change must not break |
| `site/search/` | human | Semantic search over the rewrites. Folder map: `site/search/README.md` |
| `linters/` | human | One gate per rule set — each script's docstring says what it checks; "Local checks" below says when to run it |
| `.github/workflows/` | human | Every lint on PRs (`check-commit-style` reads the **PR title**, the squash-merge subject), `check-scouting-format` also on `push` to `main`, and `deploy-site.yml` — PR build, Pages deploy, semantic re-index |

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
   `site`, `scouting`, `analysis`, `comparison`, `presentation`, `distinction`,
   `context`, `prompts`, `assets`, `linters`, `ci` (`.github/workflows/`), `config`. A
   track's scope covers its contract and its documents; the build code that
   publishes them is `site`. Omit the scope for repo-wide changes — a docs pass across several
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

The bare `scout:` / `analysis:` / `compare:` / `present:` prefixes belong to the
generating prompts, not to human commits — do not imitate them when authoring code or doc
changes. One canonical format per prompt:

```
scout: report YYYY-MM-DD (P0 P1 P2 P3 P4)   # the pillars whose reports it carries
compare: add <slug>                       # the slug is the question, so no alias
analysis: add <arxiv-id> rewrite (<alias>)
present: add <arxiv-id> talk (<alias>)
```

The distinction track has no prefix: `/distinguish` writes into a private folder
and commits nothing.

`update` replaces `add` when redoing an existing rewrite, comparison or talk. The
trailing `(<alias>)` is the rewrite's own `alias:` front-matter value, whose
resolution ladder `analysis/AUTHORING.md` §1 owns — a paper that resolves to no
alias there carries none here either, and the subject ends at `rewrite`.

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

CI runs each of these on the PR except `build-art.py --check` and the
distinction lint. Run the ones your change touches before pushing.

| Change touches | Command |
|---|---|
| any `CLAUDE.md`, `README.md`, `SETUP.md` or `context/` file | `python3 linters/check-doc-links.py` |
| `analysis/`, `scouting/`, `comparison/`, `context/` | `python3 linters/check-decision-refs.py` |
| `context/`, any `CLAUDE.md`, `README.md` or `SETUP.md` | `python3 linters/check-context-consistency.py` |
| `scouting/` | `python3 linters/check-scouting-format.py` |
| anything (the PR title is the landing subject) | `git log --format=%s main..HEAD \| python3 linters/check-commit-style.py -` |
| `analysis/`, `comparison/`, `presentation/`, `scouting/` or `site/` | `python3 site/build-site.py --check --strict`, then `python3 site/build-site.py --strict --out /tmp/probe-check` — what each sees: `site/CLAUDE.md` |
| `presentation/` | `python3 linters/check-presentation-format.py` |
| the private folder `/distinguish` writes | `python3 linters/check-distinction-format.py` with `PROBE_PRIVATE_DIR` set |
| `site/query.py`, `site/builder/catalog.py` | `python3 -I -S site/query.py catalog >/dev/null` (`-S` proves the standard library suffices) |
| `assets/build-art.py` | `python3 assets/build-art.py --check` |
| `site/search/function/` | `npx esbuild@0.28.2 site/search/function/search.ts --loader:.ts=ts --outfile=/dev/null` |

The site build is the only one with dependencies:
`pip install -r site/requirements.txt`.

## Document Markdown style

**Contributor docs** — every `CLAUDE.md`, the `SETUP.md` guides, the
`AUTHORING.md` contracts and the folder READMEs — are reference docs: plain
headers, **no emoji**, numbered headers (`## N.`, `### N-M.`) allowed. A folder
README's H1 is the folder name (`# site/`).

**`README.md`** is the one narrative doc. It opens on the hero — the
`<picture>` pair `assets/hero.svg` standing where an H1 would, linked to the
reading site, with the project name and its lines in the `alt` — and below it
every section is a `<details>` whose `<summary>` is a bold name, an em dash and
one line.

Both:

- One H1 per document (`README.md` has none — the hero stands there).
- **Each header level is uniformly marked or uniformly plain** — no mixing
  within one level in one doc.
- Backticks around paths, identifiers, CLI flags, shell commands.
- Em dash `—` (U+2014), not ` - `, when joining a label to its explanation.
  Hyphen-minus `-` stays for compound words and CLI flags only.

This governs contributor docs only. The research input in `context/`, the
prompts under `.claude/` and every agent output follow their own schema or
contract. Path correctness is **not** exempt: when a path moves, references in
prompts and context files move with it.

## Document language convention

Agent outputs — `analysis/`, `comparison/`, `presentation/`, `scouting/` and
the templates those folders ship — are **Korean**. Contributor docs and
`README.md` are **English**, so `git log`, PR threads and outside readers read
uniformly. No `_KO` / `_EN` filename suffix: `head -1 <file>` tells the
language.

## No change history in code or guides

Code comments, docstrings, guides, contracts and prompts describe **what the
repo is now**. When a requirement changes, the text that stated it is rewritten
— not annotated with what it used to say; the change lives in `git log`, the PR
and the commit body. That rules out past forms ("X used to be Y", "no longer
holds"), change narration ("renamed from", "kept for now") and incident logs
("three bugs came from this") — state the failure mode in the present instead.

Rationale is not history and stays: "a barrier because stage N needs every
stage N-1 result" explains a live design. Dead code and dead rules are deleted,
not commented out or marked deprecated.

## When adding a new doc

Every doc reference is hand-maintained, so a new doc that only lands on the
filesystem is a silent orphan:

- [ ] **Place it.** A rule binding one folder goes in that folder's
      `CLAUDE.md`; an output contract in its track's `AUTHORING.md`; a folder
      map in its `README.md`; an operator guide in its track's folder. A doc
      that fits none of those belongs in one of them, not in a new file.
- [ ] **Add a row to the Repository map** above.
- [ ] **Prove it is reachable** — `grep -rn '<basename>' .` returns at least
      one inbound link.
- [ ] **Run `python3 linters/check-doc-links.py`** — it resolves the paths in
      every `CLAUDE.md`, `README.md`, `SETUP.md` and `context/` file; pass a
      prompt or an `AUTHORING.md` as an argument to scan it too.
