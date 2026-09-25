<div align="center">

<picture><source media="(prefers-color-scheme: dark)" srcset="../../assets/wordmark-dark.svg"><img src="../../assets/wordmark.svg" width="300" alt="PROBE · Research Scout"></picture>

<picture><source media="(prefers-color-scheme: dark)" srcset="../../assets/rule-dark.svg"><img src="../../assets/rule.svg" width="560" alt=""></picture>

**Stop drowning in arXiv.**<br>
<picture><source media="(prefers-color-scheme: dark)" srcset="../../assets/claim-dark.svg"><img src="../../assets/claim.svg" width="300" alt="PROBE marks the target."></picture><br>
**Sit back with a coffee and enjoy the read.**

<br>

<table>
<tr>
<td align="center" width="33%"><picture><source media="(prefers-color-scheme: dark)" srcset="../../assets/probe-lost-dark.svg"><img src="../../assets/probe-lost.svg" width="56" alt=""></picture><br><b>Fewer papers.</b><br><sub>80 a day in, 3 out.</sub></td>
<td align="center" width="33%"><picture><source media="(prefers-color-scheme: dark)" srcset="../../assets/probe-locked-dark.svg"><img src="../../assets/probe-locked.svg" width="56" alt=""></picture><br><b>Each one tied to a decision.</b><br><sub>Scored against your pillar.</sub></td>
<td align="center" width="33%"><picture><source media="(prefers-color-scheme: dark)" srcset="../../assets/probe-analysis-dark.svg"><img src="../../assets/probe-analysis.svg" width="56" alt=""></picture><br><b>Read to the end.</b><br><sub>In Korean, in one sitting.</sub></td>
</tr>
</table>

<a href="https://jonghochoi.github.io/probe/">
  <picture><source media="(prefers-color-scheme: dark)" srcset="../../assets/reading-site-dark.svg"><img src="../../assets/reading-site.svg" width="560" alt="Read the analyses — jonghochoi.github.io/probe"></picture>
</a>

</div>

<details>
<summary><b>How it works</b></summary>

<br>

<div align="center">

<picture><source media="(prefers-color-scheme: dark)" srcset="../../assets/flow-dark.svg"><img src="../../assets/flow.svg" width="880" alt="PROBE pipeline — context/ into the run, arXiv narrowed to 3–5 papers, out to scouting and on-demand pages"></picture>

</div>

The agent **never** edits `context/`. It proposes in a report; the human decides.

</details>

<details>
<summary><b>Who writes what</b></summary>

<br>

| Folder | By | Cadence |
|---|:---:|---|
| `context/` | <picture><source media="(prefers-color-scheme: dark)" srcset="../../assets/human-dark.svg"><img src="../../assets/human.svg" width="22" align="absmiddle" alt="human"></picture> | monthly at most — agent reads only |
| `scouting/` | <picture><source media="(prefers-color-scheme: dark)" srcset="../../assets/probe-scouting-dark.svg"><img src="../../assets/probe-scouting.svg" width="22" align="absmiddle" alt="agent"></picture> | scheduled, per pillar |
| `analysis/` | <picture><source media="(prefers-color-scheme: dark)" srcset="../../assets/probe-analysis-dark.svg"><img src="../../assets/probe-analysis.svg" width="22" align="absmiddle" alt="agent"></picture> | on demand |
| `comparison/` | <picture><source media="(prefers-color-scheme: dark)" srcset="../../assets/probe-comparison-dark.svg"><img src="../../assets/probe-comparison.svg" width="22" align="absmiddle" alt="agent"></picture> | on demand |
| `presentation/` | <picture><source media="(prefers-color-scheme: dark)" srcset="../../assets/probe-presentation-dark.svg"><img src="../../assets/probe-presentation.svg" width="22" align="absmiddle" alt="agent"></picture> | on demand |

</details>

<details>
<summary><b>Commands</b></summary>

<br>

```text
/analyze  <arXiv id>
/compare  <arXiv id> <arXiv id> [<arXiv id>]
/present  <arXiv id>
/ideate   [<arXiv id | alias | topic>]
```

Scouting runs on a schedule — see [`scouting/SETUP.md`](../../scouting/SETUP.md).

</details>

<br>

<div align="center">

[![arXiv API](https://img.shields.io/badge/arXiv-API-B06749?logo=arxiv&logoColor=white&labelColor=1F1611)](https://info.arxiv.org/help/api/index.html)
[![Semantic Scholar](https://img.shields.io/badge/Semantic%20Scholar-Graph%20API-B06749?labelColor=1F1611)](https://api.semanticscholar.org/)

</div>
