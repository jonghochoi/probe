<div align="center">

<picture><source media="(prefers-color-scheme: dark)" srcset="../../assets/wordmark-dark.svg"><img src="../../assets/wordmark.svg" width="300" alt="PROBE · Research Scout"></picture>

<picture><source media="(prefers-color-scheme: dark)" srcset="../../assets/rule-dark.svg"><img src="../../assets/rule.svg" width="560" alt=""></picture>

**Stop drowning in arXiv.**<br>
<picture><source media="(prefers-color-scheme: dark)" srcset="../../assets/claim-dark.svg"><img src="../../assets/claim.svg" width="300" alt="PROBE marks the target."></picture><br>
**Sit back with a coffee and enjoy the read.**

</div>

<table>
<tr>
<td width="56%" valign="top">

**Thirty seconds, three commands.**

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

</td>
<td width="44%" valign="middle" align="center">

<table>
<tr><td align="center"><picture><source media="(prefers-color-scheme: dark)" srcset="../../assets/probe-scouting-dark.svg"><img src="../../assets/probe-scouting.svg" width="52" alt="Scouting"></picture><br><b>Scouting</b><br><code>scheduled</code></td><td align="center"><picture><source media="(prefers-color-scheme: dark)" srcset="../../assets/probe-analysis-dark.svg"><img src="../../assets/probe-analysis.svg" width="52" alt="Analysis"></picture><br><b>Analysis</b><br><code>/analyze</code></td></tr>
<tr><td align="center"><picture><source media="(prefers-color-scheme: dark)" srcset="../../assets/probe-comparison-dark.svg"><img src="../../assets/probe-comparison.svg" width="52" alt="Comparison"></picture><br><b>Comparison</b><br><code>/compare</code></td><td align="center"><picture><source media="(prefers-color-scheme: dark)" srcset="../../assets/probe-presentation-dark.svg"><img src="../../assets/probe-presentation.svg" width="52" alt="Presentation"></picture><br><b>Presentation</b><br><code>/present</code></td></tr>
</table>

<picture><source media="(prefers-color-scheme: dark)" srcset="../../assets/human-dark.svg"><img src="../../assets/human.svg" width="22" align="absmiddle" alt=""></picture> <code>/ideate</code> — you + the corpus, in chat

</td>
</tr>
</table>

<div align="center">

<a href="https://jonghochoi.github.io/probe/">
  <picture><source media="(prefers-color-scheme: dark)" srcset="../../assets/reading-site-dark.svg"><img src="../../assets/reading-site.svg" width="560" alt="Read the analyses — jonghochoi.github.io/probe"></picture>
</a>

</div>

## Three rules

1. **`/analyze` first.** Compare and present read the rewrite, never the PDF.
2. **No arXiv HTML → skipped.** Nothing is written from an abstract.
3. **`context/` is read-only** to the agent. It proposes; you decide.

## Why

| <picture><source media="(prefers-color-scheme: dark)" srcset="../../assets/probe-lost-dark.svg"><img src="../../assets/probe-lost.svg" width="22" align="absmiddle" alt=""></picture> Without | <picture><source media="(prefers-color-scheme: dark)" srcset="../../assets/probe-locked-dark.svg"><img src="../../assets/probe-locked.svg" width="22" align="absmiddle" alt=""></picture> With PROBE |
|---|---|
| 50–100 papers/day, none remembered | 3–5 per run, scored against your open decisions |
| Prior art rediscovered the hard way | The citation graph surfaces it first |
| "I'll read it properly later" | A Korean page you finish in a sitting |

## How it flows

<div align="center">

<picture><source media="(prefers-color-scheme: dark)" srcset="../../assets/flow-dark.svg"><img src="../../assets/flow.svg" width="880" alt="PROBE pipeline — context/ into the run, arXiv narrowed to 3–5 papers, out to scouting and on-demand pages"></picture>

</div>

<div align="center">

[![arXiv API](https://img.shields.io/badge/arXiv-API-B06749?logo=arxiv&logoColor=white&labelColor=1F1611)](https://info.arxiv.org/help/api/index.html)
[![Semantic Scholar](https://img.shields.io/badge/Semantic%20Scholar-Graph%20API-B06749?labelColor=1F1611)](https://api.semanticscholar.org/)

</div>
