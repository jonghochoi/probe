#!/usr/bin/env bash
# Build the combined paper-page playground: the site (from the checkout's
# current branch) under site/, the panel as index.html.
# usage: PROBE_REPO=<checkout> paper-all/build.sh <out-dir>
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
repo="${PROBE_REPO:-/home/user/probe}"
out="$1"; ids=(2606.15768 2610.16308 2610.09455)
rm -rf "$out"; mkdir -p "$out"
python3 "$repo/site/build-site.py" --strict --out "$out/full" >/dev/null
PROBE_REPO="$repo" python3 "$here/../paper/gen-paper.py" "$out/full" "${ids[@]}" >/dev/null
mkdir -p "$out/site/p"
cp -r "$out/full/assets" "$out/site/"
for i in "${ids[@]}"; do mkdir -p "$out/site/p/$i"; cp "$out/full/p/$i/index.html" "$out/site/p/$i/"; done
rm -rf "$out/full"
cp "$here/plall.css" "$here/plall.js" "$out/site/assets/"
cp "$here/playground-all.html" "$out/index.html"
echo "playground → $out ($(find "$out" -type f | wc -l) files)"
