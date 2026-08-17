<div align="center">

# 🛸 PROBE · Research Scout for Dexterous Manipulation

**Stop drowning in arXiv. Start changing what you train next week.**

*Citation-graph expansion · Anti-topic filtering · Weekly decision-grade Scouting Reports*

[![Claude](https://img.shields.io/badge/Claude-Agent-D97757?logo=anthropic&logoColor=white)](https://claude.com/claude-code)
[![arXiv API](https://img.shields.io/badge/arXiv-API-B31B1B?logo=arxiv&logoColor=white)](https://info.arxiv.org/help/api/index.html)
[![Semantic Scholar](https://img.shields.io/badge/Semantic%20Scholar-Graph%20API-1857B6)](https://api.semanticscholar.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

</div>

---

> ### 🔭 Reading the analyses
>
> **[jonghochoi.github.io/probe](https://jonghochoi.github.io/probe/)** is the
> reading site: papers re-written in Korean from their arXiv originals, so a
> reader gets the mechanism without opening the paper. `/analyze <id>` writes
> one into `analysis/`; the site is exactly that set. Everything the site is
> made of lives in `site/` — the format contract (`site/AUTHORING.md`) and the
> generator — and it deploys from Actions; the generated HTML is never
> committed. (`analysis_legacy/` holds the legacy corpus, on GitHub until those
> papers are re-written.)
>
> ```bash
> pip install -r site/requirements.txt
> npm install --no-save --prefix site/builder \
>   katex@0.16.22 pretendard @fontsource/jetbrains-mono
> python3 site/build-site.py --serve        # http://127.0.0.1:8000/probe/
> ```

---

## Why PROBE

Running dexterous-manipulation research is a full-time job — reward curves, tactile pipelines, Sim-to-Real gaps. Meanwhile **50–100 new papers land on `cs.RO` + `cs.LG` every day**, and maybe 3–5 a week actually touch hand-centric dexterous manipulation. Missing the right one means re-solving a problem someone already published.

PROBE finds them and refuses to let them die in your downloads folder. It answers the only question that matters:

> *"If this paper is right, what do I change in my training / evaluation pipeline next week?"*

| Without PROBE | With PROBE |
|---|---|
| "I'll check arXiv this weekend" → never happens | A Scouting Report lands in your repo on a fixed cadence, per pillar |
| 50–100 papers/day → skim titles, remember none | 3–5 papers/run → scored, tied to your open questions |
| Survey mode: "this is interesting" | Decision mode: "change DR range on object mass to [0.5, 2.0] kg" |
| Re-discovering already-published solutions | Citation graph surfaces the prior art before you waste the week |
| "I'll read that paper properly later" → never does | `/analyze` → a Korean re-telling of the paper, published to the reading site |

**Division of labor.** PROBE is a scout — it does not fight.

| | Owns |
|---|---|
| **Agent** | citation-graph expansion · anti-topic filtering · scoring · cross-pollination |
| **Human** | direction · Decision-Log curation · evaluation thresholds · per-pillar context refresh · discarding |

The agent **never** edits any `context/` file — it proposes in a report; the human decides.

---

## Pipeline

PROBE has **two output tracks** sharing one static, human-owned context — outward `scouting/` (find) and focused `analysis/` (read deeply). Each runs on its own trigger and writes to its own folder.

> **Pillars** — the static context splits into research pillars, each `context/P#.md` owning its own Decision Log and Tracked Literature while `MASTER.md` holds cross-cutting content only. A scouting run reads just **one `P#.md`** to stay lean; canonical names in [`context/MASTER.md`](context/MASTER.md) §5.

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
   │ scheduled · per P# │         │       /analyze        │
   │                    │         │                       │
   │  citation graph ·  │         │ one paper → Korean    │
   │  keyword sweep ·   │         │  re-telling from the  │
   │   curated lists    │         │   arXiv HTML original │
   └──────────┬─────────┘         └───────────┬───────────┘
              │ append new file               │ overwrite snapshot
              ▼                               ▼
   ┌────────────────────┐         ┌───────────────────────┐
   │     scouting/      │         │       analysis/       │
   │  P#/YYYY-MM-DD.md  │         │       <id>.md         │
   │    3–5 papers,     │         │   one file per paper, │
   │   decision-grade   │         │  published as a page  │
   └──────────┬─────────┘         └───────────┬───────────┘
              └───────────────┬───────────────┘
                              ▼  informs
         Human — read, judge, discard, refresh context
```

**Static vs. dynamic, never mixed.**

| Folder | Written by | Cadence | Write mode |
|---|---|---|---|
| `context/` | human | monthly at most | agent reads only |
| `scouting/` | agent | scheduled, per pillar | append — one dated file per run |
| `analysis/` | agent | on demand | overwrite — one snapshot per paper |
| `analysis_legacy/` | — | frozen | legacy corpus, kept until re-written |

Keeping the two apart is what stops the agent re-recommending last month's papers as the context bloats.

The on-demand entry point — run it in a local session, one-shot `claude -p "/analyze 2410.07864"`, or on the web:

- `/analyze <arXiv id>` → `analysis/<id>.md` — a Korean re-telling written from the paper's arXiv HTML original, with our own reading anchored to your `P#`/`D#`. It publishes as a page on the reading site; the format contract is [`site/AUTHORING.md`](site/AUTHORING.md)

One paper per run, named explicitly — there is no automatic `scouting/` → `analysis/` hand-off. A paper with no arXiv HTML edition is skipped rather than written from its abstract.

---

## Agent Stack

- **One template, all pillars** — `.claude/prompts/scouting.txt`; replace `<PILLAR>` with the target pillar id before each run.
- **Scheduled scouting** — cloud routines, network allowlist, troubleshooting: [`docs/agent-setup.md`](docs/agent-setup.md).
- **On-demand `/analyze`** — no routine setup; runs from any Claude Code session. Logic lives in `.claude/prompts/analyze.txt`, output format in [`site/AUTHORING.md`](site/AUTHORING.md). The scouting format lives in [`docs/style.md`](docs/style.md).

```bash
git clone https://github.com/jonghochoi/probe.git
cd probe
# 1. Fill context/MASTER.md (global anchor: Identity, Pillars overview), then each
#    context/P#.md with that pillar's Decision Log, Tracked Literature, watch list.
# 2. Generate a first Scouting Report by hand; review it ruthlessly; tune the prompt.
# 3. Only then schedule it as a routine — bad prompt + automation = garbage on a timer.
```

---

<div align="center">

*"It doesn't read papers for you.*
*It scouts which papers change your mind."*

</div>
