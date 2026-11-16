#!/usr/bin/env bash
# Build the redesign playground: the reading site at this checkout, the mock
# pages and assets on top of it, and one playground copy per page.
#
# usage: design/playground/build.sh [out-dir]    (default: design/playground/out)
# then:  python3 -m http.server -d <out-dir> 8000  and open /playground-home.html
set -euo pipefail

here="$(cd "$(dirname "$0")" && pwd)"
repo="$(cd "$here/../.." && pwd)"
out="${1:-$here/out}"
mkdir -p "$out"
cd "$repo"

# the published site exactly as the build makes it; gen-pages reads its corpus.json and shell
python3 site/build-site.py --out "$out/base"
rm -rf "$out/site"
cp -r "$out/base" "$out/site"

# the mock assets, the track mascots, and the pages the playground adds
cp "$here/scout-new.css" "$here/scout-new.js" "$here/next-pages.js" "$here/row-links.json" "$out/site/assets/"
mkdir -p "$out/site/assets/mascots"
cp assets/probe-*.svg "$out/site/assets/mascots/"
python3 "$here/gen-pages.py" "$out/base" "$out/site"

# the list offers 10 / 20 / 30 a page, where the site offers 10 / 20 / all
sed -i 's#<button type="button" data-size="0" aria-pressed="false">전체</button>#<button type="button" data-size="30" aria-pressed="false">30편</button>#' "$out/site/index.html"

# one copy per page: the copy shows that page and only that page's options
cp "$here/playground.html" "$out/playground.html"
for pair in "front:첫 화면" "home:분석 목록" "paper:논문" "scout:탐색 (지금)" "scout2:탐색 새 시안" "cmp:비교" "cmp2:비교 새 시안" "shelf2:서재 새 시안"; do
  key="${pair%%:*}"; label="${pair#*:}"
  sed -e "1s#<title>PROBE 테마 조율실</title>#<title>PROBE 조율실 $label</title>#" \
      -e "s#  var LOCK = \"\"; // set per copy#  var LOCK = \"$key\"; // set per copy#" \
      "$here/playground.html" > "$out/playground-$key.html"
done
echo "playground built in $out"
