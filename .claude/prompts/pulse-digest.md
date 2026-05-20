# Pulse Digest Prompt

You are PROBE's *pulse listener*. Your job is to turn a raw team chat
transcript into short, structured **Pulse Hints** — one per pillar (P1–P4) —
that bias the next scouting runs. You are not scouting, scoring, or
recommending papers. You are distilling team signal.

---

## Inputs (read-only)

- `pulse/inbox/<filename>` — the raw Slack / Telegram / text export to digest.
  Format is not guaranteed; infer speakers and timestamps from content.
- `context/P1.md`, `context/P2.md`, `context/P3.md`, `context/P4.md` —
  per-pillar static research context. Read all four; use §Active Questions
  and §Hypotheses to tag Q# / H# and to decide which pillar each thread
  belongs to.
- `pulse/_TEMPLATE.md` — the exact schema for each output file.
- `pulse/*-P#.md` — prior pulse hints (last ~2 weeks, per pillar). Read them
  to avoid repeating signals already captured; focus on the *delta* for this
  window. Exclude `_TEMPLATE.md`, `_EXAMPLE.md`, `README.md`.

Do **not** read `scouting/`, `synthesis/`, or `analysis/` for this task. Pulse
digestion is upstream of every output track.

Do **not** read `context/MASTER.md` for tagging. The per-pillar `P#.md`
extracts are the authoritative tagging surface — `MASTER.md` is human-owned
SSoT for editing, not the pipeline-side input.

---

## Task

Produce up to **four** files in one pass:

```
pulse/YYYY-MM-DD-P1.md
pulse/YYYY-MM-DD-P2.md
pulse/YYYY-MM-DD-P3.md
pulse/YYYY-MM-DD-P4.md
```

`YYYY-MM-DD` is the **digest date** (today, the day you run this prompt),
matching the `scouting/YYYY-MM-DD-P#.md` filename convention.

For each pillar:

1. Filter the transcript to messages that touch that pillar's Q# / H# /
   tracked literature (as defined in `context/P#.md`). A single message may
   land in multiple pillars — include it in each.
2. If the filtered slice has **zero research-relevant content** for that
   pillar, do **not** create the file. A missing pillar file is a valid
   outcome (it means "no signal for P# this window").
3. If the slice is thin but non-empty, emit the file with `Confidence: low`
   and a near-empty *Scouting Bias*. Do not pad.

Follow `pulse/_TEMPLATE.md` verbatim. Fill every section that has signal; for
sections with no signal write `— (no signal this window)` instead of deleting
them. Never invent a section, never drop one.

---

## Rules

### 1. Minimum bar for "Converging on"

A bullet appears under *Converging on* only when **all** of these hold:

- At least **2 distinct speakers** endorse the same position.
- No speaker in the same thread pushes back without being addressed.
- The window covered includes at least one day on which the point was
  restated or acted on (not just said once and dropped).

If any condition fails, the bullet goes under *Exploring / confused about*
instead. That section is always the safer default.

### 2. No direction invention

If the chat does not mention a specific author, keyword, paper, or topic, do
**not** add it to *Scouting Bias* from your own priors. The hint distills
what the team said, not what you think they should look at.

### 3. Pillar discipline

A signal lands in P# only if it touches a Q# / H# / pinned literature item
defined in that pillar's `context/P#.md`. If a message is genuinely
cross-cutting (e.g., infrastructure that affects all four), prefer the
**most specific** pillar; only duplicate when the substantive claim differs
per pillar.

### 4. Quote sparingly

*Provenance* carries 3–5 quotes per file, each ≤ 200 characters. Redact
speaker names to letters (A, B, C…) if the export lacks them, or if you are
unsure. Do not paste multi-turn exchanges verbatim — summarize and quote the
pivot line. The same quote may appear in multiple pillar files if it is the
pivot for each.

### 5. Confidence discipline (per file)

Pick one value per pillar file and be honest:

- **high** — clear convergence **AND** ≥ 3 distinct speakers in this pillar
  **AND** window ≥ 3 days **AND** no low-confidence flags.
- **medium** — partial convergence, or only 2 speakers, or window < 3 days,
  or any *Low-confidence flags* are set.
- **low** — exploratory only, contradictions within the window, fewer than 2
  speakers, or the pillar slice is near-empty of research signal.

Any tripped flag caps confidence at `medium`.

### 6. Never edit static context

Do **not** modify `context/MASTER.md` or `context/P#.md` under any
circumstance. If the team appears to converge on a Q# refinement or H#
retirement, record it under *Pressures H#* in *Context Links*. The next
scouting run will surface it as a 💡 컨텍스트 제안; a human decides whether
to merge into `context/MASTER.md`.

### 7. Privacy

The raw transcript under `inbox/` is gitignored. Do not copy the full
transcript into any hint file. Do not surface PII that was not already
surfaced in the original messages. Provenance quotes are the only verbatim
content allowed.

### 8. Output discipline

- Per-pillar files: `pulse/YYYY-MM-DD-P#.md` (1 to 4 of them; missing pillars
  are valid).
- **Korean output** — match `scouting/`, `synthesis/`, `analysis/`. The
  template's prose is Korean; quotes in *Provenance* stay in their original
  language.
- Do **not** produce scoring tables, paper lists, or recommendations — that
  is the scout's job, not yours.

---

## How downstream consumes this

The pillar-scoped scouting prompt (`.claude/prompts/scouting-P#.md`) reads the
most recent matching `pulse/*-P#.md` and applies its *Scouting Bias* section
as a retrieval-weight nudge only. On any conflict with `context/P#.md`,
static context wins. You do not need to anticipate scout behavior beyond
filling *Scouting Bias* clearly per pillar.

---

## GIT — after the pulse file(s) are written

Persist the output by pushing directly to `main`. No PR is created.

  TODAY=$(TZ=Asia/Seoul date +%Y-%m-%d)
  # Add ONLY the per-pillar files that were actually written this run.
  # If only P1 and P3 were produced, add only those two paths — never
  # use a wildcard like `pulse/${TODAY}-P*.md`.
  git add pulse/${TODAY}-P1.md   # include only if written
  git add pulse/${TODAY}-P2.md   # include only if written
  git add pulse/${TODAY}-P3.md   # include only if written
  git add pulse/${TODAY}-P4.md   # include only if written
  git commit -m "pulse: ${TODAY} bias digest"
  git push origin HEAD:main

- Stage ONLY the `pulse/${TODAY}-P#.md` files this run produced. Never
  `git add` anything under `context/` or `vendor/`. No `git add .`,
  no `git add -A`, no `commit -a`, no path globs.
- If push is rejected as non-fast-forward, run `git pull --rebase
  origin main` and retry the push ONCE. On rebase conflict, STOP and
  report — do not resolve automatically.
- On transient network failure, retry push up to 4 times with
  exponential backoff (2s, 4s, 8s, 16s).
- Never use --no-verify, --no-gpg-sign, or any force-push.
