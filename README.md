<div align="center">

# <picture><source media="(prefers-color-scheme: dark)" srcset="assets/wordmark-dark.svg"><img src="assets/wordmark.svg" width="300" alt="PROBE · Research Scout"></picture>

**Stop drowning in arXiv. Start changing what you train next week.**

*Citation-graph expansion · Anti-topic filtering · Decision-grade scouting reports*

[![Claude](https://img.shields.io/badge/Claude-Agent-D97757?logo=anthropic&logoColor=white)](https://claude.com/claude-code)
[![arXiv API](https://img.shields.io/badge/arXiv-API-B31B1B?logo=arxiv&logoColor=white)](https://info.arxiv.org/help/api/index.html)
[![Semantic Scholar](https://img.shields.io/badge/Semantic%20Scholar-Graph%20API-1857B6)](https://api.semanticscholar.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

<a href="https://jonghochoi.github.io/probe/">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/reading-site-dark.svg">
    <img src="assets/reading-site.svg" width="560"
         alt="Read the analyses — jonghochoi.github.io/probe">
  </picture>
</a>

</div>

---

## Why PROBE

**50–100 new papers** land on `cs.RO` + `cs.LG` every day. Maybe 3–5 a week
touch dexterous manipulation. PROBE finds those and answers one question:

> *"If this paper is right, what do I change in my training / evaluation
> pipeline next week?"*

| <picture><source media="(prefers-color-scheme: dark)" srcset="assets/probe-lost-dark.svg"><img src="assets/probe-lost.svg" width="22" align="absmiddle" alt=""></picture> Without PROBE | <picture><source media="(prefers-color-scheme: dark)" srcset="assets/probe-locked-dark.svg"><img src="assets/probe-locked.svg" width="22" align="absmiddle" alt=""></picture> With PROBE |
|---|---|
| 50–100 papers/day → skim titles, remember none → "I'll check arXiv this weekend" → never happens | 3–5 papers/run → scored, tied to your open questions, landing in your repo on a fixed cadence, per pillar |
| Re-discovering already-published solutions | Citation graph surfaces the prior art before you waste the week |
| "I'll read that paper properly later" → never does | `/analyze` → a Korean re-telling, published to the reading site |

**PROBE is a scout — it does not fight.**

| | Owns |
|---|---|
| **Agent** | citation-graph expansion · anti-topic filtering · scoring · cross-pollination |
| **Human** | direction · Decision-Log curation · evaluation thresholds · discarding |

The agent **never** edits a `context/` file. It proposes in a report, the human
decides.

---

## Who owns what

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/flow-dark.svg">
  <img src="assets/flow.svg" width="880"
       alt="PROBE pipeline — the day's arXiv narrowed to 3–5 papers, out to a scouting report and an analysis page, and back through the human into context/">
</picture>

| Folder | Written by | Cadence | Write mode |
|---|---|---|---|
| `context/` | human | monthly at most | agent reads only |
| `scouting/` | agent | scheduled, per pillar | append — one dated file per run |
| `analysis/` | agent | on demand | overwrite — one snapshot per paper |
| `analysis_legacy/` | — | frozen | legacy corpus, kept until re-written |

Keeping static and dynamic apart is what stops the agent re-recommending last
month's papers as the context bloats.

**Pillars.** Each `context/P#.md` owns one pillar's Decision Log and Tracked
Literature. `MASTER.md` holds cross-cutting content only, and a scouting run
reads just **one `P#.md`** — names in
[`context/MASTER.md`](context/MASTER.md) §5.

---

## Use it

| Track | Trigger | Setup | Output format |
|---|---|---|---|
| **Scouting** | a cloud routine, one per pillar | [`SETUP.md`](SETUP.md) | [`scouting/AUTHORING.md`](scouting/AUTHORING.md) |
| **Analysis** | `/analyze <arXiv id>` from any Claude Code session | none | [`site/AUTHORING.md`](site/AUTHORING.md) |

- **One paper per `/analyze`**, named explicitly. No automatic `scouting/` →
  `analysis/` hand-off.
- **No arXiv HTML edition → skipped.** Never written from the abstract.
- **Starting from empty** — fill `context/`, generate one report by hand, review
  it ruthlessly, *then* schedule it. Bad prompt + automation = garbage on a
  timer.
