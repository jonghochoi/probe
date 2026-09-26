<div align="center">

<picture><source media="(prefers-color-scheme: dark)" srcset="../../assets/wordmark-dark.svg"><img src="../../assets/wordmark.svg" width="300" alt="PROBE · Research Scout"></picture>

<picture><source media="(prefers-color-scheme: dark)" srcset="../../assets/rule-dark.svg"><img src="../../assets/rule.svg" width="560" alt=""></picture>

**Stop drowning in arXiv.**<br>
<picture><source media="(prefers-color-scheme: dark)" srcset="../../assets/claim-dark.svg"><img src="../../assets/claim.svg" width="300" alt="PROBE marks the target."></picture><br>
**Sit back with a coffee and enjoy the read.**

<a href="https://jonghochoi.github.io/probe/">
  <picture><source media="(prefers-color-scheme: dark)" srcset="../../assets/reading-site-dark.svg"><img src="../../assets/reading-site.svg" width="560" alt="Read the analyses — jonghochoi.github.io/probe"></picture>
</a>

</div>

---

```console
$ claude
> /analyze 2409.12345
  ✓ read arXiv HTML original
  ✓ wrote analysis/2409.12345.md   (요약 + body)
> /compare 2409.12345 2410.54321
  ✓ wrote comparison/<slug>.md
> /present 2409.12345
  ✓ wrote presentation/2409.12345.md   (起承轉結)
```

| | Track | Run | Writes |
|:---:|---|---|---|
| <picture><source media="(prefers-color-scheme: dark)" srcset="../../assets/probe-scouting-dark.svg"><img src="../../assets/probe-scouting.svg" width="48" alt="Scouting"></picture> | **Scouting**<br><sub>sweeps the day's arXiv</sub> | `scheduled` | `scouting/P#/<date>.md` |
| <picture><source media="(prefers-color-scheme: dark)" srcset="../../assets/probe-analysis-dark.svg"><img src="../../assets/probe-analysis.svg" width="48" alt="Analysis"></picture> | **Analysis**<br><sub>reads one paper whole</sub> | `/analyze <id>` | `analysis/<id>.md` |
| <picture><source media="(prefers-color-scheme: dark)" srcset="../../assets/probe-comparison-dark.svg"><img src="../../assets/probe-comparison.svg" width="48" alt="Comparison"></picture> | **Comparison**<br><sub>weighs two or three</sub> | `/compare <id> <id>` | `comparison/<slug>.md` |
| <picture><source media="(prefers-color-scheme: dark)" srcset="../../assets/probe-presentation-dark.svg"><img src="../../assets/probe-presentation.svg" width="48" alt="Presentation"></picture> | **Presentation**<br><sub>turns one into a talk</sub> | `/present <id>` | `presentation/<id>.md` |
| <picture><source media="(prefers-color-scheme: dark)" srcset="../../assets/human-dark.svg"><img src="../../assets/human.svg" width="48" alt="Ideation"></picture> | **Ideation**<br><sub>you + the corpus</sub> | `/ideate [topic]` | chat only |

1. **`/analyze` first.** Compare and present read the rewrite, never the PDF.
2. **No arXiv HTML → skipped.** Nothing is written from an abstract.
3. **`context/` is read-only** to the agent. It proposes; you decide.

---

<picture><source media="(prefers-color-scheme: dark)" srcset="../../assets/tagline-dark.svg"><img src="../../assets/tagline.svg" width="880" alt="The day narrows to a shortlist. Scored, tied to your open decisions, already in your repo."></picture>

| <picture><source media="(prefers-color-scheme: dark)" srcset="../../assets/probe-lost-dark.svg"><img src="../../assets/probe-lost.svg" width="22" align="absmiddle" alt=""></picture> Without | <picture><source media="(prefers-color-scheme: dark)" srcset="../../assets/probe-locked-dark.svg"><img src="../../assets/probe-locked.svg" width="22" align="absmiddle" alt=""></picture> With PROBE |
|---|---|
| 50–100 papers/day, none remembered | 3–5 per run, scored against your open decisions |
| Prior art rediscovered the hard way | The citation graph surfaces it first |
| "I'll read it properly later" | A Korean page you finish in a sitting |

<div align="center">

<picture><source media="(prefers-color-scheme: dark)" srcset="../../assets/flow-dark.svg"><img src="../../assets/flow.svg" width="880" alt="PROBE pipeline — context/ into the run, arXiv narrowed to 3–5 papers, out to scouting and on-demand pages"></picture>

</div>

<div align="center">

[![arXiv API](https://img.shields.io/badge/arXiv-API-B06749?logo=arxiv&logoColor=white&labelColor=1F1611)](https://info.arxiv.org/help/api/index.html)
[![Semantic Scholar](https://img.shields.io/badge/Semantic%20Scholar-Graph%20API-B06749?labelColor=1F1611)](https://api.semanticscholar.org/)

</div>
