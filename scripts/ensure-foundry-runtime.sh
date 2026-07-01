#!/usr/bin/env bash
# Build an *executable* runtime for a foundry on demand, so /validate can run the
# foundry-specific smoke test (impl §🧬) instead of only diffing text.
#
# The vendored snapshot under vendor/<foundry>/ is a partial, byte-stable copy
# for reading and `git apply --check` — it cannot be imported or run (its files
# import from non-vendored modules). To actually execute a generated test we
# need the *whole* upstream package installed at the pinned commit. This script
# produces that, once per checkout, under a gitignored runtime dir.
#
# Usage:  bash scripts/ensure-foundry-runtime.sh [<foundry>]   # default lerobot
#
# Contract:
#   exit 0  — runtime is ready; print the venv python path on the last stdout
#             line (callers read it to run pytest).
#   exit 1  — runtime could NOT be built (offline clone/install, unknown
#             foundry, dirty pin). Callers MUST degrade to static-only validation
#             (git apply --check) and record the reason — never fabricate a
#             §🧬 pass. The one-line reason is printed to stderr.
#
# Quiet by design: clone/install output goes to a log file, never stdout, so a
# multi-GB install does not flood an agent's context. Only a short failure tail
# is surfaced. Re-runs are a no-op once the .ready marker exists (≈free).
set -euo pipefail
cd "$(dirname "$0")/.."

foundry="${1:-lerobot}"
readme="vendor/${foundry}/README.md"
runtime_root=".foundry-runtime/${foundry}"
src_dir="${runtime_root}/src"
venv_dir="${runtime_root}/.venv"
log="${runtime_root}/build.log"
ready="${runtime_root}/.ready"
py="${venv_dir}/bin/python"

fail() { echo "ensure-foundry-runtime(${foundry}): $1" >&2; exit 1; }

[ -f "$readme" ] || fail "no vendor/${foundry}/README.md — unknown foundry"

# uv creates the runtime venv (pinned python version); hard prerequisite.
command -v uv >/dev/null 2>&1 || \
  fail "uv is not installed — required to create the runtime venv (https://docs.astral.sh/uv/)"

# Pin SHA + source repo are parsed from the vendor README provenance table
# (the same rows /implement and /validate cite). Keep those rows the single
# source of truth so the runtime can never drift from the snapshot it mirrors.
# Both parses tolerate case/whitespace drift in the row label and cell padding
# (a human edits that table by hand during the refresh procedure).
pin="$(sed -nE 's/^\|[[:space:]]*[Pp]inned[[:space:]]+[Cc]ommit[[:space:]]*\|[[:space:]]*`([0-9a-fA-F]{7,40})`.*/\1/p' "$readme" | head -1)"
[ -n "$pin" ] || fail "could not parse 'Pinned commit' SHA from $readme"

repo="$(sed -nE 's/^\|[[:space:]]*[Ss]ource[[:space:]]+[Rr]epository[[:space:]]*\|[[:space:]]*`([A-Za-z0-9._/-]+)`.*/\1/p' "$readme" | head -1)"
[ -n "$repo" ] || fail "could not parse 'Source repository' from $readme"
url="https://github.com/${repo}.git"

# Map foundry -> required python. Adding a foundry is a one-line case arm here
# plus a vendor/<name>/ snapshot (see docs/foundry-onboarding.md); no other
# part of this script changes. The python version mirrors the foundry's
# `requires-python` floor so `uv venv` never silently picks an older system
# default. The case arm doubles as the registration gate — an unregistered
# foundry fails here even when a vendor/<name>/README.md exists.
case "$foundry" in
  lerobot) pyver="3.12" ;;
  *) fail "foundry '${foundry}' not registered — add a case arm" ;;
esac

# Idempotent: once built at the recorded pin, do nothing.
if [ -f "$ready" ] && [ "$(cat "$ready" 2>/dev/null)" = "$pin" ] && [ -x "$py" ]; then
  echo "$py"
  exit 0
fi

mkdir -p "$runtime_root"
: >"$log"

# 1. Check out the full package at the pin (fetch only that commit).
if [ ! -d "$src_dir/.git" ]; then
  git init -q "$src_dir" >>"$log" 2>&1 || fail "git init failed (see $log)"
  git -C "$src_dir" remote add origin "$url" >>"$log" 2>&1 || true
fi
if ! git -C "$src_dir" fetch --depth 1 origin "$pin" >>"$log" 2>&1; then
  tail -n 5 "$log" >&2 || true
  fail "fetch of $pin from $url failed (offline?) — degrade to static validation"
fi
git -C "$src_dir" checkout -q FETCH_HEAD >>"$log" 2>&1 || fail "checkout $pin failed (see $log)"

# 2. Install into a dedicated venv, quietly. Use the venv's own pip (not
#    `uv pip install`): lerobot's pyproject pins torch to a cu128 index via
#    [tool.uv.sources], which has a version gap in some environments and makes
#    uv's resolver fail; plain pip ignores that source and resolves torch from
#    the default index. torch is the dominant cost (one-time per checkout).
uv venv --python "$pyver" "$venv_dir" >>"$log" 2>&1 || fail "uv venv (python ${pyver}) failed (see $log)"
"$py" -m ensurepip --upgrade >>"$log" 2>&1 || fail "ensurepip failed (see $log)"
if ! "$py" -m pip install -e "${src_dir}[test]" >>"$log" 2>&1; then
  tail -n 5 "$log" >&2 || true
  fail "pip install failed (see $log) — degrade to static validation"
fi

echo "$pin" >"$ready"
echo "$py"
