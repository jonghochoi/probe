#!/usr/bin/env bash
# Build the CodeGraph index over vendor/lerobot/ on demand.
#
# Invoked by /implement (and anything that reads vendor/lerobot/ through the
# CodeGraph MCP tools) before its first codegraph call. No-op if the index
# already exists, so it is cheap to call unconditionally.
#
# The DB (.codegraph/codegraph.db) is per-checkout and gitignored; only
# .codegraph/config.json (scope=vendor/lerobot) is committed. codegraph 0.9.1
# requires `init` before `index`, and `init` overwrites config.json with a
# default template whose exclude list contains **/vendor/** — which would drop
# the entire indexing scope. So back up the committed config across init and
# restore it before indexing.
set -euo pipefail
cd "$(dirname "$0")/.."

if [ -f .codegraph/codegraph.db ]; then
  exit 0
fi

trap '[ -f .codegraph/config.json.bak ] && mv -f .codegraph/config.json.bak .codegraph/config.json' EXIT

cp .codegraph/config.json .codegraph/config.json.bak
npx -y @colbymchenry/codegraph init .
mv .codegraph/config.json.bak .codegraph/config.json
trap - EXIT

npx -y @colbymchenry/codegraph index .
