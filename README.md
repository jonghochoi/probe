<div align="center">

<picture><source media="(prefers-color-scheme: dark)" srcset="assets/wordmark-dark.svg"><img src="assets/wordmark.svg" width="300" alt="PROBE · Research Scout"></picture>

<picture><source media="(prefers-color-scheme: dark)" srcset="assets/rule-dark.svg"><img src="assets/rule.svg" width="560" alt=""></picture>

**Stop drowning in arXiv.**<br>
<picture><source media="(prefers-color-scheme: dark)" srcset="assets/claim-dark.svg"><img src="assets/claim.svg" width="300" alt="PROBE marks the target."></picture><br>
**Sit back with a coffee and enjoy the read.**

*Reports in Korean, published to a reading site.*

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
touch dexterous manipulation. PROBE finds those and answers three things
about each:

> *"Is this paper actually new, did it run on real hardware, and can I
> get the code?"*

| Without PROBE <picture><source media="(prefers-color-scheme: dark)" srcset="assets/probe-lost-dark.svg"><img src="assets/probe-lost.svg" width="22" align="absmiddle" alt=""></picture> | With PROBE <picture><source media="(prefers-color-scheme: dark)" srcset="assets/probe-locked-dark.svg"><img src="assets/probe-locked.svg" width="22" align="absmiddle" alt=""></picture> |
|---|---|
| 50–100 papers/day → skim titles, remember none → "I'll check arXiv this weekend" → never happens | 3–5 papers/run → scored, tied to your open decisions, landing in your repo on a fixed cadence, per pillar |
| Re-discovering already-published solutions | Citation graph surfaces the prior art before you waste the week |
| "I'll read that paper properly later" → never does | The one you do pick comes back as a Korean page you can finish in a sitting |

<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/tagline-dark.svg">
  <img src="assets/tagline.svg" width="880"
       alt="The day narrows to a shortlist. Scored, tied to your open decisions, already in your repo.">
</picture>

</div>

---

## How it works

<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/flow-dark.svg">
  <img src="assets/flow.svg" width="880"
       alt="PROBE pipeline — the day's arXiv narrowed to 3–5 papers, out to a scouting report and an analysis page, and back through the human into context/">
</picture>

[![arXiv API](https://img.shields.io/badge/arXiv-API-B31B1B?logo=arxiv&logoColor=white)](https://info.arxiv.org/help/api/index.html)
[![Semantic Scholar](https://img.shields.io/badge/Semantic%20Scholar-Graph%20API-1857B6)](https://api.semanticscholar.org/)

</div>

The agent **never** edits a `context/` file. It proposes in a report, the human
decides.

| Folder | Written by | Cadence | Write mode |
|---|:---:|---|---|
| `context/` | <picture><source media="(prefers-color-scheme: dark)" srcset="assets/human-dark.svg"><img src="assets/human.svg" width="22" align="absmiddle" alt="human"></picture> | monthly at most | agent reads only |
| `scouting/` | <picture><source media="(prefers-color-scheme: dark)" srcset="assets/probe-scouting-dark.svg"><img src="assets/probe-scouting.svg" width="22" align="absmiddle" alt="agent"></picture> | scheduled, per pillar | append — one dated file per run |
| `analysis/` | <picture><source media="(prefers-color-scheme: dark)" srcset="assets/probe-analysis-dark.svg"><img src="assets/probe-analysis.svg" width="22" align="absmiddle" alt="agent"></picture> | on demand | overwrite — one snapshot per paper |
| `comparison/` | <picture><source media="(prefers-color-scheme: dark)" srcset="assets/probe-comparison-dark.svg"><img src="assets/probe-comparison.svg" width="22" align="absmiddle" alt="agent"></picture> | on demand | overwrite — one file per comparison |

One folder the agent only reads, three it only adds to — that split is what
stops it re-recommending last month's papers as `context/` grows.

**Pillars.** The context split is what keeps one run narrow.

- `context/MASTER.md` — cross-cutting content only. Every run reads it.
- `context/P#.md` — one pillar's decision log, tracked literature and
  anti-topics. A scouting run reads **exactly one**.

Pillar names are in [`context/MASTER.md`](context/MASTER.md) §5.

---

## Use it

The slash commands run in a [Claude Code](https://claude.com/claude-code)
session.

| Track | How to run | Output format |
|---|---|---|
| **Scouting** | [`scouting/SETUP.md`](scouting/SETUP.md) | [`scouting/AUTHORING.md`](scouting/AUTHORING.md) |
| **Analysis** | `/analyze <arXiv id>` | [`analysis/AUTHORING.md`](analysis/AUTHORING.md) |
| **Comparison** | `/compare <arXiv id> <arXiv id> [<arXiv id>]` | [`comparison/AUTHORING.md`](comparison/AUTHORING.md) |

- **One paper per `/analyze`**, named explicitly. No automatic `scouting/` →
  `analysis/` hand-off.
- **No arXiv HTML edition → skipped.** Never written from the abstract.
- **`/compare` only reads papers already rewritten.** Run `/analyze` on each
  first. A comparison naming a paper the corpus lacks is not published.
- **Starting from empty** — fill `context/`, generate one report by hand, review
  it ruthlessly, *then* schedule it. Bad prompt + automation = garbage on a
  timer.

