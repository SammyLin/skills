# Android (Jetpack Compose, Material 3)

Sources: developer.android.com (Compose lists, window insets, edge-to-edge) and m3.material.io.
Check them when a rule here seems out of date.

## Porting from an iOS app
Same screens, copy, colours, information order and states. Change the idiom:

| iOS | Android |
|---|---|
| Tab bar | `NavigationBar` (3–5 destinations); `NavigationRail` on tablets / foldables |
| Back chevron, swipe back | System back + predictive back gesture; top app bar up arrow |
| Sheet with detents | `ModalBottomSheet` |
| SF Symbols | Material Symbols (or the app's own icon set, e.g. Lucide) |
| Segmented control | `SingleChoiceSegmentedButtonRow` or the app's own pill, same as iOS design |
| `.refreshable` | `PullToRefreshBox` |
| Haptics on select | Keep subtle; `HapticFeedbackType` |

Brand colours stay the app's own; don't switch to dynamic colour (Material You) unless the
design says so.

## Layout and touch
- Touch targets at least 48×48 dp (`Modifier.minimumInteractiveComponentSize()` is on by default
  for Material components; keep it on custom ones).
- Edge-to-edge is enforced from targetSdk 35 (Android 15): draw behind system bars and pad content
  with insets. Use `Scaffold`'s `innerPadding` for the list's `contentPadding`; never hardcode a
  status or navigation bar height.
- Fixed bottom actions in `Scaffold(bottomBar = …)`; the list gets the padding, not an overlap.
- `imePadding()` once on the screen, not per field.

## Type, colour, motion
- `sp` for text so font scale applies; test at 200%. Tabular digits:
  `TextStyle(fontFeatureSettings = "tnum")`.
- Colours in `MaterialTheme.colorScheme` slots mapped from DESIGN.md tokens, light and dark.
- Respect "Remove animations" (animator duration scale 0): skeleton pulse stops.

## Lists and stability
- `LazyColumn { items(list, key = { it.id }, contentType = { it.kind }) }`: stable keys keep
  state and scroll anchor when items move; keys must be Bundle-saveable.
- Items must never be zero-height while loading (a zero-size item makes the lazy list compose
  ever more items and the scroll jumps). Give placeholders the loaded row's size.
- `Modifier.animateItem()` only for moves the user caused (reorder, delete).
- Hoist `rememberLazyListState()` above the loading/loaded `when`, or into the ViewModel, so a
  state flip does not reset scroll. Paging 3: `items(count, key = lazyPagingItems.itemKey { it.id })`.
- Coil `AsyncImage`: size it (`Modifier.size` / `aspectRatio`), placeholder and error painters
  the same size; prefer `AsyncImage` over `rememberAsyncImagePainter` (the latter loads at
  original size).
- `Text(minLines = 2, maxLines = 2, overflow = Ellipsis)` to reserve lines.
- UI state keeps the last data during refresh (`isRefreshing` flag), never resets to `Loading`.

## Accessibility
- Row reads as one sentence: `Modifier.semantics(mergeDescendants = true)`; secondary actions as
  separate `clickable` with `onClickLabel`.
- Skeleton: one node, `contentDescription = "Loading"`, children `clearAndSetSemantics {}`.
- Test with TalkBack, font scale 200%, dark theme, and RTL if the app is localised.
