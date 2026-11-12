---
name: mobile-layout-stability
description: >-
  Find and fix layout shift in a native iOS (SwiftUI) or Android (Compose) app: skeletons that
  differ from the loaded screen, images and prices that push rows when they arrive, controls that
  appear late, lists that jump on refresh or pagination, scroll position lost on updates. Walks
  every screen, fixes the cause, proves it with loading-vs-loaded screenshots and shift_check.py.
  Use when the user mentions layout shift, layout stability, skeleton screens, 畫面跳動, 版面穩定,
  載入閃一下, 跳一下, scroll jumping, "the list jumps", or "things move when it loads".
---

# mobile-layout-stability

Goal: from loading to loaded, and on every later update, nothing the user did not touch changes
position or size. Talk to the user in their language. List every screen (tabs, pushed pages,
sheets) first; walk all of them, not just the one in the report. Fix the cause (a missing
reserved size, unstable IDs, a view that only exists after data arrives); never hide a shift
with an animation.

## Checks

1. **Skeleton geometry = loaded geometry.** Same outer size, padding, spacing, corner radius, line
   count and block order. Measure both (screenshot blend, or a debug overlay), don't eyeball.
2. **Every async block reserves its space** before data arrives:
   - Images: fixed size or fixed aspect ratio on the container, never the image's intrinsic size.
   - Prices and numbers: a placeholder as wide as a typical value; tabular (monospaced) digits so
     $999 → $1,299 does not reflow the row.
   - Text that may be 1 or 2 lines: reserve the maximum (`lineLimit(2, reservesSpace: true)` /
     `minLines = 2`) when the row height must not change.
   - Pills and badges: a row that may be empty keeps its height (reserve it, or the cards differ).
   - Sections that may not exist (comparison, chart, history): decide up front. Either the
     placeholder is shown until the answer is known and then removed **below the fold only**, or
     the section is absent from the skeleton too. Never insert a block above content the user sees.
3. **Fixed controls stay fixed.** Search bar, segment control, category chips, filter row, tab bar,
   bottom buttons, FAB: rendered in the skeleton state, same place, same size. Disable them while
   loading rather than hiding them. Counts on them ("賣場特價 73") get a placeholder of the same width.
4. **Stable identity.** List items keyed by a real ID, never by index or a fresh UUID per load.
   A refresh that returns the same items must not rebuild the rows.
5. **Scroll position survives updates.** Background refresh, pagination, a cache hit replaced by
   fresh data, returning from a detail page: the item at the top stays at the top. New items above
   the viewport go in without moving the viewport (or a "N new" pill), never by pushing content down.
6. **Replace in place.** Loading → loaded is a swap inside the same frame (cross-fade at most).
   Not a removal of the skeleton container followed by insertion of a different one.
7. **No reflow on state flips.** Favourite, follow, selected chip, expanded row: the change stays
   inside the element's own bounds. Text that changes ("通知我" → "已追蹤") fits the same width.
8. **Ads and banners** have a fixed slot size before the ad loads; a failed ad leaves the slot or
   collapses only when off screen.
9. **Keyboard and sheets** resize the content area once, not on every keystroke; suggestions
   overlay, they do not push the results.

Animation rule: an animation may smooth a change that the user caused. It may not be used to
make an unrequested shift look intentional.

## Fix patterns

| Symptom | Cause | SwiftUI | Compose |
|---|---|---|---|
| Row grows when photo arrives | No reserved image size | `.frame(width:height:)` or `.aspectRatio(1, contentMode: .fill)` on the container, then `.clipped()` | `Modifier.size()` / `.aspectRatio(1f)` on `AsyncImage`; placeholder painter same size |
| Row height jumps 1→2 lines | Name length varies | `.lineLimit(2, reservesSpace: true)` | `Text(minLines = 2, maxLines = 2)` |
| Price reflows the row | Proportional digits, no placeholder width | `.monospacedDigit()`, placeholder bar width of a 5-digit price | `fontFeatureSettings = "tnum"`, same |
| Skeleton cards a different size | Hand-built skeleton drifted | Render the real row with sample data + `.redacted(reason: .placeholder)`, or share size constants | Same row composable with placeholder data, `Modifier.placeholder` style |
| List jumps after refresh | Index/random IDs | `ForEach(items, id: \.id)` with a server ID | `items(list, key = { it.id }, contentType = { … })` |
| Top of list moves on pagination/refresh | Insert above viewport / state recreated | `scrollPosition(id:)` + `.scrollTargetLayout()`; keep the model, merge not replace | Hoist `LazyListState` (`rememberLazyListState` above the `if loading`), Paging `itemKey` |
| Controls appear only after load | Header inside the loaded branch | Header outside the `if loading` switch | Same; header is a `stickyHeader` / outside the state `when` |
| Whole screen flashes on refresh | State reset to `.loading` on refresh | Keep showing old data; show refresh in the pull indicator only | `PullToRefreshBox`; UI state keeps last data |
| Section pops in above content | Optional block inserted late | Reserve, or place it below the first screen | Same |

## Verify

1. Add a debug launch flag that holds every request in its loading state (`-holdLoading YES` on
   iOS, a debug build config field on Android), so the skeleton can be screenshotted.
2. Per screen, same device, same scroll offset, fixed status bar
   (`xcrun simctl status_bar booted override --time 9:41`): screenshot loading, then loaded.
3. `python3 <this skill>/shift_check.py loading.png loaded.png -o overlay.png` (Pillow). It pairs
   the long straight edges (cards, photo blocks, search bar, controls) and lists every one that
   moved or exists in one shot only; exit 1 = shift. Text vs skeleton bars is ignored by design.
   On the overlay red = loading only, cyan = loaded only.
4. Pass and fail look like [examples/reference.png](examples/reference.png): a matching skeleton,
   and one with the three usual mistakes (controls missing while loading, cards too short, photo
   too small). Regenerate and self-check with `shift_check.py --examples examples`.
5. Look at every screenshot and overlay yourself; the script is a heuristic. Also check largest
   text size and a background refresh while scrolled halfway down.


## Per-screen report

```
Screen: <name>   States checked: loading / loaded / empty / error / large text
Moved: <element> by <n>pt when <event>
Cause: <one line>
Fix: <file:line, one line>
Evidence: <before blend> <after blend>
```
