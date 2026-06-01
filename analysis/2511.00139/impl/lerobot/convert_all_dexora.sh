#!/usr/bin/env bash
# Batch v2.1 -> v3.0 conversion for the Dexora_Real-World_Dataset tree.
#
# Default mode walks every LeRobotDataset under the given root (the 4
# airbot_* category folders + every dexora/<task> folder). Pass extra
# subpaths after the root to convert only those (e.g. just the curated
# dexterous category + a few hand-rich tasks). Idempotent: skips folders
# whose meta/info.json already shows codebase_version=v3.0. Cleans up
# <root>_v30 staging dirs after each successful conversion.
#
# Usage:
#   # everything under ROOT
#   LEROBOT_PY=~/dev/lerobot/.venv/bin/python \
#   bash convert_all_dexora.sh /media/.../Dexora_Real-World_Dataset
#
#   # only specific subsets (subpaths are relative to ROOT, or absolute)
#   LEROBOT_PY=~/dev/lerobot/.venv/bin/python \
#   bash convert_all_dexora.sh /media/.../Dexora_Real-World_Dataset \
#        airbot_dexterous \
#        dexora/turn_rubiks_cube_bimanual \
#        dexora/write_with_pen
set -euo pipefail

ROOT="${1:?usage: $0 <Dexora_Real-World_Dataset root> [subpath ...]}"
shift || true
PY="${LEROBOT_PY:?set LEROBOT_PY to the python in your lerobot venv}"
REPO_ID="${REPO_ID:-Dexora/Dexora_Real-World_Dataset}"

[ -d "$ROOT" ] || { echo "ERROR: $ROOT is not a directory"; exit 1; }
[ -x "$PY" ]  || command -v "$PY" >/dev/null 2>&1 || { echo "ERROR: $PY not executable"; exit 1; }

fails=()

convert_one() {
  local d="${1%/}"
  local info="$d/meta/info.json"
  [ -f "$info" ] || { echo "skip (no meta/info.json): $d"; return 0; }
  local ver
  ver=$("$PY" -c "import json,sys; print(json.load(open(sys.argv[1])).get('codebase_version',''))" "$info" 2>/dev/null || true)
  if [ "$ver" = "v3.0" ]; then
    echo "skip (already v3.0): $d"
    return 0
  fi
  echo "==> converting: $d  (currently $ver)"
  if ! HF_HUB_OFFLINE=1 "$PY" -m lerobot.scripts.convert_dataset_v21_to_v30 \
       --repo-id="$REPO_ID" --root="$d" --push-to-hub=False; then
    echo "    FAILED: $d  (leaving ${d}_v30 staging for inspection)"
    fails+=("$d")
    return 0   # keep batch going
  fi
  [ -d "${d}_v30" ] && rm -rf "${d}_v30"
  echo "    done."
}

resolve() {
  # Absolute path stays as-is; otherwise relative to ROOT.
  case "$1" in
    /*) printf '%s' "$1" ;;
    *)  printf '%s' "$ROOT/$1" ;;
  esac
}

if [ "$#" -gt 0 ]; then
  # Targeted mode: convert only the given subpaths.
  for sub in "$@"; do
    convert_one "$(resolve "$sub")"
  done
else
  # Walk mode: everything under ROOT.
  for d in "$ROOT"/airbot_*/; do
    [ -d "$d" ] && convert_one "$d"
  done
  if [ -d "$ROOT/dexora" ]; then
    for d in "$ROOT/dexora"/*/; do
      [ -d "$d" ] && convert_one "$d"
    done
  fi
fi

echo "all done."
if [ "${#fails[@]}" -gt 0 ]; then
  echo "FAILURES (${#fails[@]}):"
  printf '  %s\n' "${fails[@]}"
  exit 2
fi
