#!/bin/bash
# run-council.sh ROUND BATCH [only]: the three reviewers (or only the one named: codex, claude,
# opus) on rounds/ROUND/council-BATCH, in parallel, each answer into
# rounds/ROUND/review-BATCH-<reviewer>.json and its errors beside it. HILL_ROOT names another
# review's directory (web/ for the site), as for council.py; ROLE replaces the third reviewer's role.
set -u
here=$(cd "$(dirname "$0")" && pwd)
root=$(cd "${HILL_ROOT:-$here}" && pwd)
rnd=$root/rounds/$1; dir=$rnd/council-$2; schema=$here/review.schema.json
prompt=$(cat "$rnd/prompt.md")
only=${3:-}
role=${ROLE:-You review as a senior visual designer of operating-system design systems: type, colour roles, iconography and brand coherence.}
imgs=$(cd "$dir" && ls)
want() { [ -z "$only" ] || [ "$only" = "$1" ]; }
want codex && ( cd "$dir" && codex exec -s read-only --skip-git-repo-check --ephemeral --output-schema "$schema" \
    -o "$rnd/review-$2-codex.json" $(for f in $imgs; do printf -- '-i %s ' "$dir/$f"; done) \
    < "$rnd/prompt.md" > "$rnd/review-$2-codex.log" 2>&1 ) &
want claude && ( cd "$dir" && claude -p --model sonnet --tools Read --permission-mode default \
    --json-schema "$(cat "$schema")" --output-format json \
    "$prompt
Images: read every one of these files in the current directory: $(echo $imgs)" \
    < /dev/null > "$rnd/review-$2-claude.json" 2> "$rnd/review-$2-claude.log" ) &
# Gemini's Antigravity quota ran out (2026-11-08) and the gemini CLI no longer serves individual
# accounts: the third reviewer is another Claude model with another role, a weaker council.
want opus && ( cd "$dir" && claude -p --model opus --tools Read --permission-mode default \
    --json-schema "$(cat "$schema")" --output-format json \
    "$role
$prompt
Images: read every one of these files in the current directory: $(echo $imgs)" \
    < /dev/null > "$rnd/review-$2-opus.json" 2> "$rnd/review-$2-opus.log" ) &
wait
