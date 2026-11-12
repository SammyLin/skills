---
name: mobile-app-design
description: >-
  Design a native iOS (SwiftUI) and Android (Jetpack Compose) app as a whole: product brief,
  information architecture and navigation, a visual identity of its own, a token and component
  system in DESIGN.md, every screen with its hierarchy and all of its states, interaction and
  motion, copy, accessibility and platform adaptation (Apple HIG, Material 3). Use when
  designing, redesigning or reviewing an app's UI, giving an app its own look, starting the
  Android version of an iOS app (or the reverse), or when the user mentions app design,
  設計 App, 畫面設計, 改版, 換風格, design system, or asks for iOS / Android design best practices.
---

# mobile-app-design

Design the whole app before any one screen: what it is for, how people move through it, what
it looks like, then each screen. One design, two platforms, every state. Talk to the user in
their language. The owner decides product and visual direction; you propose and build.

## 0. Read what exists

- `DESIGN.md`, the theme/token file, shared components, the screen list (every tab, pushed page,
  sheet, alert). Owner decisions recorded in DESIGN.md are not yours to undo.
- Missing DESIGN.md → write it from [design-md-template.md](design-md-template.md) as you go
  through steps 1–5, and get the owner's yes before building screens on it.
- Reuse shared components; a second button or card style is how an app drifts.

## 1. Brief (half a page)

Who uses it, the one job they open it for, how often, in what situation (one hand in a store
aisle, at a desk), and what makes this app different. Every later choice should trace back here.

## 2. Structure

- **Screen map**: every screen and how you get there. Top-level destinations become tabs (3–5);
  everything else is a push or a sheet. Draw it as a list or a mermaid flowchart.
- **Primary flows**: the 2–3 paths that matter most (first launch → first value, the daily
  check, the money/permission moment), step by step, with the fewest taps.
  These flows are the funnels the `mobile-analytics` skill instruments.
- **Hierarchy per screen**: what the eye hits first, second, third. One primary action.
- **Density**: how many items a screen shows; decide it once for the app.

## 3. Visual identity

Give the app a look that belongs to it, from the brief, not a default.
[visual-identity.md](visual-identity.md): propose 2–3 directions, each as tokens plus one
rendered home screen; the owner picks. It also lists the overused looks to stay out of; run
`python3 <this skill>/palette_check.py <theme files>` on the result.

## 4. Tokens and components

Write the chosen direction into DESIGN.md as tokens (colour, type scale, spacing, radius,
elevation, motion) and components with exact sizes (buttons, cards, rows, chips, inputs,
segmented control, tab bar, sheets, empty/error blocks, skeleton). Sizes are the contract the
skeletons and both platforms build from.

## 5. Screens

For each screen: purpose, fixed controls, content blocks in order, the primary action, and every
state below. A screen is not done until each is drawn in the same frame:

| State | Rule |
|---|---|
| Loaded | The hierarchy from step 2. |
| Loading | Skeleton with the loaded geometry; spinner only for an action the user just started. |
| Empty | Same header and controls; one line on why and what to do. |
| Error / offline | Keep cached content; one line on what failed, with retry. |
| Partial | Each async block has its own placeholder; one slow block never holds the page. |
| First run / permission | Explain the value before the system prompt. |
| Large text, dark, Reduce Motion | Checked, not assumed. |

## 6. Interaction, motion, copy

- Gestures native to each platform (swipe back, pull to refresh, long press for secondary
  actions); never the only way to do something.
- Motion explains a change the user caused (where a sheet came from, what got deleted). Data
  arriving does not animate layout. Honour Reduce Motion.
- Feedback within 100 ms for every tap; haptics light and rare.
- Copy: verbs on buttons, the user's words not the system's, numbers formatted for the locale,
  one name per concept across the app.

## 7. Platform adaptation

Same structure, identity and copy on both; native navigation and controls on each.
[ios.md](ios.md) for SwiftUI, [android.md](android.md) for Compose.

## 8. Layout stability

Loading → loaded, refresh and filter changes must not move what the user did not move. Design
skeletons from the component sizes in step 4, then run the `mobile-layout-stability` skill over
every screen once they are built.

## 9. Verify on a simulator or device

- Screenshot every changed screen: loaded, loading (a debug flag that holds requests, e.g.
  `-holdLoading YES`), empty, error, largest text, dark. Look at each one yourself.
- `python3 <this skill>/palette_check.py <theme files>` exits 0, or DESIGN.md records that the
  owner chose the flagged colour.

Report per screen: what changed, why, before/after screenshots.
