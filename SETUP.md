# Agent Setup Guide

Deploying the scheduled scouting routine: a cloud session that commits its own
reports straight to `main`. On-demand `/analyze` needs none of this — it runs
from any Claude Code session.

Scheduling is created in the **RemoteTrigger form** at
[claude.ai/code/routines](https://claude.ai/code/routines) (or the `/schedule`
CLI), not in a repo config file; the durable asset is the shared prompt
`.claude/prompts/scouting.txt`. Register **one routine per pillar** (P0–P5) —
the steps below use P1 as the worked example.

| | Manual run | Scheduled routine |
|---|---|---|
| Execution | your laptop | cloud, on a cadence |
| Retrieval | built-in web search | `curl` to arXiv + Semantic Scholar REST — **no MCP** (cloud sessions cannot reach a local MCP server) |
| Output | copy by hand | the prompt commits and runs `git push origin HEAD:main` — no PR; commit history *is* the research log |

## 1. Prerequisites

| Item | Note |
|---|---|
| Claude Code Pro plan | Routines need cloud execution; the daily cap covers the scouting cadence |
| GitHub repo connected | The routine pushes to `main` in this repo |
| Network policy = Custom | The default **Trusted** policy blocks arXiv and S2 — §2-1 |
| `SEMANTIC_SCHOLAR_API_KEY` | Optional, and **prefer keyless** — §2-2 |

## 2. Environment

Both settings live in one dialog: routine → **Edit routine** → cloud icon →
gear → **Update cloud environment**. Changes apply to **new sessions only**;
the next scheduled run picks them up.

### 2-1. Network allowlist

**Trusted** allows only package registries and GitHub; everything else gets
`HTTP 403` with `x-deny-reason: host_not_allowed`. Set **Network access →
Custom** and list one host per line:

```
export.arxiv.org
arxiv.org
api.semanticscholar.org
```

Keep **"Also include default list of common package managers"** checked —
unchecking it breaks GitHub/registry access.

### 2-2. `SEMANTIC_SCHOLAR_API_KEY`

Same dialog, under **Environment variables**, `.env` format, no quotes.

- **Prefer keyless.** S2 does not issue keys to free-domain emails, and an
  unapproved key makes the API return 403 *while keyless works*. With the
  variable empty the prompt omits the header, sleeps ~3 s between calls and
  backs off on HTTP 429.
- There is no secret store — environment variables are readable by anyone who
  can edit the environment.

> **Two different 403s.** `x-deny-reason: host_not_allowed` → network layer,
> fix with the allowlist in §2-1. S2 403 *only when the key header is sent* →
> API auth, fix by dropping the key.

### 2-3. Verify

From a fresh session, both must print `200`:

```bash
curl -sS -o /dev/null -w "%{http_code}\n" \
  "https://api.semanticscholar.org/graph/v1/author/search?query=Kevin+Black&fields=name"
curl -sS -o /dev/null -w "%{http_code}\n" \
  "http://export.arxiv.org/api/query?search_query=cat:cs.RO&max_results=1"
```

## 3. Routine

| Form field | Value |
|---|---|
| Name | `probe-weekly-scout` |
| Prompt (Instructions) | The full body of `.claude/prompts/scouting.txt`, every `<PILLAR>` replaced by `P1`. Model → **Sonnet** |
| Repositories | This repo |
| Environment | The one from §2 |
| Trigger | A recurring cadence of your choosing (the form takes local time → UTC; min interval 1 h) |
| Connectors | None — retrieval is `curl`, not a connector |
| Permissions | Must allow pushing to `main`; the default `claude/`-branch-only push is not sufficient |

- Set the environment to **at most one active session**, so concurrent runs do
  not race on the shared branch (the prompt keeps a `git pull --rebase origin
  main` retry as an in-prompt backstop).
- The form has no `context_files` field and needs none: the prompt names its
  own inputs (`context/P1.md` §1–§6, the last 2 weeks of `scouting/`), the
  `curl` procedure, the output rules and the guards. Being pillar-scoped, it
  omits the monthly Cross-pollination rule, whose source is
  `context/MASTER.md` §7.

## 4. First run

Use **Run now** on the routine detail page. A green status only means "exited
without an infra error" — open the transcript and check the output with the
same rigor as a manual run:

- [ ] Follows `scouting/templates/report.md` + `scouting/AUTHORING.md`.
- [ ] One Korean report at `scouting/P#/YYYY-MM-DD.md`, no language-suffixed
      twin (`CLAUDE.md` → "Document language convention").
- [ ] Every paper link resolves — no fabricated arXiv IDs.
- [ ] The `Papers scanned:` header discloses **no** `curl` 403 / network-block
      error; one there means the Custom allowlist is missing.
- [ ] Decision implications are concrete — a specific config key,
      hyperparameter or metric, not "tune DR wider".
- [ ] The Anti-topics filter fired; an empty "did not pass filter" section is
      suspicious.

If anything fails, fix `.claude/prompts/scouting.txt` (or `context/P1.md`) and
re-run — do not leave automation on with a bad prompt.
