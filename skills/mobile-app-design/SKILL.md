---
name: mobile-app-design
description: >-
  Design a native iOS (SwiftUI) and Android (Jetpack Compose) app as a whole: product brief,
  information architecture and navigation, a visual identity of its own, a token and component
  system in DESIGN.md, every screen with its hierarchy and all of its states, interaction and
  motion, copy, bad-network behaviour (offline, slow, server errors, cache-first), accessibility
  and platform adaptation (Apple HIG, Material 3). Use when
  designing, redesigning or reviewing an app's UI, giving an app its own look, starting the
  Android version of an iOS app (or the reverse), or when the user mentions app design,
  設計 App, 畫面設計, 改版, 換風格, design system, 網路不好, 離線, 斷網, offline, or asks for iOS /
  Android design best practices.
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
- **Asks**: every moment the app asks the user for something (notification, camera, location,
  ATT, sign-in, payment, an App Store / Play rating) sits at a point in the flows above, right
  after the user saw why. Nothing is asked at first launch. The rating ask is designed in every
  app, not added later: see step 6.

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
| Error / offline / slow | Keep cached content; one line on what failed, with retry. Never shown as Empty. See step 8. |
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

### Asking for a rating

Every app asks for a store rating; decide where in the brief's flows, before building.

- **When**: right after the user got what they came for (the core value action succeeded: an
  alert set, a lesson finished), from about the 3rd launch on, at most every ~120 days. Wait about
  a second so the good news lands first. Put the launch count and the gap in config.
- **Never**: at launch, from a push open before the content shows, on top of a permission prompt,
  an interstitial ad or a sheet, or after an error.
- **System prompt only**: iOS `@Environment(\.requestReview)` / `AppStore.requestReview(in:)`;
  Android Play In-App Review (`ReviewManager.requestReviewFlow` → `launchReviewFlow`). Both decide
  whether it shows (iOS at most 3 times a year) and never say whether the user rated, so never
  wire it to a button.
- **No pre-filter**: no "Do you like the app?" that sends only the happy ones to the store; both
  stores forbid it, and so do rewards for rating.
- **A way in anyway**: a 「評分」 row in Settings opens the store's write-review page (iOS
  `https://apps.apple.com/app/id<ID>?action=write-review`, Android the Play listing).
- **Measured**: `mobile-analytics` logs `rating_prompt_requested {prompt_moment}` and compares it
  with new ratings in App Store Connect / Play Console.

## 7. Platform adaptation

Same structure, identity and copy on both; native navigation and controls on each.
[ios.md](ios.md) for SwiftUI, [android.md](android.md) for Compose.

## 8. Bad network

Anything loaded over the network will meet no signal, a slow link and a failing server (a shop
basement, a train, a lift). Design and build those cases for every call, not only the happy path.

- **Failure is not empty.** A request that failed never shows 「找不到」／"No results" and never
  logs a result. Empty is a server answer with zero items; failure is a notice with 「再試一次」.
  Collapsing an error to an empty list (`try? … ?? []`, `catch { emptyList() }`) is the bug.
- **Cached first.** Show the last good data at once, refresh in place, and on failure keep it with
  a one-line notice (「沒有網路，顯示的是 10:24 的資料」). No cache → the error block from step 5,
  same header and controls, with retry.
- **Slow is a state.** Every request has a timeout (values in one config place). Still loading
  after about 8 s → a gentle 「網路有點慢…」 under the skeleton, then the error state at the
  timeout; a skeleton never breathes forever.
- **Retries.** Reads retry once with backoff on a network error, and again when the connection
  comes back while the screen is visible. Writes (follow, submit, report) never vanish: queue and
  send when back online, or say it didn't go through and undo the optimistic UI. Make writes
  idempotent so a retry can't double-post.
- **Offline is visible.** Watch connectivity; show a small offline mark where it matters, without
  moving content. Actions that need the network say so before the user fills a form.
- **Images** keep their box and show a placeholder on failure; a broken image never collapses
  the row.
- **Measure honestly.** Analytics outcome events fire only after success; a failed request logs
  nothing (or a Crashlytics non-fatal), never a zero-result or empty outcome.
- **Testable.** A debug switch fakes offline / slow / server error in the network layer
  (`-netSim offline|slow|5xx`), so every screen can be screenshotted in each state; also try the
  real thing (iOS Network Link Conditioner "Very Bad Network", Android emulator network
  throttling).

Platform details: [ios.md](ios.md) and [android.md](android.md), "Network".

## 9. Layout stability

Loading → loaded, refresh and filter changes must not move what the user did not move. Design
skeletons from the component sizes in step 4, then run the `mobile-layout-stability` skill over
every screen once they are built.

## 10. Verify on a simulator or device

- Screenshot every changed screen: loaded, loading (a debug flag that holds requests, e.g.
  `-holdLoading YES`), empty, error, offline with and without cache, slow (step 8's `-netSim`),
  largest text, dark. Look at each one yourself.
- `python3 <this skill>/palette_check.py <theme files>` exits 0, or DESIGN.md records that the
  owner chose the flagged colour.

Report per screen: what changed, why, before/after screenshots.
