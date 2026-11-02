#!/usr/bin/env bash
# Run one review axis with an external model, falling back down the list.
#
#   run-reviewer.sh --self <claude|codex|agy|other> <brief-file> <out-file>
#
# Last stdout line: "reviewer=<name>" on success (exit 0),
# or "reviewer=none" when every external reviewer failed (exit 1).
# Each attempt's stderr goes to <out-file>.<name>.err.
# No timeout wrapper on purpose: macOS has no `timeout`; the caller's tool limit is the timeout.
set -u

[ "${1:-}" = "--self" ] && [ $# -eq 4 ] || {
  echo "usage: $0 --self <claude|codex|agy|other> <brief-file> <out-file>" >&2; exit 2; }
self=$2 brief=$3 out=$4
[ -s "$brief" ] || { echo "brief missing or empty: $brief" >&2; exit 2; }

case $self in
  claude) order="agy codex" ;;
  codex)  order="agy claude" ;;
  agy)    order="codex claude" ;;
  *)      order="agy codex claude" ;;
esac

repo=$(git rev-parse --show-toplevel) || exit 2
cd "$repo" || exit 2
snapshot() { git rev-parse HEAD; git status --porcelain; }
before=$(snapshot)

run() { # $1 = reviewer; stdout -> $out, stderr -> $out.$1.err
  case $1 in
    agy)    agy --mode plan --settings '{"permissions":{"allow":["command(git)"]}}' \
              -p "$(cat "$brief")" > "$out" ;;
    codex)  codex exec -s read-only -C "$repo" -o "$out" - < "$brief" > /dev/null ;;
    claude) claude -p --permission-mode plan < "$brief" > "$out" ;;
  esac 2> "$out.$1.err"
}

for r in $order; do
  if ! command -v "$r" > /dev/null; then echo "skip $r: not installed" >&2; continue; fi
  rm -f "$out"
  run "$r"; code=$?
  if [ "$(snapshot)" != "$before" ]; then
    echo "WARNING: repo changed while $r was reviewing (HEAD or working tree); check git status" >&2
  fi
  if [ $code -eq 0 ] && [ -s "$out" ]; then echo "reviewer=$r"; exit 0; fi
  echo "fail $r: exit $code, $( [ -s "$out" ] && echo output || echo empty output ); see $out.$r.err" >&2
done

echo "reviewer=none"
exit 1
