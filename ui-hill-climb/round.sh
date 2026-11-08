#!/bin/bash
# round.sh NN CAPTURE: one council round of the screen set on a candidate the harness captured.
#
#   ./round.sh 01 ../../os/_output/test
#
# Copies screens.json's screens from CAPTURE (the harness's PNGs, by view name) into
# rounds/NN/shots, builds the two blind batches - every screen a pair against round 00, sides at
# random, and three of round 00's screens again as the control - runs the three reviewers on both
# in parallel, records them in ledger.jsonl, and writes the before/after page into
# ../_output/compare (outside the repository: the Artifact tool publishes it from there).
set -euo pipefail
here=$(cd "$(dirname "$0")" && pwd)
nn=$1 capture=$(realpath "$2")
cd "$here"
shots=rounds/$nn/shots
mkdir -p "$shots"
ids=$(python3 -c 'import json; print(" ".join(s["id"] for s in json.load(open("screens.json"))["screens"]))')
for id in $ids; do
  test -s "$capture/$id.png" || { echo "round.sh: $capture/$id.png missing" >&2; exit 1; }
  cp "$capture/$id.png" "$shots/$id.png"
done
test -s rounds/$nn/prompt.md || { echo "round.sh: rounds/$nn/prompt.md missing" >&2; exit 1; }

A=desktop,desktop-light,desktop-scale-150,shell-overview,shell-app-grid,shell-quick-settings,shell-calendar,shell-notifications,shell-lock-screen,shell-lock-prompt
B=org.gnome.Nautilus,org.gnome.Settings,panel-network,gtk-dialog,gtk-dialog-light,com.mitchellh.ghostty,org.gnome.SystemMonitor,installer,io.github.construct_linux.Construct
python3 council.py "$nn" shell --screens "$A" --candidate "$shots" --control desktop,shell-calendar,shell-lock-screen \
  --refs ref-gnome-overview.png,ref-elementary-desktop.jpg,ref-macos-quick-settings.jpg,ref-macos-lock.jpg
python3 council.py "$nn" apps --screens "$B" --candidate "$shots" --control org.gnome.Settings,gtk-dialog,com.mitchellh.ghostty \
  --refs ref-gnome-files.png,ref-elementary-files.png,ref-cosmic-settings.png,ref-elementary-shortcuts.png
./run-council.sh "$nn" shell & ./run-council.sh "$nn" apps & wait
python3 record.py "$nn" shell
python3 record.py "$nn" apps
python3 "${SKILL_DIR:?SKILL_DIR names the ui-hill-climb skill}/scripts/ledger.py" ledger.jsonl

# The page: compare.mjs names a shot <screen>.<viewport>.<theme>, so the view names' dots go.
page=$here/../_output/compare; cmp=$here/../_output/compare-src
rm -rf "$page" "$cmp"; mkdir -p "$cmp/before" "$cmp/after"
for id in $ids; do
  n=${id//./-}.2880x1800.default.png
  cp rounds/00/shots/$id.png "$cmp/before/$n"; cp "$shots/$id.png" "$cmp/after/$n"
done
python3 -c '
import json, sys
for line in open("ledger.jsonl"):
    r = json.loads(line)
    for p in r["pairs"]:
        p["screen"] = p["screen"].replace(".", "-")
    print(json.dumps(r))' > "$cmp/ledger.jsonl"
node "$SKILL_DIR/scripts/compare.mjs" --before "$cmp/before" --after "$cmp/after" --out "$page" \
  --ledger "$cmp/ledger.jsonl" --round "$((10#$nn))" --title "The desktop, before and after" \
  --note "${NOTE:-Round $nn of CONSTRUCT's design review: the candidate against os main's approved needles.}"
echo "$page/index.html"
