#!/usr/bin/env bash
# Remove docs/pr/<pr-number>/ from the PR's branch before merge, so a squash merge leaves main without it.
# The images in the PR keep working: their links point at the earlier commit.
#   detach.sh <pr-number>
set -euo pipefail
pr=$1 dir=docs/pr/$1
[ -d "$dir" ] || { echo "no $dir on this branch: nothing to remove"; exit 0; }
git rm -q -r "$dir"
rmdir docs/pr 2>/dev/null || true
git commit -q -m "Remove PR #$pr evidence"
git push -q
echo "removed $dir"
