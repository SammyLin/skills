---
name: mobile-app-design
description: >-
  Design, build and audit native iOS (SwiftUI) and Android (Jetpack Compose) app screens: a
  DESIGN.md the whole app follows, every screen drawn in all of its states (loading, empty,
  error, loaded, offline), platform rules from Apple's HIG and Material 3, and a layout-stability
  audit so nothing jumps between skeleton and content. Use when designing or reviewing an app's
  UI, starting an Android version of an iOS app (or the reverse), or when the user mentions
  layout shift, skeleton screens, 畫面跳動, 版面穩定, 載入閃一下, scroll jumping, "the list jumps",
  or asks for iOS / Android design best practices.
---

# mobile-app-design

One design, two platforms, every state. Talk to the user in their language.

## 0. Read what exists

- The app's `DESIGN.md` (colours, type, components, banned list). Missing → write one from
  [design-md-template.md](design-md-template.md) before touching a screen, and get the owner's
  yes on it. Owner decisions recorded there are not yours to undo.
- The shared design components (theme, skeleton, buttons). Reuse them; a second skeleton or
  a second button style is the most common way an app drifts.
- The screen list: every tab, pushed page, sheet and alert. Write it down; the audit walks it.

## 1. Design each screen as a set of states

A screen is not done until each state below is drawn, and each one keeps the same frame:

| State | Rule |
|---|---|
| Loading | Skeleton with the loaded layout's exact geometry. A spinner only for an action the user just started. |
| Loaded | Content replaces the skeleton in place. |
| Empty | Same header and controls as loaded; one line saying why it is empty and what to do. |
| Error / offline | Keep cached content if there is any; say what failed in one line, with a retry. |
| Partial | Each async block (price, photo, chart) has its own placeholder; one slow block never holds the page. |
| Large text | Largest Dynamic Type / 200% font scale: nothing clipped, layout may stack but not overlap. |
| Dark, Reduce Motion | Checked, not assumed. |

## 2. Platform rules

Same information architecture and copy on both; native controls and navigation on each.
[ios.md](ios.md) for SwiftUI, [android.md](android.md) for Compose. Never ship one platform's
idiom on the other (iOS back chevron on Android, a FAB on iOS, Material ripple in SwiftUI).

## 3. Layout stability

The skeleton → loaded swap, a background refresh and a filter change must not move anything the
user did not move. Run [layout-stability.md](layout-stability.md) over **every** screen in the
list from step 0, not just the one in the bug report. Fix the cause (missing reserved size,
unstable IDs, a view that only exists after data arrives); never hide a shift with an animation.

## 4. Verify on a device or simulator

- Add a debug launch flag that holds every request in its loading state (`-holdLoading YES` on
  iOS, a debug build config field on Android), so the skeleton can be screenshotted.
- Screenshot each screen loading, then loaded, same device, same scroll offset, status bar
  fixed (`xcrun simctl status_bar booted override --time 9:41`). Then run
  `python3 <this skill>/shift_check.py loading.png loaded.png -o overlay.png` (Pillow). It pairs
  the long straight edges (cards, photo blocks, search bar, controls) and lists every one that
  moved or exists in only one shot; exit 1 = shift. Text vs skeleton bars is ignored by design.
- What pass and fail look like: [examples/reference.png](examples/reference.png) (a matching skeleton,
  and one with the three usual mistakes: controls missing while loading, cards too short, photo
  too small). Regenerate and self-check with `shift_check.py --examples examples`.
- Look at every screenshot and overlay yourself before saying done; the script is a heuristic.
- Large text and dark mode: one screenshot each per changed screen.

Report per screen: what moved, why, what fixed it, before/after screenshots.
