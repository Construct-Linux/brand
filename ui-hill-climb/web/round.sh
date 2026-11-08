#!/bin/bash
# round.sh NN [BASE_URL]: one council round of the site's screen set.
#
#   ./round.sh 00 http://127.0.0.1:8801   # the baseline, scored twice: the first noise measure
#   ./round.sh 01 http://127.0.0.1:8802   # a candidate against round 00
#
# Captures screens.json from BASE_URL (the site served from a checkout: python3 -m http.server)
# into rounds/NN/shots - never an earlier capture - builds the two blind batches, runs the three
# reviewers on both in parallel, records them in ledger.jsonl and prints the summary. The capture
# needs Playwright and @axe-core/playwright resolvable from PW_DIR (outside the repository).
set -euo pipefail
here=$(cd "$(dirname "$0")" && pwd)
nn=$1 url=${2:-http://127.0.0.1:8802}
: "${SKILL_DIR:?SKILL_DIR names the ui-hill-climb skill}" "${PW_DIR:?PW_DIR holds node_modules/playwright}"
export HILL_ROOT=$here
export ROLE="You review as a senior visual designer of design-system and brand documentation sites: type, layout, colour roles and brand coherence."
cd "$here"
rm -rf "rounds/$nn/shots"
(cd "$PW_DIR" && node "$SKILL_DIR/scripts/capture.mjs" --base-url "$url" --screens "$here/screens.json" \
  --out "$here/rounds/$nn/shots" --axe) > "rounds/$nn/capture.log" 2>&1 || { cat "rounds/$nn/capture.log"; exit 1; }

# Desktop at 1440 in both schemes, then mobile at 390 with two desktop shots in the other scheme:
# every section is judged at least once at each width.
D=top.desktop.dark,menus.desktop.dark,overview.desktop.light,accent.desktop.dark,compare.desktop.light,light.desktop.dark,elevation.desktop.dark,perception.desktop.light,swatches.desktop.dark,wallpapers.desktop.light,identity.desktop.light
M=top.mobile.dark,menus.mobile.light,overview.mobile.dark,accent.mobile.dark,compare.mobile.light,light.mobile.light,elevation.mobile.dark,perception.mobile.dark,wallpapers.mobile.light,identity.mobile.dark,top.desktop.light
DC=top.desktop.light,accent.desktop.light
MC=accent.mobile.light,identity.mobile.light
DR=ref-radix-colors.png,ref-primer-color.png,ref-gnome-hig-palette.png
MR=ref-radix-colors-mobile.png,ref-elementary-brand.png,ref-primer-color.png
c=../council.py
if [ "$nn" = 00 ]; then
  for pass in p1 p2; do
    python3 $c 00 desk-$pass --screens "$D" --refs "$DR"
    python3 $c 00 mobile-$pass --screens "$M" --refs "$MR"
  done
  for b in desk-p1 desk-p2 mobile-p1 mobile-p2; do ../run-council.sh 00 "$b" & done; wait
  for b in desk-p1 desk-p2 mobile-p1 mobile-p2; do python3 ../record.py 00 "$b"; done
else
  python3 - "$nn" <<'PY'
import sys
t = open("prompt-template.md").read()
t = t.replace("__ATTACHED__", """- Pairs of the same screen in two versions (sNN-a.png, sNN-b.png), in no particular order.
- Single screens (cNN.png) to score on their own.""").replace("__TASKS__", """1. For each pair, say which version is better for this product and audience ("a", "b" or "tie"),
   and the single most important reason.
2. Score each rubric category 1-10, where 10 is the best reference in the set, not perfection:
   as "scores" for the versions you preferred, taken as a whole; as "control" for the cNN set.""")
open(f"rounds/{sys.argv[1]}/prompt.md", "w").write(t)
PY
  python3 $c "$nn" desk --screens "$D" --candidate "rounds/$nn/shots" --control "$DC" --refs "$DR"
  python3 $c "$nn" mobile --screens "$M" --candidate "rounds/$nn/shots" --control "$MC" --refs "$MR"
  ../run-council.sh "$nn" desk & ../run-council.sh "$nn" mobile & wait
  python3 ../record.py "$nn" desk
  python3 ../record.py "$nn" mobile
fi
python3 "$SKILL_DIR/scripts/ledger.py" ledger.jsonl
