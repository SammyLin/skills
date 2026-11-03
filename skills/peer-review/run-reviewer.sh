#!/usr/bin/env bash
# Run one review axis with an external model, falling back down the list.
#
#   run-reviewer.sh --self <claude|codex|agy|other> <brief-file> <out-file>
#
# Last stdout line: "reviewer=<name>" on success (exit 0),
# or "reviewer=none" when every external reviewer failed (exit 1).
# Each attempt's stderr goes to <out-file>.<name>.err.
# Each reviewer gets PEER_REVIEW_TIMEOUT seconds (default 900), then is killed and the next one runs.
# macOS has no `timeout`, so perl's alarm does it: exit 142 means timed out.
set -u

[ "${1:-}" = "--self" ] && [ $# -eq 4 ] || {
  echo "usage: $0 --self <claude|codex|agy|other> <brief-file> <out-file>" >&2; exit 2; }
self=$2 brief=$3 out=$4
limit=${PEER_REVIEW_TIMEOUT:-900}
tlim() { perl -e 'alarm shift; exec @ARGV or die "exec $ARGV[0]: $!\n"' "$limit" "$@"; }
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
    # Print mode auto-denies any command outside the allow list, the turn ends with only a
    # preamble like "I'll start by checking the diff", and agy still exits 0 with nothing on
    # stderr. The denial shows up only in its log, so fail on it there.
    # Not --mode plan: there agy may write a plan and stop to wait for "Proceed". Read-only comes
    # from denying write_file and allowing only read-only commands (rules match by token prefix,
    # so plain `git` or `find` would also let through `git reset --hard` or `find -delete`).
    agy)    tlim agy --log-file "$out.agy.log" --settings \
              '{"permissions":{"deny":["write_file(*)"],"allow":["command(git diff)","command(git log)","command(git show)","command(git status)","command(git rev-parse)","command(git ls-files)","command(git blame)","command(ls)","command(cat)","command(head)","command(tail)","command(grep)","command(rg)","command(wc)"]}}' \
              -p "$(cat "$brief")

Shell commands allowed: git diff/log/show/status/rev-parse/ls-files/blame, ls, cat, head, tail, grep, rg, wc. Any other command is denied. To find files, use ls, git ls-files or your built-in file tools, not find." \
              > "$out" || return
            ! grep 'soft-denying' "$out.agy.log" >&2 ;;
    codex)  tlim codex exec -s read-only -C "$repo" -o "$out" - < "$brief" > /dev/null ;;
    claude) tlim claude -p --permission-mode plan < "$brief" > "$out" ;;
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
  [ $code -eq 142 ] && echo "fail $r: timed out after ${limit}s" >&2
  echo "fail $r: exit $code, $( [ -s "$out" ] && echo output || echo empty output ); see $out.$r.err" >&2
done

echo "reviewer=none"
exit 1
