<div align="center">

# 🛸 PROBE · Research Scout for Dexterous Manipulation

<img src="docs/LOGO.png" alt="NEXUS Logo" width="600">

**Stop drowning in arXiv. Start changing what you train next week.**

*Citation-graph expansion · Anti-topic filtering · Weekly decision-grade Scouting Reports*

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)](https://python.org)
[![Claude](https://img.shields.io/badge/Claude-Agent-D97757?logo=anthropic&logoColor=white)](https://claude.com/claude-code)
[![arXiv API](https://img.shields.io/badge/arXiv-API-B31B1B?logo=arxiv&logoColor=white)](https://info.arxiv.org/help/api/index.html)
[![Semantic Scholar](https://img.shields.io/badge/Semantic%20Scholar-Graph%20API-1857B6)](https://api.semanticscholar.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

</div>

---

> ### 📖 New here? Start with the onboarding guide.
>
> [`docs/probe_guide.html`](docs/probe_guide.html)
> — download and open in a browser for a full visual walkthrough of PROBE.
>
> ```bash
> git clone https://github.com/jonghochoi/probe.git
> open probe/docs/probe_guide.html         # macOS
> # xdg-open probe/docs/probe_guide.html   # Linux
> ```

---

## Why PROBE

Running dexterous-manipulation research is a full-time job — reward curves, tactile pipelines, Sim-to-Real gaps. Meanwhile **50–100 new papers land on `cs.RO` + `cs.LG` every day**, and maybe 3–5 a week actually touch hand-centric dexterous manipulation. That is a 3–5% signal rate in a firehose, and the cost of missing the right paper is re-solving a problem someone already published.

PROBE finds those 3–5 for you and refuses to let them die in your downloads folder. It does not stop at "here are some interesting papers" — it answers the only question that matters:

> *"If this paper is right, what do I change in my training / evaluation pipeline next week?"*

| Without PROBE | With PROBE |
|---|---|
| "I'll check arXiv this weekend" → never happens | A Scouting Report lands in your repo on a fixed cadence, per pillar |
| 50–100 papers/day → skim titles, remember none | 3–5 papers/run → scored, tied to your open questions |
| Survey mode: "this is interesting" | Decision mode: "change DR range on object mass to [0.5, 2.0] kg" |
| Re-discovering already-published solutions | Citation graph surfaces the prior art before you waste the week |
| "I'll read that paper properly later" → never does | `/analyze-paper` → Korean deep-dive **+ a vendor-agnostic Layer 1 Design** anchored to your Decision Log |
| "Great paper, but I'll never reproduce it" | `/reproduce-paper` drives Design → impl → validation in a converging loop, shipping a unified-diff patch against a target foundry (default `lerobot`) |

**Division of labor.** PROBE is a scout — it does not fight. The agent owns citation-graph expansion, anti-topic filtering, scoring, and cross-pollination. The human owns every judgement call: direction, Decision-Log curation, evaluation thresholds, per-pillar context refresh, and discarding. The agent **never** edits any `context/` file — it proposes in a report; the human decides.

---

## Pipeline

PROBE has **two output tracks** sharing one static, human-owned context — outward `scouting/` (find) and focused `analysis/` (reproduce). Each runs on its own trigger and writes to its own folder.

> **Pillars**: the static context is organized into a small set of research pillars, each owning its own Decision Log and Tracked Literature — canonical names and definitions in [`context/MASTER.md`](context/MASTER.md) §5.
>
> **Anchor vs. per-pillar owner**: `context/MASTER.md` is a thin **global anchor** (the pillars + cross-cutting content — Identity, Pillars overview, Venue, Cross-pollination). Each `context/P#.md` **owns** its pillar's Decision Log, Tracked Literature, Anti-topics, and Curated Lists; the cloud scouting routine reads **one `P#.md`** to keep agent context lean. Edit the `P#.md` for pillar content; edit MASTER only for global content.

```
   ┌────────────────────────────────────────────────────────┐
   │ context/  (static · human-owned · read-only every run) │
   │ MASTER.md  · global anchor — Pillars + Venue           │
   │ P#.md      · per-pillar owners — Decision Log / lit    │
   └──────────────────────────┬─────────────────────────────┘
                              │ read-only (every run)
                              ▼
                          P R O B E
              ┌───────────────┴───────────────┐
              ▼                               ▼
   ┌────────────────────┐         ┌───────────────────────┐
   │      OUTWARD       │         │        FOCUSED        │
   │      Scouting      │         │   On-demand Analysis  │
   │ scheduled · per P# │         │     /analyze-paper    │
   │                    │         │                       │
   │  citation graph ·  │         │ one paper → deep-dive │
   │  keyword sweep ·   │         │   → Layer 1 Design →  │
   │   curated lists    │         │   impl → validation   │
   └──────────┬─────────┘         └───────────┬───────────┘
              │ append new file               │ overwrite snapshot
              ▼                               ▼
   ┌────────────────────┐         ┌───────────────────────┐
   │     scouting/      │         │       analysis/       │
   │  P#/YYYY-MM-DD.md  │         │   <id>/analysis.md +  │
   │    3–5 papers,     │         │   design.md (+ impl/  │
   │   decision-grade   │         │      validation)      │
   └──────────┬─────────┘         └───────────┬───────────┘
              └───────────────┬───────────────┘
                              ▼  informs
         Human — read, judge, discard, refresh context
```

**Static vs. dynamic, never mixed.** `context/` is static — it changes monthly at most, and the agent only *reads* it. The tracks are dynamic and agent-written: `scouting/` is append-only (one dated file per pillar per run; the next run reads only that pillar's last ~2 weeks), and `analysis/` is an overwrite-snapshot regenerated on demand. Keeping the two apart is what stops the agent re-recommending last month's papers as the context bloats.

**Analysis convergence loop.** A single `/analyze-paper` produces the deep-dive *and* a Layer 1 Design; `/implement-design` maps the Design onto a target foundry; `/validate-impl` statically checks the result. `/reproduce-paper` orchestrates the three as a bounded loop — fixing the impl against the foundry (inner loop) or re-extracting the Design from the paper (outer loop) until the verdict reaches a fixed point. Full branch matrix in [`.claude/prompts/reproduction.md`](.claude/prompts/reproduction.md).

The two entry points (logic in `.claude/prompts/<name>.md`; run them in a local session, one-shot `claude -p "/analyze-paper 2410.07864"`, or on the web):

- `/analyze-paper <arXiv id | url | pdf url>` → `analysis.md` + `design.md`
- `/reproduce-paper <arXiv id | design path> [--foundry <name>] [--max-rounds N]` — drives `/implement-design` → `/validate-impl` against a target foundry (default `lerobot`) until the verdict stabilizes (default `--max-rounds 3`)

The agent never edits `context/MASTER.md` or `vendor/lerobot/`; each run overwrites its `analysis/<id>/` snapshot (no append); input is one paper named explicitly on the command — there is no automatic `scouting/` → `analysis/` hand-off. The deep-dive index lives at [`catalogs/analyses.md`](catalogs/analyses.md).

---

## Agent Stack

Run `.claude/prompts/scouting.md` by hand for a week or two before automating — the prompt that survives manual iteration is the one you deploy. A single template is shared across all pillars; replace `<PILLAR>` with the target pillar id before each run. Full setup — cloud routines, network allowlist, the on-demand analysis trio and its `/reproduce-paper` orchestrator, troubleshooting — lives in [`docs/AGENT_SETUP.md`](docs/AGENT_SETUP.md).

```bash
git clone https://github.com/jonghochoi/probe.git
cd probe
# 1. Fill context/MASTER.md (global anchor: Identity, Pillars overview), then each
#    context/P#.md with that pillar's Decision Log, Tracked Literature, watch list.
# 2. Generate a first Scouting Report by hand; review it ruthlessly; tune the prompt.
# 3. Only then schedule it as a routine — bad prompt + automation = garbage on a timer.
```

| Component | Technology |
|---|---|
| **Agent engine** | Claude (Sonnet 4.6 / Opus 4.8) via Claude Code |
| **Scheduler** | RemoteTrigger ([claude.ai/code/routines](https://claude.ai/code/routines)) — cloud cron, direct push to `main` |
| **Paper search** | arXiv REST API via `curl` (Atom XML) |
| **Citation graph** | Semantic Scholar Graph API (JSON via `jq`) — optional `SEMANTIC_SCHOLAR_API_KEY` |
| **Code grounding** | CodeGraph MCP over `vendor/lerobot/` — `/implement-design` cites exact `file:line` |
| **Prompts** | `.claude/prompts/scouting.md` (shared across pillars) + `analysis.md` · `implementation.md` · `validation.md` · `reproduction.md` (on-demand) |
| **Output** | Direct commits to `main` — the commit history *is* the research log |

---

## References

PROBE vendors code and specs from external repos — kept in sync with upstream, not rewritten.

| Source | What PROBE borrows |
|---|---|
| [huggingface/lerobot](https://github.com/huggingface/lerobot) | The pinned snapshot at `vendor/lerobot/` — the v0 foundry every `impl.patch` targets. Pinned commit + refresh in [`vendor/lerobot/README.md`](vendor/lerobot/README.md). |
| [colbymchenry/codegraph](https://github.com/colbymchenry/codegraph) | The MCP server indexing `vendor/lerobot/`, so `/implement-design` grounds Design rows in exact `file:line`. See [`CLAUDE.md`](CLAUDE.md) § CodeGraph. |

---

<div align="center">

*"It doesn't read papers for you.*
*It scouts which papers change your mind."*

</div>
