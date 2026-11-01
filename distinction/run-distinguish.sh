#!/usr/bin/env bash
# The scheduled /distinguish run — distinction/SETUP.md §4.
#
# The scheduler calls this file inside the checkout and sets PROBE_PRIVATE_DIR
# to the private folder. Nothing machine-specific lives here: the checkout is
# found from this file's own path, so the pull below carries a merged change
# to it — the tool list included — to the next run, as it does the prompt.
set -euo pipefail

# Wrapped in a function so bash reads the whole file before running any of
# it: the pull below can replace this file mid-run.
main() {
  : "${PROBE_PRIVATE_DIR:?PROBE_PRIVATE_DIR is unset}"
  if [ ! -f "$PROBE_PRIVATE_DIR/BASKET.md" ]; then
    echo "run-distinguish: no BASKET.md in $PROBE_PRIVATE_DIR" >&2
    exit 1
  fi

  # The private folder's git ignores this log.
  exec >>"$PROBE_PRIVATE_DIR/runs/distinguish.log" 2>&1
  echo "── run-distinguish $(date -Iseconds) ──"

  cd "$(dirname "$(readlink -f "$0")")/.."
  # The pull fast-forwards the current branch, so a feature branch would run
  # its own prompt instead of main's.
  if [ "$(git rev-parse --abbrev-ref HEAD)" != main ]; then
    echo "run-distinguish: checkout is not on main" >&2
    exit 1
  fi
  git pull --ff-only origin main

  # -p runs one turn with no one to approve a tool, so every tool the
  # procedure uses is granted here, and nothing it must not: no git add,
  # commit or push. Agent is the verify pass (prompt step 6).
  claude -p "/distinguish" \
    --add-dir "$PROBE_PRIVATE_DIR" \
    --allowedTools "Read,Write,Edit,Glob,Grep,Agent,Bash(printenv *),Bash(test *),Bash(date *),Bash(python3 *),Bash(git log *),Bash(git rev-parse *),Bash(grep *),Bash(sha256sum *),Bash(sh *),Bash(cd *)"
}

main "$@"
exit
