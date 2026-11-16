#!/usr/bin/env bash
# Build the paper-page playground: the site under site/, the panel as index.html.
# usage: PROBE_REPO=<checkout> paper/build.sh <out-dir>
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
repo="${PROBE_REPO:-/home/user/probe}"
out="$1"; ids=(2606.15768 2610.16308 2610.09455)
rm -rf "$out"; mkdir -p "$out"
python3 "$repo/site/build-site.py" --strict --out "$out/full" >/dev/null
mkdir -p "$out/site/p"
cp -r "$out/full/assets" "$out/site/"
for i in "${ids[@]}"; do mkdir -p "$out/site/p/$i"; cp "$out/full/p/$i/index.html" "$out/site/p/$i/"; done
PROBE_REPO="$repo" python3 "$here/gen-paper.py" "$out/full" "${ids[@]}" >/dev/null
cp "$out/full/assets/plpaper-data.js" "$out/site/assets/"
rm -rf "$out/full"
cp "$here/plpaper.css" "$here/plpaper.js" "$out/site/assets/"
cp "$here/playground-paper.html" "$out/index.html"
echo "playground → $out ($(find "$out" -type f | wc -l) files)"
