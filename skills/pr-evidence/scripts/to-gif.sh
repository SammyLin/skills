#!/usr/bin/env bash
# Turn a screen recording (mp4/mov) into a GIF small enough for a PR.
#   to-gif.sh <video> <out.gif> [width=360] [fps=12] [max_mb=8]
# Two-pass palette for clean colours; if the GIF is over max_mb it retries narrower and slower.
set -euo pipefail
in=$1 out=$2 width=${3:-360} fps=${4:-12} max_mb=${5:-8}
command -v ffmpeg >/dev/null || { echo "ffmpeg missing: brew install ffmpeg" >&2; exit 1; }
tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT
for _ in 1 2 3 4; do
  f="fps=$fps,scale=$width:-1:flags=lanczos"
  ffmpeg -loglevel error -y -i "$in" -vf "$f,palettegen=stats_mode=diff" "$tmp/p.png"
  ffmpeg -loglevel error -y -i "$in" -i "$tmp/p.png" -lavfi "$f [x]; [x][1:v] paletteuse=dither=bayer:bayer_scale=5:diff_mode=rectangle" -loop 0 "$out"
  size=$(( $(stat -f %z "$out" 2>/dev/null || stat -c %s "$out") / 1024 / 1024 ))
  [ "$size" -lt "$max_mb" ] && { echo "$out ${size}MB ${width}px ${fps}fps"; exit 0; }
  width=$(( width * 3 / 4 )); fps=$(( fps > 8 ? fps - 2 : fps ))
done
echo "$out is still ${size}MB: trim the recording (ffmpeg -ss/-t) and try again" >&2; exit 1
