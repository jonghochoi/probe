<div align="center">

<a href="https://jonghochoi.github.io/probe/"><picture><source media="(prefers-color-scheme: dark)" srcset="assets/hero-dark.svg"><img src="assets/hero.svg" width="880" alt="PROBE — Stop drowning in arXiv. PROBE marks the target. Open the reading site."></picture></a>

</div>

<br>

<details>
<summary><b>Why PROBE</b> — from the arXiv flood to your next idea</summary>
<br>

| Without PROBE | With PROBE |
|---|---|
| Skim a hundred titles, remember none | **Scouting** — a few scored papers, tied to your open decisions |
| "I'll read it later" → never | **Analysis** — a Korean page you finish in a sitting |
| Three papers, the same claimed win | **Comparison** — only where they part |
| Slides the night before | **Presentation** — a talk, with what to say per slide |
| "Surely someone has tried this" | **Ideation** — the untried idea, and how to refute it |

Every rewrite starts from the arXiv original, not the abstract. Every judgement
is made against your own pillars and Decision Log. All of it publishes
together, in Korean, on the reading site.

</details>

<details>
<summary><b>How it works</b> — you own the context, the agent writes the rest</summary>
<br>

<picture><source media="(prefers-color-scheme: dark)" srcset="assets/own-dark.svg"><img src="assets/own.svg" width="880" alt="Who writes what: you write context/, and PROBE reads it and writes scouting/, analysis/, comparison/ and presentation/. Changes to context/ come to you as proposals."></picture>

`context/MASTER.md` holds what cuts across pillars, and each `context/P#.md`
holds one pillar's decision log, tracked literature and anti-topics.

| Track | You run in [Claude Code](https://claude.com/claude-code) | It writes |
|:---:|---|---|
| <picture><source media="(prefers-color-scheme: dark)" srcset="assets/probe-scouting-dark.svg"><img src="assets/probe-scouting.svg" height="64" alt="scouting"></picture><br><sub><b>Scouting</b></sub> | scheduled, every pillar in one run — [setup](scouting/SETUP.md) · `/scout [pillars]` | `scouting/P#/<date>.md` and `scouting/runs/<date>.md` — [format](scouting/AUTHORING.md) |
| <picture><source media="(prefers-color-scheme: dark)" srcset="assets/probe-analysis-dark.svg"><img src="assets/probe-analysis.svg" height="64" alt="analysis"></picture><br><sub><b>Analysis</b></sub> | `/analyze <arXiv id>` | `analysis/<id>.md` — [format](analysis/AUTHORING.md) |
| <picture><source media="(prefers-color-scheme: dark)" srcset="assets/probe-comparison-dark.svg"><img src="assets/probe-comparison.svg" height="64" alt="comparison"></picture><br><sub><b>Comparison</b></sub> | `/compare <id> <id> [<id>]` | `comparison/<slug>.md` — [format](comparison/AUTHORING.md) |
| <picture><source media="(prefers-color-scheme: dark)" srcset="assets/probe-presentation-dark.svg"><img src="assets/probe-presentation.svg" height="64" alt="presentation"></picture><br><sub><b>Presentation</b></sub> | `/present <arXiv id>` | `presentation/<id>.md` — [format](presentation/AUTHORING.md) |
| <picture><source media="(prefers-color-scheme: dark)" srcset="assets/probe-ideation-dark.svg"><img src="assets/probe-ideation.svg" height="64" alt="ideation"></picture><br><sub><b>Ideation</b></sub> | `/ideate [<id \| alias \| topic>]` | nothing, it answers in chat |

</details>

<details>
<summary><b>Ground rules</b> — what to know before you automate</summary>
<br>

- **Start by hand.** One report, reviewed ruthlessly, *then* the schedule.
- **You name the papers.** A report never feeds `analysis/` on its own.
- **No arXiv HTML, no rewrite.** Never written from the abstract.
- **The rewrite comes first.** `/compare` and `/present` read what `/analyze` wrote.

</details>
