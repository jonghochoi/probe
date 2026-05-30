# eval/

probe's soundness **calibration harness** — a programmatic measurement
tool, ported and adapted from the sibling benchmark
[`SoundnessBench`](https://github.com/jonghochoi/soundnessbench)
(`rigorbench/`).

## Why this exists

probe's `scouting/` and `analysis/` tracks are themselves LLM rigor
judges: they score each paper and recommend pipeline changes. But probe
has no way to check whether those judgments are *calibrated*.
SoundnessBench's finding is the risk: under neutral prompting, LLM judges
suffer an **optimism bias** — they over-rate methodologically unsound work
as sound. `eval/` measures probe's soundness prompt against a
human-labelled gold set so the judgment quality is a number, not a vibe,
and A/B-tests the **neutral vs. skeptical** prompt to quantify how much
the skeptical gate (the `🩺 건전성 판정`, see `docs/STYLE.md` §5-2)
actually reduces that bias.

This is a calibration tool for the *prompt*, not the scout's run path.
It never calls arXiv or writes a report; the production scout still runs
through the Claude Code agent.

## Layout

| Path | Role |
|---|---|
| `judge/buckets.py` | low/high label normalization (ported verbatim) |
| `judge/metrics.py` | accuracy + Cohen's kappa (ported) + `optimism_metrics` (false-high rate, new) |
| `judge/client.py` | multi-provider chat clients + offline `RandomBaseline` |
| `judge/prompts.py` | load a prompt variant, build chat messages |
| `judge/run.py` | gold loading, robust JSON parse, scoring loop, `compare_prompts` A/B |
| `prompts/soundness_neutral.md` | neutral rigor prompt (A/B baseline) |
| `prompts/soundness_skeptical.md` | aggressive "default to low" prompt |
| `data/gold.jsonl` | small robotics gold set (hypothesis + experiment + low/high) |
| `config.yaml` | provider / model / hyperparameters |
| `requirements.txt` | runtime deps (openai / anthropic / pyyaml / dotenv) |

CLI entry point: `scripts/run-soundness-eval.py`.

## Gold set schema

One JSON object per line (the SoundnessBench schema, so the same runner
scores either source):

```json
{"pair_id": "probe_gold_001", "hypothesis": "...", "experiment": "...", "rigor_bucket": "high", "soundness_score": 0.85}
```

`rigor_bucket` (`low`|`high`) is the human label scored against;
`soundness_score` is optional metadata.

## Usage

```bash
pip install -r eval/requirements.txt

# offline smoke run — no API key, chance-level reference:
python scripts/run-soundness-eval.py --provider random --prompt compare

# calibrate the skeptical prompt (needs OPENAI_API_KEY or another provider):
python scripts/run-soundness-eval.py --prompt skeptical --output eval/results/skeptical.json

# A/B neutral vs skeptical and report the false-high reduction:
python scripts/run-soundness-eval.py --prompt compare --output-dir eval/results
```

### Bootstrap against SoundnessBench

Before a large robotics gold set exists, point `--gold` at the sibling
benchmark's 1,099 labelled pairs to calibrate the prompt immediately:

```bash
python scripts/run-soundness-eval.py --prompt compare \
    --gold ../SoundnessBench/data/soundnessbench.jsonl \
    --output-dir eval/results --limit 200
```

## What it reports

- `rigor_bucket_accuracy` — exact-match agreement with the gold label.
- `rigor_bucket_kappa` — Cohen's kappa (chance-corrected agreement).
- `false_high_rate` — among gold-`low` items, the fraction predicted
  `high`. This is the optimism bias; the skeptical prompt should lower it.
- `compare` mode adds `false_high_rate_reduction` (neutral − skeptical)
  and a one-line verdict.

Calibration outputs under `eval/results/*.json` are gitignored; only the
harness, prompts, and gold set are versioned.
