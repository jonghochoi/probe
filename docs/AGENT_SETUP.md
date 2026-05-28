# 🤖 Agent Setup Guide

This guide takes you from zero to a scheduled, self-running PROBE agent — cloud-scheduled, committing its own reports directly to `main`. No laptop, no reminders, no "did I run PROBE this week?"

> ### Run manually for 1–2 weeks first
>
> Do **not** automate on day one. Open a [Claude.ai](https://claude.ai) conversation with Sonnet or Opus, paste `context/MASTER.md`, run the `.claude/prompts/scouting.md` template by hand (one global find/replace of `<PILLAR>` → `P1`/`P2`/`P3`/`P4` before pasting), and iterate until the report quality is where you want it. The prompt that survives manual iteration is the prompt you deploy as a routine. Bad prompt + full automation = weekly garbage generated on schedule.

---

## Claude Code Routines — full agent

Only **three** things change versus a manual run:

- **Execution location** — your laptop → the cloud (runs Mon & Thu 09:00 even with the laptop off).
- **Retrieval** — Claude's built-in web search → direct `curl` calls to public REST APIs (arXiv + Semantic Scholar Graph). Same data sources, better citation accuracy and reproducibility. **No MCP server is involved** — cloud routine sessions cannot reach a local MCP server, so retrieval is plain `curl`.
- **Output** — manual copy → the prompt itself commits the report file and pushes directly to `main` with `git push origin HEAD:main` (no PR is created; commit history *is* the research log). To prevent concurrent runs from racing on the shared branch, configure the RemoteTrigger to allow at most one active session per environment, and the prompt retains a `git pull --rebase origin main` retry as an in-prompt safety net.

The repo's durable asset is the **prompt** (`.claude/prompts/scouting.md`, shared by P1–P4), not a config file. There is **no `.claude/routines/*.yaml`** auto-registration and no `claude routine register` CLI — scheduling is created through the **RemoteTrigger form** at [claude.ai/code/routines](https://claude.ai/code/routines) (or the `/schedule` CLI). You do not write new logic here; you understand and verify the prompt, then paste it into the form.

> This guide uses **P1** as the worked example. The scouting and synthesis prompts are now single shared templates (`.claude/prompts/scouting.md`, `synthesis.md`); for another pillar, replace every `<PILLAR>` token in the template with `P2`/`P3`/`P4` (one global find/replace before pasting into the form), swap `context/P1.md` → `context/P{2,3,4}.md` and `synthesis/P1_BRIEF.md` → `synthesis/P{2,3,4}_BRIEF.md` in your routine title/notes, and register one routine per pillar.

### Prerequisites

| Item | Note |
|---|---|
| Claude Code Pro plan | Routines need cloud execution. The Pro daily cap easily covers 2 runs/week. |
| GitHub repo connected to Claude Code | Required for PR output (this repo). |
| Outbound network policy | The routine's cloud environment must allow `export.arxiv.org` and `api.semanticscholar.org` — see Step 1. |
| `SEMANTIC_SCHOLAR_API_KEY` | Optional. Set as an environment variable (there is no secret store). See Step 1. |
| MCP servers | **Not required** — MCP is unreachable from cloud sessions; retrieval is `curl` REST. |

### Step 1 — Environment & network setup

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

### Step 2 — Create the RemoteTrigger routine

There is no YAML and no `claude routine register`. Create the schedule in the [claude.ai/code/routines](https://claude.ai/code/routines) web form (or the `/schedule` CLI). The fields:

| Form field | Value |
|---|---|
| Name | `probe-weekly-scout` |
| Prompt (Instructions) | Paste the full body of `.claude/prompts/scouting.md` after replacing every `<PILLAR>` with `P1` (one global find/replace; the file shows the exact instruction at the top). Model selector → **Sonnet**. |
| Repositories | This repo. Output is pushed to a `claude/`-prefixed branch and reviewed via PR. |
| Environment | The Step 1 environment (`SEMANTIC_SCHOLAR_API_KEY` if used + Network access = Custom). |
| Trigger (Schedule) | Mon & Thu 09:00 (the form takes local time → UTC; min interval 1 h). For exact cron, after creating run the CLI `/schedule update` with `0 9 * * 1,4`. |
| Connectors | None — remove all (retrieval is `curl`, not an MCP connector). |
| Permissions | Default (`claude/` branch push) is sufficient — PR output needs no unrestricted push. |

The prompt is the routine body and is **self-contained**: it names its own context files (`context/P1.md`, the last 2 weeks of `scouting/`), the `curl` procedure, output rules and guards. The form has no `context_files` field — the agent clones the repo and reads files per the prompt. The prompt is **pillar-scoped**: it reads the `context/P#.md` extract (skeleton §1–§9; Pillar=§2, Decision Log=§4, Anti-topics=§5, Tracked Literature=§6, Researchers=§7, Competitor=§8, Open Items=§9; no Cross-pollination/Feedback-Loop sections), never the full doc.

### Step 3 — The externalized prompts already exist

`.claude/prompts/scouting.md` and `synthesis.md` are committed — one scouting + one synthesis prompt, each a single shared template for all four pillars (`<PILLAR>` substituted to `P1`/`P2`/`P3`/`P4` once before paste). They are the manual-run prompt with the **retrieval instructions** swapped from built-in web search to explicit `curl` REST, plus a trailing **commit/push step** so each scheduled run self-persists its report (PR creation stays with the harness):

| Retrieval step | Manual run | Routine (`curl` REST) |
|---|---|---|
| Author Watch | built-in web search | S2 `/author/search` → `/author/{id}/papers` |
| Citation-Graph expansion | built-in web search | S2 `/paper/arXiv:XXXX.XXXXX/citations` |
| Keyword Sweep / topic-watch | built-in web search | arXiv `export.arxiv.org/api/query` |
| Competitor Monitoring | built-in web search | arXiv query + S2 author lookup |

S2 = Semantic Scholar Graph API (JSON via `jq`); arXiv is Atom XML parsed directly. On failure (non-zero exit, HTTP error, empty body after retries) the prompt records the exact command and HTTP status verbatim under 📋 Scout Methodology and continues with the sources that succeeded — it never fabricates a citation or an arXiv ID. After the report is written the prompt resolves the run date (`TZ=Asia/Seoul`) and runs `git add` / `commit` / `git push origin HEAD:main` for that single report file — the only addition beyond retrieval; no PR is created. Everything else (0–3 scoring, "≥2 on every axis", no-padding, no-duplicate-vs-last-2-weeks, the `context/P#.md` never-modify guard) is unchanged from the manual run.

> The P1-scoped prompt intentionally **drops the monthly Cross-pollination rule** — its source section (full `context/MASTER.md` §12) does not exist in the P1 extract.

### Step 4 — First run & verification

There is no `--dry-run`. On the routine detail page use **Run now** — it opens a fresh session and executes once. A green run status only means "exited without an infra error", **not** that the prompt succeeded — open the session transcript and inspect the actual output (blocked network requests show up there). Check with the same rigor as a manual run:

- Follows `scouting/_TEMPLATE.md` + `docs/STYLE.md`.
- Both the English and Korean files were produced.
- Every paper link resolves (no fabricated arXiv IDs).
- 📋 Scout Methodology has **no** `curl` 403 / network-block errors (if it does → the Custom allowlist is missing).
- Decision implications are concrete (a specific config key / hyperparameter / metric, not "tune DR wider").
- The Anti-topics filter actually fired (an empty "did not pass filter" section is suspicious).

If it is unsatisfactory, fix `scouting.md` (or `context/P1.md`) and re-run — do not leave automation on with a bad prompt.

### Step 5 — Monthly human review

Automation is not the finish line. Once a month fill in three numbers. The P1 extract has no Feedback Loop section, so record this human review in the full multi-pillar `context/MASTER.md` Section 13 (the agent reads only the extract; the feedback record lives in the source of truth).

| Field | Question |
|---|---|
| Papers surfaced | How many did PROBE report this month? |
| Actually read | Of those, how many did *you* read? |
| Influenced a decision | Of those, how many changed an experiment? |

The ratio is PROBE's real KPI. If it trends to zero, the prompt is drifting — not the model; re-check Anti-topics (§5) and Pillar P1 (§2) in `context/P1.md`.

### Bonus — P1 Synthesis Brief

Where weekly scouting looks *outward* for new papers, this output looks *inward*: it compresses what the already-pinned papers are collectively saying — what props up each Decision and what shakes it — into a prose narrative so you can carry the P1 architecture in your head. Run it as a **second, fully separate** RemoteTrigger routine:

| Form field | Value |
|---|---|
| Name | `probe-p1-synthesis` |
| Prompt | Paste `.claude/prompts/synthesis.md` with every `<PILLAR>` replaced by `P1` (one global find/replace before paste). Model Sonnet. |
| Repositories | This repo |
| Environment | Default is fine — **no search → no custom domains needed** |
| Trigger | Monthly (exact cron via `/schedule update` `0 9 1 * *`) |
| Connectors | None |
| Input | `context/P1.md` §4 (D1–D7) + §6 (pinned papers) only |
| Output | `synthesis/P1_BRIEF.md` — Korean, overwritten each run (living snapshot) |
| Retrieval | **None** — no MCP/web/`curl`, pure static-file compression (zero citation-fabrication risk) |

When the pinned literature (§6) changes, don't wait for the monthly run — hit **Run now** to refresh the brief. Its value is entirely in being short and honest; if it grows long it is dead.

### Bonus — On-demand paper deep-dive (`/analyze-paper` → `/implement` → `/validate`, orchestrated by `/reproduce-paper`)

Scouting finds new papers *outward*; synthesis re-states the pinned set; this third mode reads **one specific paper** the human already cares about (typically a pinned/anchor paper from `context/MASTER.md` §8 that you have not fully internalized) and leaves a Korean deep-dive **plus a vendor-agnostic Layer 1 Design**. From the Design, `/implement` produces a target-codebase patch and `/validate` does static validation. `/reproduce-paper` is the superset — it drives all three through a converging inner loop and is the recommended entry point when you actually want the patch on a target foundry. None of these are scheduled routines — all are on-demand slash commands.

| Item | Value |
|---|---|
| Invoke (orchestrated) | `/reproduce-paper <arXiv id \| analysis/<id>/design.md> [--foundry <name>] [--max-rounds N]` — runs analyze → implement → validate, then loops `/implement --feedback <prev-validation>` + `/validate` until the validation verdict stabilises or the round cap is reached |
| Invoke (step-by-step) | `/analyze-paper <arXiv id \| arXiv url \| pdf url>` → `/implement analysis/<id>/design.md [--foundry <name>]` → `/validate analysis/<id>/design.md [--foundry <name>]` |
| Slash commands | `.claude/commands/{analyze-paper,implement,validate,reproduce-paper}.md` (thin wrappers) |
| Canonical prompts | `.claude/prompts/{analysis,implementation,validation,reproduction}.md` (single source per stage) |
| Input context | full `context/MASTER.md`, read-only (a paper spans multiple pillars, so the full doc, not an extract) |
| Body acquisition | `curl`, full-text-preferred: `arxiv.org/abs` → `/html` → ar5iv → abstract-only, with the level recorded in the document header |
| Outputs | `analysis/<id>/analysis.md` (deep-dive), `analysis/<id>/design.md` (Layer 1 Design — vendor-agnostic), `analysis/<id>/impl/<foundry>/impl.{md,patch}` (Layer 2), `analysis/<id>/validation/<foundry>.md` (validation), plus per-round validation copies `analysis/<id>/validation/<foundry>.round_<N>.md` when run via `/reproduce-paper` — all Korean, overwritten each run |
| Structure | (A) formatted neutral summary + (B) `context/MASTER.md`-anchored decision-grade implications; Design is 7-section vendor-agnostic spec; impl carries foundry coordinates; validation carries 4-check report |
| Retrieval | full-text `curl` only at `/analyze-paper` (no Semantic Scholar / MCP); `/implement`, `/validate`, `/reproduce-paper` are local |
| Foundries | v0 foundry is `lerobot` (= `vendor/lerobot/`). Future foundries are added as new `--foundry <name>` values without changing Design or prompts. |
| Termination | `/reproduce-paper` exits on one of `all_pass` / `unmappable` / `stable_partial` / `stable_design` (focused re-extraction byte-identical) / `hold_and_report` (empty focus-hint) / `max_rounds_exhausted`. The validation §🔎 bucket classifier drives the inner/outer branch; `partial` stabilisation counts as a clean exit and only `paper-silent-experimental` gaps stay as 🚧 permanently. |

Network note: `/analyze-paper`'s full-text fetch needs the session environment to allow `arxiv.org` / `ar5iv.labs.arxiv.org` / `export.arxiv.org` (same Custom-allowlist requirement as Step 1). When full text cannot be fetched (arXiv HTML exists only for LaTeX-source papers ~2023-12+; PDF-only/complex-macro/withdrawn papers; non-arXiv paywalls; policy block; 429), the failure is recorded verbatim in the header and part (B) is marked **(본문 미확보 — 잠정)**. Format/emoji/term rules live in `docs/STYLE.md` §5 (analysis) / §6 (Design + impl) / §7 (validation).

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Papers recommended are in your Anti-topics list | Anti-topics are too vague | Rewrite `context/P#.md` §5 with concrete exclusions (e.g. "any paper whose primary task is locomotion") |
| "Decision implication" is generic ("tune DR wider") | Prompt isn't forcing specificity | Add to `scouting.md`: "name a specific config key / hyperparameter / metric (not a hand-wave like 'tune X wider')" |
| Same paper recommended two weeks in a row | Agent skipped the last-2-weeks context | Confirm the prompt's read-only "last 2 weeks of `scouting/`" reference is intact and those files exist |
| `claude routine register` / a `.claude/routines/*.yaml` does nothing | That is not the execution mechanism | Register via the RemoteTrigger form ([claude.ai/code/routines](https://claude.ai/code/routines)) — Step 2/4 |
| Agent silently edits `context/P#.md` | Prompt guard missing | Re-add the hard "never modify `context/P#.md`" guard (currently present in `scouting.md` — do not remove it) |
| Routine ran but PR is empty / every `curl` fails | Outbound network policy blocking the API domains | Set Network access = Custom and allow `export.arxiv.org` / `arxiv.org` / `api.semanticscholar.org`; check the verbatim error under 📋 Scout Methodology |
| Citation graph only partially filled / frequent HTTP 429 | Semantic Scholar rate-limited | Run keyless (recommended) or add a *valid approved* key; keep the ~3 s sleep + backoff. See the two-403 note in Step 1 |
| Semantic Scholar returns 403 even with a key set | Invalid/unapproved key (free-domain emails no longer get keys) | Remove the `SEMANTIC_SCHOLAR_API_KEY` env var and run keyless (works at 200) |
| `scouting.md` tries to call MCP tools | Stale prompt (MCP residue) | Confirm the RETRIEVAL section is `curl` REST — MCP is unreachable from cloud sessions |
