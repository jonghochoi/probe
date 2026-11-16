#!/usr/bin/env bash
# Build the pillar-page playground: the reading site under site/, the pillar
# drafts at site/pl/, and the playground page at the top.
#
# usage: design/playground/pillar/build.sh <checkout> [out-dir]
#   <checkout> - a probe checkout whose site/ carries the redesign (the port
#   branch, or main once it lands); the design branch keeps only the records
# then:  python3 -m http.server -d <out-dir> 8000  and open /
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
repo="$(cd "${1:?a checkout with the redesigned site}" && pwd)"
out="${2:-$here/out}"
rm -rf "$out" && mkdir -p "$out"
python3 "$repo/site/build-site.py" --out "$out/site"
cp "$here/pl.css" "$here/pl.js" "$out/site/assets/"
PROBE_REPO="$repo" python3 "$here/gen-pillar.py" "$out/site"
cp "$here/playground-pillar.html" "$out/index.html"
echo "pillar playground built in $out"
