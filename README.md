<div align="center">

# 🛸 PROBE · Research Scout for Dexterous Manipulation

**Stop drowning in arXiv. Start changing what you train next week.**

*Citation-graph expansion · Anti-topic filtering · Decision-grade Scouting Reports*

[![Claude](https://img.shields.io/badge/Claude-Agent-D97757?logo=anthropic&logoColor=white)](https://claude.com/claude-code)
[![arXiv API](https://img.shields.io/badge/arXiv-API-B31B1B?logo=arxiv&logoColor=white)](https://info.arxiv.org/help/api/index.html)
[![Semantic Scholar](https://img.shields.io/badge/Semantic%20Scholar-Graph%20API-1857B6)](https://api.semanticscholar.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

</div>

---

PROBE is a Claude agent that reads a research context you own and writes two
things: a scheduled **Scouting Report** — 3–5 papers per run, scored, each tied
to an open decision in your own Decision Log — and, on demand, an **Analysis**,
one paper re-told in Korean from its arXiv HTML original. The reports stay in
the repo; the analyses publish to the reading site at
**[jonghochoi.github.io/probe](https://jonghochoi.github.io/probe/)**.

---

## Why PROBE

Running dexterous-manipulation research is a full-time job — reward curves,
tactile pipelines, Sim-to-Real gaps. Meanwhile **50–100 new papers land on
`cs.RO` + `cs.LG` every day**, and maybe 3–5 a week actually touch hand-centric
dexterous manipulation. PROBE finds those and answers the only question that
matters:

> *"If this paper is right, what do I change in my training / evaluation
> pipeline next week?"*

| Without PROBE | With PROBE |
|---|---|
| "I'll check arXiv this weekend" → never happens | A Scouting Report lands in your repo on a fixed cadence, per pillar |
| 50–100 papers/day → skim titles, remember none | 3–5 papers/run → scored, tied to your open questions |
| Survey mode: "this is interesting" | Decision mode: "change DR range on object mass to [0.5, 2.0] kg" |
| Re-discovering already-published solutions | Citation graph surfaces the prior art before you waste the week |
| "I'll read that paper properly later" → never does | `/analyze` → a Korean re-telling of the paper, published to the reading site |

**What a hit actually looks like** — from
[`scouting/P1/2026-08-17.md`](scouting/P1/2026-08-17.md):

> **G0.5: One Autoregressive Stream for Robot Reasoning and Action**
> [arXiv:2608.11739](https://arxiv.org/abs/2608.11739) · source: citation-graph (π0)
>
> ![P1](https://img.shields.io/badge/P1-f5e9d5.svg) / ![D7](https://img.shields.io/badge/D7-d97706.svg) ![D1](https://img.shields.io/badge/D1-d97706.svg)
>
> **(c) 시사점** — 액션 전문가 분리 구조의 이점 재검토 필요: 단일 스트림이 7개
> 독립 벤치마크에서 π0.5·GR00T-N1.7 모두 제압 → Body/Hand 이중 헤드 분리 설계의
> 성능 우위를 직접 실증해야 하는 압력 증가

Not "this paper is interesting." A named decision — `D7`, how the π backbone
gets partitioned — and what that decision now owes.

**Division of labor.** PROBE is a scout; it does not fight. The agent owns
citation-graph expansion, anti-topic filtering, scoring and cross-pollination.
Direction, Decision-Log curation, evaluation thresholds and discarding stay
human — and the agent **never** edits a `context/` file, it proposes in a report
and the human decides.

---

## How it works

Two output tracks share one static, human-owned context, each on its own trigger
and writing to its own folder. Keeping static and dynamic apart is what stops
the agent re-recommending last month's papers as the context bloats.

```
   context/   static · human-owned · read-only on every run
      │       MASTER.md — global anchor · P#.md — per-pillar Decision Log
      ▼
   PROBE ───── scheduled, one pillar per run ────►  scouting/P#/YYYY-MM-DD.md
      │                                             3–5 papers, decision-grade
      └─────── /analyze <arXiv id> ──────────────►  analysis/<id>.md
      │                                             one paper, a published page
      ▼  informs
   Human — read, judge, discard, refresh context/
```

| Folder | Written by | Cadence | Write mode |
|---|---|---|---|
| `context/` | human | monthly at most | agent reads only |
| `scouting/` | agent | scheduled, per pillar | append — one dated file per run |
| `analysis/` | agent | on demand | overwrite — one snapshot per paper |
| `analysis_legacy/` | — | frozen | legacy corpus, kept until re-written |

**Pillars.** The static context splits into research pillars, each
`context/P#.md` owning its own Decision Log and Tracked Literature while
`MASTER.md` holds cross-cutting content only. A scouting run reads just **one
`P#.md`** to stay lean; canonical names in
[`context/MASTER.md`](context/MASTER.md) §5.

---

## Use it

| Track | Trigger | Setup | Output format |
|---|---|---|---|
| **Scouting** | a cloud routine, one per pillar | [`SETUP.md`](SETUP.md) — RemoteTrigger form, network allowlist, first-run verification | [`scouting/AUTHORING.md`](scouting/AUTHORING.md) |
| **Analysis** | `/analyze <arXiv id>` from any Claude Code session, or `claude -p "/analyze 2410.07864"` | none | [`site/AUTHORING.md`](site/AUTHORING.md) |

One paper per `/analyze` run, named explicitly — there is no automatic
`scouting/` → `analysis/` hand-off, and a paper with no arXiv HTML edition is
skipped rather than written from its abstract. Both prompts live in
`.claude/prompts/`; the site's generator is mapped in
[`site/README.md`](site/README.md).

Starting from an empty context: fill `context/MASTER.md` and each
`context/P#.md`, generate one Scouting Report by hand, review it ruthlessly, and
only then schedule it. Bad prompt + automation = garbage on a timer.

---

<div align="center">

*"It doesn't read papers for you.*
*It scouts which papers change your mind."*

</div>
