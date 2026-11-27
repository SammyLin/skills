---
name: pr-evidence
description: >-
  Show in a GitHub pull request that the change works: pick the strongest kind of evidence for
  the task (GIF of the interaction > screenshots > written description with logs), record it from
  an iOS simulator, Android emulator or browser, turn video into a small GIF, and put the files
  in the PR itself (committed on the PR's branch under docs/pr/<number>/ and kept in the repo as
  a record). Use whenever a PR needs proof, screenshots or a GIF ("附 GIF",
  "PR 要有截圖", "錄一下", "record a GIF", "add screenshots to the PR"), and before opening a PR
  for a UI change.
---

# pr-evidence

GitHub has no API to upload images to a PR. This skill puts them in the PR another way:
commit them on the PR's branch under `docs/pr/<number>/` and embed them by commit SHA. They merge
with the PR and stay in the repo as a record of what each change looked like.

## 1. Pick the evidence

Use the first that fits; when a PR has both UI and logic, give both.

| The change | Evidence |
|---|---|
| Something moves or responds: a flow, tap, scroll, drag, popup, animation, transition | **GIF** of doing it |
| A still screen changed: layout, text, colour, a state | **Screenshots**, before and after, same screen, same size |
| No screen: logic, backend, script, data, config | **Description + log**: the test run or command output, trimmed to what proves it |

Changed on iOS and Android → evidence from both. Couldn't verify something (no device, no SDK,
no login) → say so in the PR instead of implying it was checked.

## 2. Record

Get the app straight to the screen (the repo's CLAUDE.md lists its launch arguments) and drive
it with a throwaway UI test or script; delete that test afterwards.

**iOS simulator**
```bash
xcrun simctl io <udid> recordVideo --codec=h264 --force /tmp/ev/flow.mp4 &  REC=$!
# ...run the throwaway UI test (xcodebuild test -only-testing:...) or simctl launch...
kill -INT $REC; wait $REC            # SIGINT, or the mp4 has no index and won't open
xcrun simctl io <udid> screenshot /tmp/ev/after.png
```

**Android emulator**
```bash
adb shell screenrecord --time-limit 30 /sdcard/flow.mp4 &  REC=$!
# ...drive it (adb shell input, or an instrumented test)...
kill -INT $REC; sleep 1; adb pull /sdcard/flow.mp4 /tmp/ev/
adb exec-out screencap -p > /tmp/ev/after.png
```

**Web**: Playwright `browser.newContext({ recordVideo: { dir } })`, or the web-validate skill for
pages behind a login.

Before and after screenshots: take "before" on the base branch (or the current release) with the
same device, launch arguments and data.

Look at every frame you attach. A blank screen, spinner, popup in the way or the wrong screen is
a failed recording: fix and record again.

## 3. Make the GIF

```bash
scripts/to-gif.sh /tmp/ev/flow.mp4 /tmp/ev/flow.gif   # [width=320] [fps=10] [max_mb=8]
```
Trim first if it runs long (`ffmpeg -ss 2 -t 8 -i in.mp4 -c copy out.mp4`): 5–15 s showing just the
change. GitHub doesn't show images of 10 MB or more; the script shrinks until it's under 8 MB.
The files stay in the repo, so keep them small: one short GIF per flow, screenshots resized to
about 480 px wide (`sips -Z 960 shot.png` keeps the longer side at 960 px).

## 4. Put it in the PR

On the PR's branch, inside the repo:
```bash
scripts/attach.sh <pr-number> /tmp/ev/flow.gif /tmp/ev/before.png /tmp/ev/after.png
```
It commits them to `docs/pr/<pr-number>/`, pushes, and prints Markdown image links pinned to that
commit (they keep working even if the files are moved or deleted later). Put them in the PR description (`gh pr edit <n> --body-file ...`) under a heading per
platform, one line each saying what it shows:

```markdown
## Evidence
### iOS
Scrolling the 小三國語 page: one card per lesson, then 其他練習.
![flow.gif](https://github.com/<owner>/<repo>/blob/<sha>/docs/pr/176/flow.gif?raw=true)
```

Logs go in a fenced block in the description, trimmed: the command, the lines that prove it,
the summary line.

Check the files landed: `gh api "repos/<owner>/<repo>/contents/docs/pr/<n>/<file>?ref=<sha>" --jq .size`.
Don't test the image links with curl: on a private repo they 404 without a browser session, yet
show in the PR for anyone signed in with access. Ask the user to look once the first time.

## 5. Merge

Nothing to do: the files merge with the PR and stay in `docs/pr/<pr-number>/`.

## Rules

- Never commit evidence to main or to a branch that isn't the PR's.
- No secrets, real children's or customers' names, emails or tokens on screen: use demo data.
- Say what each image shows; an unexplained GIF is weak evidence.
