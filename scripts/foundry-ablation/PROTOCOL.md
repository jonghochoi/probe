# Foundry-quality ablation harness

A repeatable experiment for attributing *why* a PROBE `/implement-design` mapping is or
isn't as good as a reference implementation. Run it across many papers and
accumulate samples; the ledger aggregates a verdict over time.

## The question

PROBE reaches code through a mediated pipeline — paper → `analysis/<id>/analysis.md`
(deep-dive) → `analysis/<id>/design.md` (Layer-1, deliberately vendor-agnostic,
context-reduced) → `/implement-design` (maps onto the vendored base). A direct setup
(paper + repo handed straight to a coder) skips that filtering. When the
mediated output looks weaker, two causes are confounded:

- **H_context** — the analysis→design filtering drops *load-bearing* detail
  that exists upstream, so `/implement-design` fills paper-silent gaps blindly.
- **H_verify** — the snapshot foundry gives no execution feedback (only
  `git apply --check`), so shape/signature/form defects survive. (Largely
  addressed by the `§🧬` execution tier — see `scripts/ensure-foundry-runtime.sh`
  and `validation.md §🧬`.)
- **H_null** — the perceived gap is not a *correctness* gap at all but
  reasoning-richness / form, and the mediated pipeline produces
  behaviourally-equivalent code.

This harness isolates **H_context** with an a-axis ablation, and lets you log
the H_verify / form signals alongside so a per-paper picture accumulates.

## Method — a-axis ablation (the part that needs LLM agents)

For a paper with both `analysis/<id>/design.md` and `analysis/<id>/analysis.md`, run two
**isolated** foundry-mapping agents that differ ONLY in their input corpus:

- **a1 — design-only**: sees `analysis/<id>/design.md` + the foundry base
  (`vendor/<foundry>/policies/<base>/`). Nothing else.
- **a2 — context-rich**: sees the Design + the full `analysis/<id>/analysis.md` + the
  base, and may fetch the actual paper.

Both must be forbidden from reading the existing impl/validate-impl artifacts
(`analysis/<id>/impl/**`, `analysis/<id>/validation/**`) and any reference repo
(e.g. a fork that already implements the paper) — those leak the answer.

Each agent reports, for the contested "decision points" (the underspecified
hyperparameters / architecture choices), `value` + `[SPECIFIED: where]` or
`[ASSUMED: reason]`. `prep_ablation.py <id>` prints the two ready-to-paste,
id-filled agent prompts so every sample uses identical wording.

> The agents are the measurement instrument; a shell script cannot spawn them.
> The orchestrating model spawns them per the prompts `prep_ablation.py` emits,
> then records the outcome with `ablation_ledger.py add`.

## Metric

Per decision point, compare a1 vs a2:

- **status upgrade** (`a1=ASSUMED` → `a2=SPECIFIED`) — richer context *recovered*
  a spec the design had dropped. This is the H_context signature.
- **value shift** (`a1_value ≠ a2_value`, no upgrade) — context nudged an
  otherwise-arbitrary choice; weak/ambiguous.
- **neutral** (identical value + status) — context changed nothing.

Per-paper verdict:

- `context_pins`  — any status upgrade → **H_context supported** for this paper.
- `context_shifts` — value shift without upgrade → ambiguous, investigate.
- `context_neutral` — all neutral → **H_context refuted** for this paper.

`ablation_ledger.py report` aggregates these across all logged papers, plus the
`exec_verdict` (§🧬 pass/fail/skipped) and `form` (in-place vs subclass-seam)
columns so the H_verify / form signal accumulates in the same table.

## Workflow

```bash
# 1. emit the two controlled agent prompts for a paper
python3 scripts/foundry-ablation/prep_ablation.py 2511.00139

# 2. (orchestrating model) spawn two isolated agents with those exact prompts,
#    collect their 4 decision-point answers.

# 3. record the sample (JSON on stdin or a file — schema in ablation_ledger.py)
python3 scripts/foundry-ablation/ablation_ledger.py add sample.json

# 4. aggregate across everything logged so far
python3 scripts/foundry-ablation/ablation_ledger.py report
```

The ledger (`ledger.jsonl`) is committed so samples persist across checkouts.
