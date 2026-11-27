# pr-evidence

English · [繁體中文](README.zh-TW.md)

Puts proof that a change works into the GitHub pull request itself.

It picks the strongest evidence the task allows: a **GIF** when something moves or responds,
**before/after screenshots** when a still screen changed, a **description with logs** when there
is no screen. It records from an iOS simulator, Android emulator or browser, turns video into a
GIF small enough for GitHub (ffmpeg, two-pass palette), and attaches it.

GitHub has no API to upload images to a PR, so the files are committed on the PR's branch under
`docs/pr/<number>/` and embedded by commit SHA. Before merge they are removed in one more commit:
with a squash merge main never gets them, and the images in the PR keep working because GitHub
keeps every PR commit.

- `scripts/to-gif.sh` video → GIF under 8 MB
- `scripts/attach.sh` commit files on the PR's branch, print the Markdown
- `scripts/detach.sh` remove them before merge

Needs `ffmpeg`, `gh`, and Xcode or the Android SDK for the platform you record. Use it in
Claude Code: `/pr-evidence`, or say "add a GIF to the PR".

MIT.
