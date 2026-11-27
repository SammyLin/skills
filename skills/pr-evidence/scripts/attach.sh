#!/usr/bin/env bash
# Commit evidence files onto the PR's branch and print Markdown that shows them in the PR.
#   attach.sh <pr-number> <file>...        run inside the repo, on the PR's branch
# Files go to docs/pr/<pr-number>/ and stay in the repo as a record. Links point at the commit SHA,
# so they keep working even if the files are moved or deleted later (GitHub keeps every PR commit).
set -euo pipefail
pr=$1; shift
[ $# -gt 0 ] || { echo "usage: attach.sh <pr-number> <file>..." >&2; exit 1; }
branch=$(git branch --show-current)
head=$(gh pr view "$pr" --json headRefName -q .headRefName)
[ "$branch" = "$head" ] || { echo "on $branch, but PR #$pr is $head: check out the PR's branch" >&2; exit 1; }
for f in "$@"; do
  s=$(( $(stat -f %z "$f" 2>/dev/null || stat -c %s "$f") / 1024 / 1024 ))
  [ "$s" -lt 10 ] || { echo "$f is ${s}MB; GitHub won't show images of 10MB or more: shrink it (to-gif.sh)" >&2; exit 1; }
done
dir=docs/pr/$pr
mkdir -p "$dir"
cp "$@" "$dir/"
git add "$dir"
git commit -q -m "PR #$pr evidence" -- "$dir"
git push -q
sha=$(git rev-parse HEAD)
repo=$(gh repo view --json nameWithOwner -q .nameWithOwner)
for f in "$@"; do
  n=$(basename "$f")
  echo "![$n](https://github.com/$repo/blob/$sha/$dir/$n?raw=true)"
done
