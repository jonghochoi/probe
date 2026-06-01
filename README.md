<div align="center">

# 🛸 PROBE · Research Scout for Dexterous Manipulation

<img src="docs/LOGO.png" alt="NEXUS Logo" width="600">

**Stop drowning in arXiv. Start changing what you train next week.**

*Author watch · Citation-graph expansion · Anti-topic filtering · Weekly decision-grade Scouting Reports*

---

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)](https://python.org)
[![Claude](https://img.shields.io/badge/Claude-Agent-D97757?logo=anthropic&logoColor=white)](https://claude.com/claude-code)
[![arXiv API](https://img.shields.io/badge/arXiv-API-B31B1B?logo=arxiv&logoColor=white)](https://info.arxiv.org/help/api/index.html)
[![Semantic Scholar](https://img.shields.io/badge/Semantic%20Scholar-Graph%20API-1857B6)](https://api.semanticscholar.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

📖 팀 온보딩 한글 문서: [`docs/probe_guide.html`](docs/probe_guide.html)

</div>

---

> ### 📖 New here? Start with the onboarding guide.
>
> **한글 시각 가이드 (Korean visual onboarding):** [`docs/probe_guide.html`](docs/probe_guide.html)
> — download and open in a browser for a full visual walkthrough of PROBE.
>
> ```bash
> git clone https://github.com/jonghochoi/probe.git
> open probe/docs/probe_guide.html         # macOS
> # xdg-open probe/docs/probe_guide.html   # Linux
> ```
>
> 동기·파이프라인·운영 노하우·월간 리뷰 KPI 까지 같은 가이드 한 곳에 담겨 있다.

---

## 📌 Why PROBE?

Running dexterous manipulation research is a full-time job. You tune reward curves, debug tactile pipelines, chase Sim-to-Real gaps — and somewhere between the hardware and the gradient logs, arXiv slips off the map.

The field does not wait. **50–100 new papers land on `cs.RO` + `cs.LG` every day.** Of those, maybe 3–5 per week actually touch hand-centric dexterous manipulation plus Sim-to-Real. That's a 3–5% signal rate in a firehose, and the cost of missing the right paper is re-solving a problem someone already published — the most expensive mistake a researcher can make.

**PROBE finds those 3–5 for you — and won't let them die in your downloads folder.**

But it does not stop at "here are some interesting papers." It asks the only question that matters:

> *"If this paper is right, what do I change in my training/evaluation pipeline next week?"*

Summaries are cheap. PROBE produces **decision material** across three tracks — outward (find), inward (compress), focused (reproduce).

| Without PROBE | With PROBE |
|---|---|
| "I'll check arXiv this weekend" → never happens | Weekly Scouting Report lands in your repo (Mon/Thu, per pillar) |
| 50–100 papers/day → skim titles, remember none | 3–5 papers/week → scored, tied to your open questions |
| Survey mode: "this is interesting" | Decision mode: "change DR range on object mass to [0.5, 2.0] kg" |
| Re-discovering already-published solutions | Citation graph surfaces the prior art before you waste the week |
| Echo chamber — same authors, same methods | Monthly cross-pollination picks from adjacent fields |
| Pinned papers blur into noise over six weeks | Monthly Synthesis Brief keeps the per-pillar architecture in your head |
| "I'll read that paper properly later" → never does | `/analyze-paper` produces a Korean deep-dive **and a vendor-agnostic Layer 1 Design** anchored to your Decision Log |
| "Great paper, but I'll never actually reproduce it" | `/reproduce-paper` takes the Design, drives `/implement-design` → `/validate-impl` in a converging loop, and ships a unified-diff patch against a target foundry (default `lerobot`) |

---

## 🧭 The Pipeline

PROBE has **three output tracks** sharing one static context — outward (`scouting/`), inward (`synthesis/`), focused (`analysis/`). Each answers a different question, runs on a different cadence, and writes to its own folder; together they keep the research log honest.

> **Pillars**: P1 Heterogeneous Body/Hand Action Expert · P2 Structured Input-Modality Binding · P3 Hand-level System0 · P4 VLM Pretraining Preservation · P5 Task Definition & Falsifiable Evaluation — canonical definitions in [`context/MASTER.md`](context/MASTER.md) §5.
>
> **Full doc vs. per-pillar extract**: `context/MASTER.md` is the single source of truth (all five pillars, D1–D26). Each `context/P#.md` is a narrowed, history-free extract of one pillar with an identical §1–§9 skeleton; the cloud scouting/synthesis routines read **one extract** to keep agent context lean and pillar-focused. Edit the full doc; regenerate extracts from it — never the reverse.

```
   ┌───────────────────────────────────────────────────────────────────┐
   │ context/  (static · human-owned · read-only every run)            │
   │                                                                   │
   │ MASTER.md   · Identity / Pillars (P1–P5) / Decision Log (D1–D26)  │
   │             · Tracked Literature (5 × 8) / Researchers /          │
   │               Competitor Monitoring / Anti-topics                 │
   │ P{1..4}.md  · per-pillar history-free extracts (§1–§9 skeleton)   │
   └─────────────────────────────────┬─────────────────────────────────┘
                                     │ read-only (every run)
                                     ▼
   ┌───────────────────────────────────────────────────────────────────┐
   │                             P R O B E                             │
   └───────────┬─────────────────────┬──────────────────────┬──────────┘
               │                     │                      │
               ▼                     ▼                      ▼
   ┌─────────────────────┐ ┌────────────────────┐ ┌────────────────────┐
   │   OUTWARD           │ │   INWARD           │ │   FOCUSED          │
   │   Weekly Scouting   │ │   Monthly Synth.   │ │   On-demand Anal.  │
   │                     │ │                    │ │                    │
   │   Mon/Thu · per P#  │ │   monthly · per P# │ │   /analyze-paper   │
   │                     │ │                    │ │                    │
   │ · Author Watch      │ │ · compress the     │ │ · one paper —      │
   │ · Citation-Graph    │ │   pinned set       │ │   full-text first  │
   │ · Keyword Sweep     │ │ · connect dots:    │ │ · neutral summary  │
   │ · Competitor watch  │ │   D# ↔ §6 pins     │ │   + decision-      │
   │                     │ │                    │ │   grade implic.    │
   │ in: P#.md +         │ │ in: P#.md §4 + §6  │ │ in: MASTER.md      │
   │     last ~2 wk      │ │     (D# + pins)    │ │     + paper body   │
   │                     │ │                    │ │                    │
   │ curl: arXiv + S2    │ │ no retrieval —     │ │ curl: arxiv/html   │
   │                     │ │ static compress    │ │ → ar5iv → abstract │
   └──────────┬──────────┘ └─────────┬──────────┘ └─────────┬──────────┘
              │ writes new           │ overwrites           │ overwrites
              ▼                      ▼                      ▼
   ┌─────────────────────┐ ┌────────────────────┐ ┌────────────────────┐
   │ scouting/           │ │ synthesis/         │ │ analysis/          │
   │ P#/YYYY-MM-DD.md    │ │ P{1..4}_BRIEF.md   │ │ <id>/analysis.md   │
   │                     │ │                    │ │                    │
   │ 3–5 papers, scored, │ │ living per-pillar  │ │ single Korean      │
   │ decision-grade KO   │ │ narrative brief    │ │ deep-dive doc      │
   └──────────┬──────────┘ └─────────┬──────────┘ └─────────┬──────────┘
              │                      │                      │
              └──────────────────────┼──────────────────────┘
                                     │ informs
                                     ▼
                    ┌─────────────────────────────────┐
                    │             Human               │
                    │                                 │
                    │  · Read, judge, discard         │
                    │  · Update context (monthly)     │
                    │  · Log feedback   (monthly)     │
                    └─────────────────────────────────┘
```

### Sidebar: analysis convergence loop

The FOCUSED column drills deeper than the main diagram shows. A
single `/analyze-paper` call produces the *analysis* and a *Layer 1
Design*; the Design is then mapped onto a target *foundry* by
`/implement-design`, and the resulting impl is statically validated by
`/validate-impl`. The validation's §🔎 section sorts every open 🚧 item into four
buckets, and the next-action choice is deterministic from the verdict
cells plus those buckets — so `/reproduce-paper` orchestrates the whole
thing as an **iterative loop with two nested cycles**:

```
   Initial pass (round 0):

       /analyze-paper ──► design ──► /implement-design ──► impl ──► /validate-impl ──► verdict + §🔎 buckets


   Branch on verdict + §🔎 buckets (round 1..N):

       ⚖️ pass ∧ no paper-extractable     ──►  done (success)

       🔍 / 🧪 / 📐 fail/partial          ──►  inner loop
       §🔎 vendor-resolved                      /implement-design --feedback <validation-path>
       §🔎 paper-silent-defaultable             Design fixed; surgical patch update
                                                (vendor-lift / default+NOTE promote)

       📚 fail/partial                    ──►  outer loop
       §🔎 paper-extractable §X.Y               /analyze-paper --focus "<§X.Y,...>"
                                                Design re-extracted, then re-foundry

       §🔎 paper-silent-experimental only ──►  stable_partial (honest defer)
       focused re-extract byte-identical  ──►  stable_design (fixed point)
```

- **§🔎 §🚧 bucket classifier.** Every round, `/validate-impl` re-classifies
  each open 🚧 item zero-state into `vendor-resolved` /
  `paper-extractable §X.Y` / `paper-silent-defaultable` /
  `paper-silent-experimental`, and emits a machine-readable
  `<!-- ANALYSIS_BUCKETS -->` footer (including a `focus-hint:` line).
  This footer is the single source of truth the orchestrator parses to
  pick its next action.
- **Inner loop.** The Design is a vendor-agnostic single source of
  truth, so impl-side gaps are filled without touching it:
  🔍 patch-apply failures, 🧪 signature/constant mismatches,
  📐 silent-skip rows, plus `vendor-resolved` (lift the cited vendor
  `file:line`) and `paper-silent-defaultable` (promote a default with a
  mandatory `# NOTE:` comment) buckets. `/implement-design --feedback
  <validation-path>` treats the prior round's `impl.md` + `impl.patch` as a
  starting point; passing hunks are preserved and every new hunk traces
  1-to-1 to a specific validation row (the honesty guard).
- **Outer loop.** A 📚 `fail`/`partial` — or any `paper-extractable`
  bucket — means the Design is shallower than the paper body.
  `/reproduce-paper` runs `/analyze-paper --focus "<focus-hint>"` to
  re-extract just the named sections (everything else copied verbatim),
  then re-runs `/implement-design` (full regenerate, since the Design moved) and
  `/validate-impl` in the same round. Layer-1 has a large blast radius, but the
  loop is bounded by fixed-point detection rather than a manual gate.
- **Honest termination (fixed-point, no extra counter).** When the
  verdict tuple + 🪛/🚧 tables + §🔎 bucket set repeat byte-for-byte,
  `/reproduce-paper` exits `stable_partial` — only
  `paper-silent-experimental` items remain as permanent 🚧. When a
  focused re-extraction leaves the Design byte-identical, it exits
  `stable_design`. Together these guard against inner↔outer ping-pong.
  The last validation report is the closure note; nothing else is appended.

The full branch matrix and termination conditions are specified in
[`.claude/prompts/reproduction.md`](.claude/prompts/reproduction.md) and
[`.claude/prompts/implementation.md`](.claude/prompts/implementation.md) §F (Update
mode).

### Core principle: static vs. dynamic, never mixed

The split between `context/` (static) and the output tracks (dynamic) exists for one reason: to keep the agent's context lean.

- **Static** (`context/`) changes monthly at most. The agent *reads* it, never writes.
- **Dynamic** — agent-written. `scouting/` is append-only (one dated file per pillar per run; the next run reads only that pillar's last ~2 weeks). `synthesis/` and `analysis/` are overwrite-snapshots — no history, regenerate on demand.

Shove everything into one file and within six weeks the context bloats, the agent re-recommends last month's papers, and the pinned literature drifts into a mess.

---

## 🧑‍🔬 Division of Labor

PROBE is a scout. It does not fight. The human still owns every judgement call.

| Human owns | Agent owns |
|---|---|
| **Direction** — is the Identity claim still load-bearing? Is the top Pillar still the right priority? | **Author watch** — recent submissions from the Researchers list |
| **Decision Log curation** — if a paper shakes a default or trips a deferred trigger, update the relevant Decision | **Citation-graph expansion** — semantic neighbors of the Tracked Literature anchors |
| **Evaluation protocol** — own the falsifier thresholds the active Decision Log defines; without these, no report matters | **Anti-topic filtering** — drop whatever the Anti-topics list excludes |
| **Context refresh** — refresh Tracked Literature, Decision Log, and Competitor Monitoring whenever a phase boundary or Decision-Log trigger fires | **Scoring** — Pillar / Decision fit, Identity alignment, novelty, reproducibility, Sim2Real evidence |
| **Feedback loop** — did any scouted paper change an experiment or a Decision? | **Cross-pollination** — forced periodic pick from the cross-pollination rotation |
| **Discarding** — most papers won't matter, that's fine | **Competitor monitoring** — work through the Competitor watch list |

The agent **never** edits `context/MASTER.md`. It can *propose* changes in the report. The human decides.

---

## ⚡ Quick Start

```bash
git clone https://github.com/jonghochoi/probe.git
cd probe
```

1. Open `context/MASTER.md` and fill in **your** Identity, Pillars, Decision Log defaults, Tracked Literature, and Competitor watch list. Shipping defaults are a Sharpa Hand / Isaac Lab template — useful as an example, not a universal config.
2. Decide how you want to run the agent — manually in a Claude.ai conversation, or fully scheduled via Claude Code Routines. See [Agent Setup Guide](#-agent-setup-guide) below.
3. Generate your first Scouting Report. Review it ruthlessly. Tune the prompt. Commit.

> 💡 **Do not automate on day one.** Run manually for 1–2 weeks until the report quality is where you want it. Bad prompt + full automation = weekly garbage generated on schedule.

---

## 🤖 Agent Setup Guide

Full setup walkthrough lives in [`docs/AGENT_SETUP.md`](docs/AGENT_SETUP.md) — cloud-scheduled Claude Code Routines, network/allowlist configuration, the on-demand analysis trio (`/analyze-paper` → `/implement-design` → `/validate-impl`) and its `/reproduce-paper` orchestrator, and troubleshooting. Run the `.claude/prompts/scouting.md` template by hand for 1–2 weeks before automating — the prompt that survives manual iteration is the prompt you deploy as a routine. A single template is shared by all four pillars; replace `<PILLAR>` with `P1`/`P2`/`P3`/`P4` once before each manual run or before pasting into a RemoteTrigger routine.

---

## 🧱 Agent Stack

| Component | Technology |
|---|---|
| **Agent engine** | Claude (Sonnet 4.6 / Opus 4.7) via Claude Code Routines |
| **Scheduler** | RemoteTrigger ([claude.ai/code/routines](https://claude.ai/code/routines)) — cloud cron, direct push to `main` |
| **Paper search** | arXiv REST API (`export.arxiv.org/api/query`, Atom XML) via `curl` |
| **Citation graph** | Semantic Scholar Graph API (`api.semanticscholar.org/graph/v1`, JSON via `jq`) — optional `SEMANTIC_SCHOLAR_API_KEY` |
| **Prompts** | `.claude/prompts/scouting.md` (weekly, shared by P1–P4) + `synthesis.md` (monthly, shared by P1–P4) + `analysis.md` · `implementation.md` · `validation.md` · `reproduction.md` (on-demand) |
| **Output** | Direct commits to `main` — commit history *is* the research log |
| **Context** | `context/P{1..4}.md` (static, human, per-pillar) + `scouting/` (dynamic, agent) + `synthesis/P{1..4}_BRIEF.md` (monthly snapshot) |

---

## 📡 Signals That PROBE Is Actually Working

- At least **one paper per week** triggers a concrete change in your experiment design or in a Decision Log entry.
- The Anti-topics filter catches **≥ 10 papers/week** — that's the healthy exclusion rate.
- The agent reports "no paper scored ≥ 2 this week" without padding.
- Quarterly, you can point at a line in `context/MASTER.md` Decision Log that moved because of a scouted paper.

If none of those are true after a month, the prompt is drifting or the Tracked Literature is stale. Fix the static context first, the prompt second. The model is almost never the problem.

---

## 🔗 Related Projects

| Project | Role |
|---|---|
| **[nexus](https://github.com/jonghochoi/nexus)** | Centralized RL experiment hub — MLflow + TensorBoard dual logging |
| **[observer](https://github.com/jonghochoi/observer)** | Automated evaluation pipeline — multi-view recording, failure-mode classification, checkpoint ranking |
| **probe** *(you are here)* | Research scouting — the upstream that decides *what is worth experimenting on at all* |

> `probe` → `nexus` → `observer` is one research loop.
> PROBE surfaces the idea. NEXUS logs the experiment. OBSERVER judges the policy.

---

## 🙏 Upstream References

PROBE depends on three external repositories. Code and specs vendored from
these repos are kept in sync with their upstream rather than rewritten —
the references below are the exact sources.

| Repo | What PROBE borrows |
|---|---|
| **[epoko77-ai/im-not-ai](https://github.com/epoko77-ai/im-not-ai)** | The `humanize-korean` skill at `.claude/skills/humanize-korean/` and the four pipeline agents (`ai-tell-detector`, `korean-style-rewriter`, `content-fidelity-auditor`, `naturalness-reviewer`) at `.claude/agents/`. Every Korean output (`scouting/`, `synthesis/`, `analysis/`) passes the `humanize-korean` pipeline (detector → rewriter → fidelity / naturalness review, tiered by track) before commit so the long-form Korean prose does not read as machine-generated. Tone and style for Korean output are fully delegated to this skill; PROBE-specific fidelity invariants are codified in [`docs/STYLE.md`](docs/STYLE.md) §4-5. |
| **[huggingface/lerobot](https://github.com/huggingface/lerobot)** | The pinned snapshot vendored at `vendor/lerobot/` — six baseline policies (`pi0`, `pi05`, `pi0_fast`, `smolvla`, `act`, `diffusion`) plus the `rtc` real-time-chunking module, configs, the processor, the `datasets/` tree (the de-facto standard LeRobotDataset format), `transforms/`, and `utils/`. `analysis/<id>/impl/<foundry>/impl.patch` is a unified diff against this snapshot; the pinned commit and refresh procedure live in [`vendor/lerobot/README.md`](vendor/lerobot/README.md). |
| **[colbymchenry/codegraph](https://github.com/colbymchenry/codegraph)** | The MCP code-intelligence server that indexes `vendor/lerobot/` into a per-checkout SQLite knowledge graph at `.codegraph/codegraph.db`. The index is built on demand by `scripts/ensure-codegraph.sh` — `/implement-design` runs it before its first codegraph call (no session-start cost for runs that never touch `vendor/`); only `.codegraph/config.json` (scope definition) is committed. `/implement-design` uses its `codegraph_search` / `codegraph_node` / `codegraph_context` tools to ground Design rows in exact `file:line` coordinates inside the vendored snapshot. See [`CLAUDE.md`](CLAUDE.md) §CodeGraph. |

---

## 📚 Further Reading

| Document | Description |
|---|---|
| [`CLAUDE.md`](CLAUDE.md) | Contributor rules — commit-message style + document Markdown style + CodeGraph usage |
| [`docs/AGENT_SETUP.md`](docs/AGENT_SETUP.md) | Full agent setup — Claude Code Routines, network allowlist, on-demand analysis trio, troubleshooting |
| [`docs/probe_guide.html`](docs/probe_guide.html) | **Korean onboarding guide** — download and open locally for a visual walkthrough of motivation, pipeline, and operations |
| [`docs/STYLE.md`](docs/STYLE.md) | Output formatting rules — emoji system, link format, Korean authoring |
| [`context/MASTER.md`](context/MASTER.md) | Live research context (single source of truth) — Identity, Pillars, Decision Log, Tracked Literature, Competitor Monitoring |
| `context/P{1..4}.md` | Per-pillar narrowed extracts read by the scouting/synthesis pipeline |
| [`scouting/README.md`](scouting/README.md) | Weekly scouting pipeline summary; `P#/YYYY-MM-DD.md` dated reports |
| [`synthesis/README.md`](synthesis/README.md) | Synthesis pipeline summary; `P{1..4}_BRIEF.md` living per-pillar narratives |
| [`analysis/README.md`](analysis/README.md) | On-demand single-paper deep-dive — `/analyze-paper <id\|url\|pdf>` → `analysis/<id>/analysis.md` + `<id>/design.md`; follow-up `/implement-design <design-path> [--foundry <name>]` → `<id>/impl/<foundry>/{impl.md,impl.patch}`; `/validate-impl` → `<id>/validation/<foundry>.md`; `/reproduce-paper <id\|design-path>` orchestrates the three through a converging loop |
| [`analysis/_catalogs/`](analysis/_catalogs/) | Cross-paper lineage catalogs (D19b / D22) — `README.md` defines the common column standard (License + commercial marker, Access icon, `hf:`/`gh:`/`web` link prefix, 🤖/👤/🔀 data type) and operations procedure; `vlm.md` open-weight VLM candidates, `vla.md` landmark VLA lineage matrix, `dataset.md` multi-embodiment further-pretrain corpus catalog with hand-DOF prioritization for the Sharpa / xhand target. Also hosts pillar methodology references — `vlm-prior-preservation.md` (P4 forgetting / carve-out + path-intervention A~D + 4-stage recipe + forward-KL measurement protocol) |
| [`vendor/lerobot/README.md`](vendor/lerobot/README.md) | Read-only `lerobot` snapshot — the v0 foundry, target of every `foundry=lerobot` impl patch. Pinned commit, refresh procedure, license |
| [`scouting/templates/report.md`](scouting/templates/report.md) | Weekly Scouting Report template; latest dated reports are the output-quality bar |
| [`brand.py`](brand.py) | ASCII art, sigil, and color constants |

---

<div align="center">

*"It doesn't read papers for you.*
*It scouts which papers change your mind."*

</div>
