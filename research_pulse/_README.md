# research_pulse/ — Chat-to-Scout Bias (PoC, 2 weeks)

> **Status:** proof-of-concept, Tier A only. Not wired to automation.
> **Goal:** test whether team Slack/Telegram chatter, distilled into a short
> hint file, improves the next weekly Scouting Report.

---

## Why this exists

`research_context.md` changes monthly. `research_log/` is produced weekly. But
the actual research thinking — doubt, convergence, direction changes — happens
in chat, daily. `research_pulse/` sits in that gap.

It is a **temporal layer between static context and weekly output**. The agent
may read pulse hints as a *bias nudge*; it may never treat them as
authoritative. Static context always wins on conflict.

---

## Directory layout

```
research_pulse/
├── _README.md               ← you are here
├── _TEMPLATE.md             ← hint schema (agent fills this in)
├── 2026-W17_EXAMPLE.md      ← reference quality bar
├── inbox/                   ← drop raw chat exports here (gitignored)
│   └── _README.md
└── YYYY-WXX.md              ← produced by the digest flow
```

---

## The flow (manual, one pass per week)

1. **Export chat.** From Slack (export a channel as txt/json) or Telegram
   (export chat as HTML/JSON). Save the file under
   `research_pulse/inbox/YYYY-WXX_<channel>.<ext>`. Anything under `inbox/`
   is gitignored — team chat is assumed private.
2. **Run the digest.** Open Claude (desktop, CLI, or claude.ai) with this
   repo attached. Paste `.claude/prompts/pulse-digest.md` and point it at
   the inbox file. Claude produces `research_pulse/YYYY-WXX.md` following
   `_TEMPLATE.md`.
3. **Review the hint.** 60 seconds, human in the loop. Delete the file if the
   signal is wrong; edit the *Scouting Bias* section if it overreaches.
4. **Run the weekly scout** with the Stage-1 prompt, plus the extension
   below. The scout reads the most recent pulse hint and applies its bias.

---

## Extending the Stage-1 Scouting Prompt

Append this block to the Scouting Prompt in the top-level `README.md` (the
copy-paste block under Stage 1):

```
PULSE HINT (optional):
Before running the three retrieval passes, check for the most recent file in
research_pulse/*.md (skip _TEMPLATE.md, _README.md, and any *_EXAMPLE.md).
If one exists:
  - Apply its "Scouting Bias" section as retrieval-weight nudges only.
  - On any conflict with research_context.md, static context wins.
  - Do not treat the hint as authoritative — it may contain premature
    convergence.
  - In Scout Methodology, note which pulse file you used and which biases
    actually changed your retrieval.
If no pulse file is available, proceed normally.
```

That is the only change to the existing scouting pipeline. Nothing else in
`research_log/` or `research_context.md` is modified.

---

## What the hint is NOT

- **Not a context patch.** The agent must never edit `research_context.md`
  based on pulse signal. If the team appears to converge on a Q#/H# change,
  the weekly scout can surface it under `💡 Context Suggestions` — a human
  still decides.
- **Not a paper recommendation.** The hint biases *retrieval*, not selection.
  The scouting scoring rubric is unchanged.
- **Not a transcript log.** The hint contains ≤ 5 short quotes for
  provenance. Full transcripts stay in `inbox/` and are gitignored.

---

## Failure modes to watch

| Failure | Symptom | Mitigation |
|---|---|---|
| **Premature convergence** | Hint declares convergence from one loud voice | `Converging on` requires ≥ 2 speakers, no pushback — enforced in the digest prompt. Human review step is the real safety net. |
| **Context drift** | Pulse bias starts overriding pinned literature | Static context always wins on conflict. Scout methodology must note which biases fired — audit weekly. |
| **Noise amplification** | Off-topic chat turns into spurious bias | `Confidence: low` is a valid, expected output. Skip a week if the window had no research signal. |
| **Privacy leak** | Raw transcript committed to repo | `inbox/*` gitignored by default. Never move transcripts out of `inbox/`. |

---

## PoC success criterion

After 2 weeks: has **at least one** pulse-biased scout produced a paper
(or a rejected candidate) that the team recognizes as a direct match to a
chat-room concern? If yes, iterate on the schema. If no, kill the PoC —
the gap probably isn't worth bridging, or the digest prompt needs rework.
