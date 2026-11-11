# iOS (SwiftUI)

Source: Apple Human Interface Guidelines (Layout, Loading, Typography, Accessibility, Tab bars).
Check developer.apple.com/design/human-interface-guidelines when a rule here seems out of date.

## Layout and touch
- Hit targets at least 44×44 pt, even when the glyph is smaller (`.contentShape`, `.frame(minWidth: 44, minHeight: 44)`).
- Respect safe areas. Backgrounds may extend under bars (`.ignoresSafeArea` on the background
  only); content and controls do not.
- Fixed bottom actions go in `.safeAreaInset(edge: .bottom)`, so lists scroll above them instead
  of under them.
- One gutter value for the whole app (typically 16–20 pt) in the theme.

## Navigation
- Tab bar: 3–5 top-level destinations, always visible except on pushed detail pages where the
  design says otherwise. Each tab keeps its own navigation stack and scroll position.
- Push (`NavigationStack`) for drilling into content; sheets for a self-contained task, with
  detents (`.presentationDetents`) for short ones. Alerts only for things that need a decision.
- Swipe-back must keep working: don't replace the back button with a custom one that breaks it.

## Type, colour, motion
- System font with Dynamic Type. Fixed point sizes go through one helper that scales with
  `@ScaledMetric` / `relativeTo:`; cap the growth on dense controls (`.dynamicTypeSize(...xxxLarge)`)
  instead of letting them break.
- Tabular digits for prices and counters (`.monospacedDigit()`).
- Colours as named theme tokens with light and dark values. Meaning never by colour alone.
- Honour Reduce Motion (`@Environment(\.accessibilityReduceMotion)`): skeleton pulses stop,
  transitions become cross-fades.
- SF Symbols for icons; important actions have a text label, not only an icon.

## Loading (HIG "Loading")
- Show content as soon as any is available and fill the rest in place; placeholders should look
  like the content they stand for.
- Skeleton when the wait can exceed about a second; a spinner only for an action the user started.
- Every skeleton has a timeout path to an error state; it never breathes forever.

## SwiftUI tools for stability
- `.redacted(reason: .placeholder)` on the real view with sample data: same geometry for free.
- `.lineLimit(n, reservesSpace: true)` reserves lines.
- `AsyncImage` / custom cached image: size the container, not the image.
- `.contentTransition(.numericText())` for a number that changes in place (width already reserved).
- `ForEach` with stable server IDs; `scrollPosition(id:)` + `.scrollTargetLayout()` to keep the
  anchor; `.defaultScrollAnchor(.bottom)` for chat-like lists.
- Keep loaded data while refreshing (`.refreshable` shows the system indicator); don't swap the
  whole view back to the skeleton.
- Wrap only user-caused changes in `withAnimation`; data arriving should not animate layout.

## Accessibility
- VoiceOver: a list row reads as one sentence (`.accessibilityElement(children: .combine)` or an
  explicit label); secondary buttons in the row stay separate elements.
- Skeletons are one element labelled "Loading", children hidden.
- Test at the largest accessibility text size and in dark mode.
