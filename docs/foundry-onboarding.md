# Foundry onboarding

A **foundry** is a target codebase that `/implement-design` maps a Layer 1
Design onto and `/validate-impl` verifies against. The v0 foundry is
`lerobot`; this guide is the generic procedure for registering another one.
CLAUDE.md's "Foundry runtime" section summarizes the runtime half; this doc
is the full checklist, including the doc and prompt touchpoints that are
easy to miss.

## What a foundry consists of

| Surface | Where | Role |
|---|---|---|
| Vendored snapshot | `vendor/<name>/` | Read-only, byte-stable partial copy for reading and `git apply --check` — the coordinate system every `impl.md`/`impl.patch` grounds in |
| Provenance table | `vendor/<name>/README.md` | `Source repository` + `Pinned commit` + `Vendor date` + `License` + `Scope` rows; the SHA every impl/validation meta table cites |
| Runtime case arm | `scripts/ensure-foundry-runtime.sh` | Clone URL + `requires-python` floor, keyed by foundry name; builds the executable `.foundry-runtime/<name>/` on demand |
| Impl/validation outputs | `analysis/<id>/impl/<name>/`, `analysis/<id>/validation/<name>.md` | Created per paper by the pipeline once the foundry exists |

## Checklist

1. **Create the snapshot** — `vendor/<name>/` holding the *minimum code
   surface a Design needs to ground in* (for lerobot: policies + configs +
   processor + datasets + transforms + utils). Copy files byte-identical
   from the pinned upstream commit; keep upstream license headers; include
   the upstream `LICENSE`. The snapshot does not need to import or run —
   partial trees are expected (the runtime, not the snapshot, executes).
2. **Write `vendor/<name>/README.md`** — mirror `vendor/lerobot/README.md`:
   the provenance table (the `Pinned commit` row format is load-bearing —
   `| Pinned commit | `<sha>` |` — `ensure-foundry-runtime.sh` parses it),
   the vendored-tree listing, the "not vendored" boundary, and a refresh
   procedure. State explicitly that hand-edits are forbidden and a pin bump
   invalidates every existing `impl.patch` under `*/<name>/`.
3. **Register the runtime** — add one `case` arm in
   `scripts/ensure-foundry-runtime.sh` (`<name>) url="…"; pyver="…" ;;`).
   Nothing else in the script changes. If the upstream package needs
   install quirks (index pins, extras), keep them inside the arm or the
   install step with a comment, as the lerobot torch/cu128 note does.
4. **Check the prompt touchpoints** — the prompts parameterize `<foundry>`
   almost everywhere, but two spots are foundry-specific and gate a new
   foundry:
   - `.claude/prompts/implementation.txt` §A base selection and the
     grounding-inputs list are written `For --foundry lerobot:` — add the
     equivalent base-selection guidance for the new foundry (which
     subtrees are candidate bases, which are shared surface).
   - The smoke-test apply step translates the vendored prefix to the
     upstream layout (`git apply -p3 --directory=src/lerobot` in
     `implementation.txt` §G and `validation.txt` §🧬) — add the new
     foundry's directory mapping alongside.
5. **Wire the docs** — the CLAUDE.md Repository map (`vendor/<name>/` row)
   and, if the foundry becomes a default anywhere, the command
   argument-hints in `.claude/commands/*.md`.
6. **Smoke the registration** — `bash scripts/ensure-foundry-runtime.sh
   <name>` must either print a venv python path (online) or fail with a
   one-line reason (offline) — never silently succeed without a `.ready`
   marker. Then run `/implement-design` for one Design with
   `--foundry <name>` end to end.

## Invariants that must survive onboarding

- **The committed surface stays the snapshot only** — `.foundry-runtime/`
  is gitignored; never stage it.
- **Patches are authored against `vendor/<name>/` paths**, and validation
  translates the prefix to the upstream tree. Keep the mapping in step 4
  consistent or `/validate-impl §🧬` will mis-apply.
- **Unknown or unbuildable runtime degrades gracefully** — `/validate-impl
  §🧬` records `skipped`, never a fabricated pass; static verdicts stand.
- **One pin per foundry** — the README provenance row is the single source
  of truth; the runtime re-parses it on every invocation and rebuilds when
  it moves.
