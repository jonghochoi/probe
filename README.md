<div align="center">

# 🛸 PROBE · Research Scout for Dexterous Manipulation

<img src="docs/LOGO.png" alt="NEXUS Logo" width="600">

**Stop drowning in arXiv. Start changing what you train next week.**

*Author watch · Citation-graph expansion · Anti-topic filtering · Weekly decision-grade Scouting Reports*

---

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)](https://python.org)
[![Claude](https://img.shields.io/badge/Claude-Agent-D97757?logo=anthropic&logoColor=white)](https://claude.com/claude-code)
[![arXiv API](https://img.shields.io/badge/arXiv-API-B31B1B?logo=arxiv&logoColor=white)](https://info.arxiv.org/help/api/index.html)
[![Semantic Scholar](https://img.shields.io/badge/Semantic%20Scholar-Graph%20API-1857B6)](https://api.semanticscholar.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

📖 팀 온보딩 한글 문서: [`docs/INTRO_KO.md`](docs/INTRO_KO.md)

</div>

---

## 📌 Why PROBE?

Running dexterous manipulation research is a full-time job. You tune reward curves, debug tactile pipelines, chase Sim-to-Real gaps — and somewhere between the hardware and the gradient logs, arXiv slips off the map.

The field does not wait. **50–100 new papers land on `cs.RO` + `cs.LG` every day.** Of those, maybe 3–5 per week actually touch hand-centric dexterous manipulation plus Sim-to-Real. That's a 3–5% signal rate in a firehose, and the cost of missing the right paper is re-solving a problem someone already published — the most expensive mistake a researcher can make.

**PROBE finds those 3–5 for you.**

But it does not stop at "here are some interesting papers." It asks the only question that matters:

> *"If this paper is right, what do I change in the Isaac Lab pipeline next week?"*

Summaries are cheap. PROBE produces **decision material**.

| Without PROBE | With PROBE |
|---|---|
| "I'll check arXiv this weekend" → never happens | Weekly Scouting Report lands in your repo |
| 50–100 papers/day → skim titles, remember none | 3–5 papers/week → scored, tied to your open questions |
| Survey mode: "this is interesting" | Decision mode: "change DR range on object mass to [0.5, 2.0] kg" |
| Re-discovering already-published solutions | Citation graph surfaces the prior art before you waste the week |
| Echo chamber — same authors, same methods | Monthly cross-pollination picks from adjacent fields |

---

## 📁 Repository Structure

```
probe/
│
├── CLAUDE.md                       # Contributor rules — commit & doc style
├── README.md                       # ← you are here
├── brand.py                        # ASCII art, sigils, color constants
│
├── context/                        # Static input — human-maintained
│   ├── MASTER.md                   #   single source of truth (P1–P5):
│   │                               #   Identity, Pillars, Decision Log
│   │                               #   (D1–D26), Tracked Literature (5 × 8),
│   │                               #   Competitor / Researchers / Anti-topics
│   └── P{1..4}.md                  #   per-pillar history-free extracts —
│                                   #   identical §1–§9 skeleton; the
│                                   #   pipeline reads one, never the full doc
│
├── .claude/
│   ├── prompts/                    # Externalized agent prompts
│   │   ├── scouting-P{1..4}.md     #   weekly scout, one per pillar
│   │   ├── synthesis-P{1..4}.md    #   monthly synthesis brief, per pillar
│   │   └── paper-analysis.md       #   on-demand single-paper deep-dive
│   └── commands/                   # Slash commands (on-demand)
│       └── analyze-paper.md        #   /analyze-paper <id|url|pdf>
│
├── scouting/                       # Dynamic output — agent-generated (weekly)
│   ├── README.md                   #   pipeline summary
│   ├── _TEMPLATE.md                #   Scouting Report form
│   └── YYYY-MM-DD-P#.md            #   Korean reports — one per run (Mon/Thu),
│                                   #   one per pillar (P1–P4)
│
├── synthesis/                      # Monthly synthesis output
│   ├── README.md                   #   pipeline summary
│   └── P{1..4}_BRIEF.md            #   living per-pillar narrative (regen)
│
├── analysis/                       # Paper deep-dive output (on-demand)
│   ├── README.md                   #   purpose + filename convention
│   ├── _TEMPLATE.md                #   Korean deep-dive form
│   └── <arxiv-id>.md               #   single Korean analysis (regen)
│
└── docs/
    ├── INTRO_KO.md                 # Korean onboarding + operations manual
    ├── STYLE_GUIDE.md              # Output formatting rules (emoji, links,
    │                               #   Korean authoring) — SSOT for reports
    └── LOGO.png                    # Project logo
```

> **Pillars**: P1 Heterogeneous Body/Hand Action Expert · P2 Structured Input-Modality Binding · P3 Hand-level System0 · P4 VLM Pretraining Preservation · P5 Task Definition & Falsifiable Evaluation — canonical definitions in [`context/MASTER.md`](context/MASTER.md) §5.
>
> **Full doc vs. per-pillar extract**: `context/MASTER.md` is the single source of truth (all five pillars, D1–D26). Each `context/P#.md` is a narrowed, history-free extract of one pillar with an identical §1–§9 skeleton; the cloud scouting/synthesis routines read **one extract** to keep agent context lean and pillar-focused. Edit the full doc; regenerate extracts from it — never the reverse.

### Core principle: static vs. dynamic, never mixed

`context/MASTER.md` and `scouting/` exist for one reason: to keep the agent's context lean.

- **Static** (`context/MASTER.md`) changes monthly at most. The agent *reads* it, never writes.
- **Dynamic** (`scouting/`) is append-only. Each run produces one file per pillar (`YYYY-MM-DD-P#.md`). The agent only reads that pillar's **last ~2 weeks** when generating a new report.

Shove everything into one file and within six weeks the context bloats, the agent re-recommends last month's papers, and the pinned literature drifts into a mess.

---

## 🧭 The Pipeline

```
              ┌──────────────────────────────┐
              │  context/MASTER.md           │  static · human-owned
              │  • Identity & Purpose        │
              │  • Pillars (P1–P5)           │
              │  • Decision Log (D1–D26)     │
              │  • Tracked Literature (5 × 8)│
              │  • Competitor Monitoring     │
              │  • Researchers to Follow     │
              │  • Anti-topics               │
              └──────────────┬───────────────┘
                             │ read-only (every run)
                             ▼
              ┌──────────────────────────────┐
              │           P R O B E          │
              │        (Claude Agent)        │
              │                              │
              │  1. Author Watch             │  ← highest signal
              │  2. Citation-Graph Expansion │  ← semantic, not keyword
              │  3. Keyword Sweep            │  ← noisy, last resort
              │  4. Competitor Monitoring    │  ← §10 watch list
              │                              │
              │  Score every candidate on:   │
              │    · P# / D# relevance       │
              │    · Identity align/tension  │
              │    · Novelty vs. tracked     │
              │    · Reproducibility         │
              │    · Sim2Real evidence       │
              └──────────────┬───────────────┘
                             │ writes
                             ▼
              ┌──────────────────────────────┐
              │  scouting/YYYY-MM-DD-P#.md   │  Scouting Report
              │                              │
              │  Top 3–5 papers only         │
              │    · Connects to P#/D#       │
              │    · What's genuinely new    │
              │    · Decision implication    │  ← the point
              │    · Failure mode to probe   │  ← the point
              └──────────────┬───────────────┘
                             │ informs
                             ▼
              ┌──────────────────────────────┐
              │           Human              │
              │                              │
              │  · Read, judge, discard      │
              │  · Update context (monthly)  │
              │  · Log feedback  (monthly)   │
              └──────────────────────────────┘
```

---

## 🧑‍🔬 Division of Labor

PROBE is a scout. It does not fight. The human still owns every judgement call.

| Human owns | Agent owns |
|---|---|
| **Direction** — is the Identity claim still load-bearing? Is P1 really the most important Pillar? | **Author watch** — last 14 days of submissions from §9 researchers |
| **Decision Log curation** — if a paper shakes a v1 default or trips a deferred trigger, update D# | **Citation-graph expansion** — semantic neighbors of §8 tracked literature (5 × 8) |
| **Evaluation protocol** — D25's 4-contribution falsifier thresholds; without these, no report matters | **Anti-topic filtering** — drop mobile-manip, locomotion, parallel grippers, router-MoE (DexReMoE excepted) |
| **CP-driven context update** — Tracked Literature, Decision Log, Competitor monitoring at every CP | **Scoring** — P#/D# fit, Identity alignment, novelty, reproducibility, Sim2Real evidence |
| **Feedback loop** — did any scouted paper change an experiment or a Decision? | **Cross-pollination** — forced monthly pick from §12 rotation |
| **Discarding** — most papers won't matter, that's fine | **Competitor monitoring** — §10 watch list (DexReMoE / CATFA / SaTA / Sharpa VTLA / π lineage) |

The agent **never** edits `context/MASTER.md`. It can *propose* changes in the report. The human decides.

---

## ⚡ Quick Start

```bash
git clone https://github.com/jonghochoi/probe.git
cd probe
```

1. Open `context/MASTER.md` and fill in **your** Identity, Pillars, Decision Log defaults, Tracked Literature, and Competitor watch list. Shipping defaults are a Sharpa Hand / Isaac Lab template — useful as an example, not a universal config.
2. Decide how you want to run the agent — manually in a Claude.ai conversation, or fully scheduled via Claude Code Routines. See [Agent Setup Guide](#-agent-setup-guide) below.
3. Generate your first Scouting Report. Review it ruthlessly. Tune the prompt. Commit.

> 💡 **Do not automate on day one.** Run manually for 1–2 weeks until the report quality is where you want it. Bad prompt + full automation = weekly garbage generated on schedule.

---

## 🤖 Agent Setup Guide

This section walks you from zero to a scheduled, self-running PROBE agent. Three stages, each a concrete upgrade over the last.

```
Stage 1 (Week 1–2)  Manual      — paste context into Claude.ai, iterate on the prompt
Stage 2 (Week 3–4)  Semi-auto   — Claude desktop Scheduled Tasks (laptop must be open)
Stage 3 (Week 5+)   Full agent  — Claude Code Routines (cloud-scheduled, commits via PR)
```

You do **not** skip stages. The prompt that survives Stage 1 is the prompt you deploy in Stage 3.

---

### 🪜 Stage 1 — Manual run (Week 1–2)

Goal: produce two consecutive Scouting Reports that you'd actually read. Nothing is automated yet.

1. Open a new [Claude.ai](https://claude.ai) conversation with **Claude Sonnet** or **Opus**.
2. Upload (or paste) `context/MASTER.md` as a project file.
3. Paste the **Scouting Prompt** (see below). Fill in the run date and pillar.
4. Read the output against `scouting/_TEMPLATE.md`. If it fails the template, the prompt is the problem — not the agent.
5. Save the output as `scouting/YYYY-MM-DD-P#.md`, commit, repeat on the next run (Mon/Thu).

<details>
<summary><b>📋 Scouting Prompt (copy-paste)</b></summary>

```
You are PROBE — a research scout for hand-centric dexterous
manipulation.

CONTEXT (read-only):
- context/MASTER.md  (attached)
- scouting/<this pillar's last ~2 weeks>.md  (attached)
- docs/STYLE_GUIDE.md  (attached) — formatting, emoji system, Korean authoring rules

TASK:
Produce a Scouting Report for <YYYY-MM-DD> · Pillar P#.
This routine runs twice a week — every Monday and Thursday.
Each run produces ONE Korean output file:
  `scouting/YYYY-MM-DD-P#.md` — Korean (use the run date)

PROCESS (in this order):
1. Author Watch — check last 14 days of arXiv submissions from
   every researcher listed in Section 9 of context/MASTER.md.
2. Citation-Graph Expansion — for each pinned paper in Section 8
   (Tracked Literature; 5 Pillars × 8 papers = 40 anchors), list
   new papers (past 8 weeks) that cite it. Rank by semantic
   relevance to the Pillars (Section 5) and active Decisions
   (Section 6), not keyword overlap.
3. Keyword Sweep — cs.RO + cs.LG, last 14 days, filter against
   the Anti-topics list (Section 7). This is the noisiest source;
   weight it lowest.

For every candidate paper, score on a 0–3 scale:
  · Relevance     — which P# / D# does it touch?
  · Novelty       — genuinely new, or a delta over tracked work?
  · Reproducibility — code / data / hardware details?
  · Sim2Real      — real-robot evidence, or sim-only?

---

OUTPUT — Korean report (`YYYY-MM-DD-P#.md`)

Write the report directly in Korean, following scouting/_TEMPLATE.md
exactly. Top 3–5 papers only. Apply docs/STYLE_GUIDE.md §4 (Korean
authoring rules): all prose is formal Korean (합니다/됩니다 체), while
paper titles, config / code names, formulas, P#/D#/CP# tags, arXiv
links, emojis and `<a id="ref-…">` anchors stay verbatim.

### Emoji rules (docs/STYLE_GUIDE.md §2)
Apply emojis to section and subsection headers only — never inside body text.

Section-level (##):
  📋  Scout Methodology
  🥇  Paper N — PRIORITY ★★★
  🥈  Paper N — PRIORITY ★★
  🥉  Paper N — PRIORITY ★
  🌱  Paper N — CROSS-POLLINATION (adjacent field)
  📊  Scoring Summary
  🚫  Candidate Papers That Did Not Pass Filter
  💡  Context Suggestions
  🔄  Run-over-Run Synthesis

Subsection-level (###), same across all papers:
  🎯  (a) P# / D# touched
  ✨  (b) What is genuinely new
  ⚙️  (c) Decision implication
  ⚠️  (d) Failure mode to probe first
  📌  All sub-sections within Context Suggestions

### Link rules (docs/STYLE_GUIDE.md §3)
Every paper entry must include a direct link:
  - arXiv → [arXiv:XXXX.XXXXX](https://arxiv.org/abs/XXXX.XXXXX)
  - DOI   → [DOI](https://doi.org/...)
  - None  → [no public link]
Links appear in the paper header, Scoring Summary table, Candidate Papers
table, and inline in Context Suggestions. Do not fabricate arXiv IDs.

### Per-paper required sections
For each paper, state:
  (a) which P# / D# it touches,
  (b) what is *genuinely* new,
  (c) decision implication — what changes in MY Isaac Lab pipeline
      next week if this paper is right? Be concrete (config name,
      hyperparameter, specific metric). Vague is failure.
  (d) failure mode to probe first.

---

RULES:
- Do not recommend any paper already covered in this pillar's recent
  reports — the last ~2 weeks (~4 files `scouting/YYYY-MM-DD-P#.md`).
- Do not edit context/MASTER.md. If a pinned paper should be replaced,
  write the suggestion under 💡 Context Suggestions.
- If fewer than 3 papers pass score >= 2, say so. Do not pad.
- Once per month, force-include one paper from an adjacent field
  per Section 12 of context/MASTER.md (Cross-pollination Budget).
- Every paper link must be verified to resolve correctly before
  inclusion. Do not fabricate arXiv IDs.
```

</details>

---

### 🧩 Stage 2 — Semi-auto (Week 3–4)

Goal: the agent runs on a schedule, but tools/MCP are not yet wired. You're letting Claude re-generate reports automatically, still using its built-in web search for retrieval.

Use **Claude Desktop → Scheduled Tasks**:

1. Open Claude Desktop → Settings → Scheduled Tasks.
2. Create task: `PROBE scout`.
3. Trigger: every Monday and Thursday 09:00 Asia/Seoul.
4. Prompt: the same Scouting Prompt from Stage 1.
5. Attach `context/MASTER.md` + this pillar's last two `scouting/*-P#.md` files.
6. Action: save the result to `scouting/YYYY-MM-DD-P#.md` (copy manually, or use the desktop's file-export hook).

Limitation: your laptop has to be awake and Claude Desktop has to be running. Good enough for a month; not good enough forever.

---

### 🛰️ Stage 3 — Full agent via Claude Code Routines (Week 5+)

This is the endgame: cloud-scheduled, commits its own reports via pull request. No laptop, no reminders, no "did I run PROBE this week?"

Only **three** things change versus Stage 1/2:

- **Execution location** — your laptop → the cloud (runs Mon & Thu 09:00 even with the laptop off).
- **Retrieval** — Claude's built-in web search → direct `curl` calls to public REST APIs (arXiv + Semantic Scholar Graph). Same data sources, better citation accuracy and reproducibility. **No MCP server is involved** — cloud routine sessions cannot reach a local MCP server, so retrieval is plain `curl`.
- **Output** — manual copy → the prompt itself commits & pushes the report file, then the RemoteTrigger/harness opens the GitHub PR from that branch (commit history *is* the research log).

The repo's durable asset is the **prompt** (`.claude/prompts/scouting-P{1..4}.md`), not a config file. There is **no `.claude/routines/*.yaml`** auto-registration and no `claude routine register` CLI — scheduling is created through the **RemoteTrigger form** at [claude.ai/code/routines](https://claude.ai/code/routines) (or the `/schedule` CLI). You do not write new logic here; you understand and verify the prompt, then paste it into the form.

> This guide uses **P1** as the worked example. For another pillar, swap `scouting-P1.md` → `scouting-P{2,3,4}.md`, `context/P1.md` → `context/P{2,3,4}.md`, output `synthesis/P1_BRIEF.md` → `synthesis/P{2,3,4}_BRIEF.md`, and register one routine per pillar.

**Prerequisites**

| Item | Note |
|---|---|
| Claude Code Pro plan | Routines need cloud execution. The Pro daily cap easily covers 2 runs/week. |
| GitHub repo connected to Claude Code | Required for PR output (this repo). |
| Outbound network policy | The routine's cloud environment must allow `export.arxiv.org` and `api.semanticscholar.org` — see Step 1. |
| `SEMANTIC_SCHOLAR_API_KEY` | Optional. Set as an environment variable (there is no secret store). See Step 1. |
| MCP servers | **Not required** — MCP is unreachable from cloud sessions; retrieval is `curl` REST. |

**Step 1 — Environment & network setup**

Retrieval is `curl` against two public APIs (no install needed):

- arXiv — `http://export.arxiv.org/api/query` (Atom XML, no key)
- Semantic Scholar Graph — `https://api.semanticscholar.org/graph/v1` (JSON via `jq`, key optional)

**Network access (the real blocker).** A cloud environment defaults to the **Trusted** network policy, which allows only package registries and GitHub — every other host is rejected with `HTTP 403`, response header `x-deny-reason: host_not_allowed`. The fix is environment-side:

1. [claude.ai/code/routines](https://claude.ai/code/routines) → the routine → **Edit routine**.
2. Click the **cloud icon** (environment name) below the Instructions box.
3. Hover the environment → the **gear/settings icon** → **Update cloud environment**.
4. **Network access → Custom**. In **Allowed domains**, one per line:
   ```
   export.arxiv.org
   arxiv.org
   api.semanticscholar.org
   ```
   Keep **"Also include default list of common package managers"** checked (unchecking it breaks GitHub/registry access).
5. **Save changes.** Network policy changes apply to **new sessions only** — a scheduled routine run is a fresh session, so the next run picks it up.

**`SEMANTIC_SCHOLAR_API_KEY` (optional — and currently, prefer keyless).** Set it in the *same* dialog under **Environment variables**, `.env` format, one line, **no quotes**:

```
SEMANTIC_SCHOLAR_API_KEY=your_key_here
```

Referenced from `curl` as `$SEMANTIC_SCHOLAR_API_KEY`. Important nuance: Semantic Scholar no longer issues new keys to free-domain emails or third-party apps, and an **invalid/unapproved key makes the API return 403 *with* the header while it works keyless (200)**. Unless you already hold a valid approved key, **run keyless** — the prompts omit the header when the variable is empty and already sleep ~3 s between calls with backoff on HTTP 429. There is no dedicated secret store; environment variables are visible to anyone who can edit the environment (fine for a personal-tier key, but be aware).

> **Two different 403s — do not confuse them:**
> - `x-deny-reason: host_not_allowed` → **network layer** (the security proxy). Fix: the Custom allowlist above.
> - Semantic Scholar 403 *only when the key header is sent* → **API auth** (invalid/unapproved key). Fix: drop the key and run keyless.

Verify from a fresh session (keyless → expect `200`; bad key → `403`):

```bash
curl -sS -o /dev/null -w "%{http_code}\n" \
  "https://api.semanticscholar.org/graph/v1/author/search?query=Kevin+Black&fields=name,authorId"
curl -sS -o /dev/null -w "%{http_code}\n" \
  "http://export.arxiv.org/api/query?search_query=cat:cs.RO&max_results=1"
```

**Step 2 — Create the RemoteTrigger routine**

There is no YAML and no `claude routine register`. Create the schedule in the [claude.ai/code/routines](https://claude.ai/code/routines) web form (or the `/schedule` CLI). The fields:

| Form field | Value |
|---|---|
| Name | `probe-weekly-scout` |
| Prompt (Instructions) | Paste the full body of `.claude/prompts/scouting-P1.md`. Model selector → **Sonnet**. |
| Repositories | This repo. Output is pushed to a `claude/`-prefixed branch and reviewed via PR. |
| Environment | The Step 1 environment (`SEMANTIC_SCHOLAR_API_KEY` if used + Network access = Custom). |
| Trigger (Schedule) | Mon & Thu 09:00 (the form takes local time → UTC; min interval 1 h). For exact cron, after creating run the CLI `/schedule update` with `0 9 * * 1,4`. |
| Connectors | None — remove all (retrieval is `curl`, not an MCP connector). |
| Permissions | Default (`claude/` branch push) is sufficient — PR output needs no unrestricted push. |

The prompt is the routine body and is **self-contained**: it names its own context files (`context/P1.md`, the last 2 weeks of `scouting/`), the `curl` procedure, output rules and guards. The form has no `context_files` field — the agent clones the repo and reads files per the prompt. The prompt is **pillar-scoped**: it reads the `context/P#.md` extract (skeleton §1–§9; Pillar=§2, Decision Log=§4, Anti-topics=§5, Tracked Literature=§6, Researchers=§7, Competitor=§8, Open Items=§9; no Cross-pollination/Feedback-Loop sections), never the full doc.

**Step 3 — The externalized prompts already exist**

`.claude/prompts/scouting-P{1..4}.md` and `synthesis-P{1..4}.md` are committed — one scouting + one synthesis prompt per pillar. They are the Stage-1 prompt with the **retrieval instructions** swapped from built-in web search to explicit `curl` REST, plus a trailing **commit/push step** so each scheduled run self-persists its report (PR creation stays with the harness):

| Retrieval step | Stage 1/2 | Stage 3 (`curl` REST) |
|---|---|---|
| Author Watch | built-in web search | S2 `/author/search` → `/author/{id}/papers` |
| Citation-Graph expansion | built-in web search | S2 `/paper/arXiv:XXXX.XXXXX/citations` |
| Keyword Sweep / topic-watch | built-in web search | arXiv `export.arxiv.org/api/query` |
| Competitor Monitoring | built-in web search | arXiv query + S2 author lookup |

S2 = Semantic Scholar Graph API (JSON via `jq`); arXiv is Atom XML parsed directly. On failure (non-zero exit, HTTP error, empty body after retries) the prompt records the exact command and HTTP status verbatim under 📋 Scout Methodology and continues with the sources that succeeded — it never fabricates a citation or an arXiv ID. After the report is written the prompt resolves the run date (`TZ=Asia/Seoul`) and runs `git add`/`commit`/`push` for that single report file — the only addition beyond retrieval; PR creation is left to the RemoteTrigger/harness. Everything else (0–3 scoring, "≥2 on every axis", no-padding, no-duplicate-vs-last-2-weeks, the `context/P#.md` never-modify guard) is unchanged from Stage 1.

> The P1-scoped prompt intentionally **drops the monthly Cross-pollination rule** — its source section (full `context/MASTER.md` §12) does not exist in the P1 extract. Do not be surprised diffing it against the Stage-1 prompt above.

**Step 4 — First run & verification**

There is no `--dry-run`. On the routine detail page use **Run now** — it opens a fresh session and executes once. A green run status only means "exited without an infra error", **not** that the prompt succeeded — open the session transcript and inspect the actual output (blocked network requests show up there). Check it with Stage-1 rigor:

- Follows `scouting/_TEMPLATE.md` + `docs/STYLE_GUIDE.md`.
- Both the English and Korean files were produced.
- Every paper link resolves (no fabricated arXiv IDs).
- 📋 Scout Methodology has **no** `curl` 403 / network-block errors (if it does → the Custom allowlist is missing).
- Decision implications are concrete (named Isaac Lab config key / metric, not "tune DR wider").
- The Anti-topics filter actually fired (an empty "did not pass filter" section is suspicious).

If it is unsatisfactory, fix `scouting-P1.md` (or `context/P1.md`) and re-run — do not leave automation on with a bad prompt.

**Step 5 — Monthly human review**

Automation is not the finish line. Once a month fill in three numbers. The P1 extract has no Feedback Loop section, so record this human review in the full multi-pillar `context/MASTER.md` Section 13 (the agent reads only the extract; the feedback record lives in the source of truth).

| Field | Question |
|---|---|
| Papers surfaced | How many did PROBE report this month? |
| Actually read | Of those, how many did *you* read? |
| Influenced a decision | Of those, how many changed an experiment? |

The ratio is PROBE's real KPI. If it trends to zero, the prompt is drifting — not the model; re-check Anti-topics (§5) and Pillar P1 (§2) in `context/P1.md`.

**Bonus — P1 Synthesis Brief**

Where weekly scouting looks *outward* for new papers, this output looks *inward*: it compresses what the already-pinned papers are collectively saying — what props up each Decision and what shakes it — into a prose narrative so you can carry the P1 architecture in your head. Run it as a **second, fully separate** RemoteTrigger routine:

| Form field | Value |
|---|---|
| Name | `probe-p1-synthesis` |
| Prompt | Paste `.claude/prompts/synthesis-P1.md`, model Sonnet |
| Repositories | This repo |
| Environment | Default is fine — **no search → no custom domains needed** |
| Trigger | Monthly (exact cron via `/schedule update` `0 9 1 * *`) |
| Connectors | None |
| Input | `context/P1.md` §4 (D1–D7) + §6 (pinned papers) only |
| Output | `synthesis/P1_BRIEF.md` — Korean, overwritten each run (living snapshot) |
| Retrieval | **None** — no MCP/web/`curl`, pure static-file compression (zero citation-fabrication risk) |

When the pinned literature (§6) changes, don't wait for the monthly run — hit **Run now** to refresh the brief. Its value is entirely in being short and honest; if it grows long it is dead.

**Bonus — On-demand paper deep-dive (`/analyze-paper`)**

Scouting finds new papers *outward*; synthesis re-states the pinned set; this third mode reads **one specific paper** the human already cares about (typically a pinned/anchor paper from `context/MASTER.md` §8 that you have not fully internalized) and leaves a Korean deep-dive. It is **not a scheduled routine** — no RemoteTrigger. It is an on-demand slash command you invoke when you need it, in a local or web session.

| Item | Value |
|---|---|
| Invoke | `/analyze-paper <arXiv id \| arXiv url \| pdf url>` |
| Slash command | `.claude/commands/analyze-paper.md` (thin wrapper) |
| Canonical prompt | `.claude/prompts/paper-analysis.md` (single source) |
| Input context | full `context/MASTER.md`, read-only (a paper spans multiple pillars, so the full doc, not an extract) |
| Body acquisition | `curl`, full-text-preferred: `arxiv.org/abs` → `/html` → ar5iv → abstract-only, with the level recorded in the document header |
| Output | `analysis/<arxiv-id>.md` — single Korean document, overwritten each run |
| Structure | (A) formatted neutral summary + (B) `context/MASTER.md`-anchored decision-grade implications |
| Retrieval | full-text `curl` only (no Semantic Scholar / MCP) |

Network note: the slash command's full-text fetch needs the session environment to allow `arxiv.org` / `ar5iv.labs.arxiv.org` / `export.arxiv.org` (same Custom-allowlist requirement as Step 1). When full text cannot be fetched (arXiv HTML exists only for LaTeX-source papers ~2023-12+; PDF-only/complex-macro/withdrawn papers; non-arXiv paywalls; policy block; 429), the failure is recorded verbatim in the header and part (B) is marked **(본문 미확보 — 잠정)**. Format/emoji/term rules live in `docs/STYLE_GUIDE.md` §5.

---

### 🧰 Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Papers recommended are in your Anti-topics list | Anti-topics are too vague | Rewrite `context/P#.md` §5 with concrete exclusions (e.g. "any paper whose primary task is locomotion") |
| "Decision implication" is generic ("tune DR wider") | Prompt isn't forcing specificity | Add to `scouting-P#.md`: "name the exact Isaac Lab config key and range" |
| Same paper recommended two weeks in a row | Agent skipped the last-2-weeks context | Confirm the prompt's read-only "last 2 weeks of `scouting/`" reference is intact and those files exist |
| `claude routine register` / a `.claude/routines/*.yaml` does nothing | That is not the execution mechanism | Register via the RemoteTrigger form ([claude.ai/code/routines](https://claude.ai/code/routines)) — Step 2/4 |
| Agent silently edits `context/P#.md` | Prompt guard missing | Re-add the hard "never modify `context/P#.md`" guard (currently present in `scouting-P#.md` — do not remove it) |
| Routine ran but PR is empty / every `curl` fails | Outbound network policy blocking the API domains | Set Network access = Custom and allow `export.arxiv.org` / `arxiv.org` / `api.semanticscholar.org`; check the verbatim error under 📋 Scout Methodology |
| Citation graph only partially filled / frequent HTTP 429 | Semantic Scholar rate-limited | Run keyless (recommended) or add a *valid approved* key; keep the ~3 s sleep + backoff. See the two-403 note in Step 1 |
| Semantic Scholar returns 403 even with a key set | Invalid/unapproved key (free-domain emails no longer get keys) | Remove the `SEMANTIC_SCHOLAR_API_KEY` env var and run keyless (works at 200) |
| `scouting-P#.md` tries to call MCP tools | Stale prompt (MCP residue) | Confirm the RETRIEVAL section is `curl` REST — MCP is unreachable from cloud sessions |

---

## 🧱 Agent Stack

| Component | Technology |
|---|---|
| **Agent engine** | Claude (Sonnet 4.6 / Opus 4.7) via Claude Code Routines |
| **Scheduler** | RemoteTrigger ([claude.ai/code/routines](https://claude.ai/code/routines)) — cloud cron, GitHub PR output |
| **Paper search** | arXiv REST API (`export.arxiv.org/api/query`, Atom XML) via `curl` |
| **Citation graph** | Semantic Scholar Graph API (`api.semanticscholar.org/graph/v1`, JSON via `jq`) — optional `SEMANTIC_SCHOLAR_API_KEY` |
| **Prompts** | `.claude/prompts/scouting-P{1..4}.md` (weekly) + `synthesis-P{1..4}.md` (monthly) + `paper-analysis.md` (on-demand) |
| **Output** | GitHub PR — commit history *is* the research log |
| **Context** | `context/P{1..4}.md` (static, human, per-pillar) + `scouting/` (dynamic, agent) + `synthesis/P{1..4}_BRIEF.md` (monthly snapshot) |

---

## 📡 Signals That PROBE Is Actually Working

- At least **one paper per week** triggers a concrete change in your experiment design or in a Decision Log entry.
- The Anti-topics filter catches **≥ 10 papers/week** — that's the healthy exclusion rate.
- The agent reports "no paper scored ≥ 2 this week" without padding.
- Every Checkpoint (CP1–CP5), you can point at a line in `context/MASTER.md` Decision Log that moved because of a scouted paper.

If none of those are true after a month, the prompt is drifting or the Tracked Literature is stale. Fix the static context first, the prompt second. The model is almost never the problem.

---

## 🔗 Related Projects

| Project | Role |
|---|---|
| **[nexus](https://github.com/jonghochoi/nexus)** | Centralized RL experiment hub — MLflow + TensorBoard dual logging |
| **[observer](https://github.com/jonghochoi/observer)** | Automated evaluation pipeline — multi-view recording, failure-mode classification, checkpoint ranking |
| **probe** *(you are here)* | Research scouting — the upstream that decides *what is worth experimenting on at all* |

> `probe` → `nexus` → `observer` is one research loop.
> PROBE surfaces the idea. NEXUS logs the experiment. OBSERVER judges the policy.

---

## 📚 Further Reading

| Document | Description |
|---|---|
| [`docs/INTRO_KO.md`](docs/INTRO_KO.md) | Korean onboarding — motivation, pipeline, operations manual |
| [`docs/STYLE_GUIDE.md`](docs/STYLE_GUIDE.md) | Output formatting rules — emoji system, link format, Korean authoring |
| [`context/MASTER.md`](context/MASTER.md) | Live research context (single source of truth) — Identity, Pillars, Decision Log, Tracked Literature, Competitor Monitoring |
| `context/P{1..4}.md` | Per-pillar narrowed extracts read by the scouting/synthesis pipeline |
| [`synthesis/README.md`](synthesis/README.md) | Synthesis pipeline summary; `P{1..4}_BRIEF.md` living per-pillar narratives |
| [`analysis/README.md`](analysis/README.md) | On-demand single-paper deep-dive — `/analyze-paper <id\|url\|pdf>` → Korean `analysis/<id>.md` |
| [`scouting/_TEMPLATE.md`](scouting/_TEMPLATE.md) | Weekly Scouting Report template; latest dated reports are the output-quality bar |
| [`brand.py`](brand.py) | ASCII art, sigil, and color constants |

---

<div align="center">

*"It doesn't read papers for you.*
*It scouts which papers change your mind."*

</div>
