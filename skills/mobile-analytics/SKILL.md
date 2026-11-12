---
name: mobile-analytics
description: >-
  Set the tracking (埋點) and dashboard standard for a consumer (2C) iOS (SwiftUI) and Android
  (Compose) app on Firebase Analytics / GA4: one tracking-plan.yaml shared by both platforms
  (events, parameters, user properties, identity, consent, metric definitions, dashboards), GA4
  recommended events where they fit, one analytics module per platform, DebugView verification,
  and a fixed set of dashboards in GA4 Explorations and Looker Studio on the BigQuery export
  (health, acquisition, activation, retention, core value, monetization, release, data quality).
  plan_check.py lints the plan against Firebase limits and checks both codebases against it. Use
  when adding or auditing analytics in a mobile app, designing events, building a product
  dashboard, or when the user mentions 埋點, 事件追蹤, tracking plan, Firebase Analytics, GA4,
  DebugView, BigQuery export, Looker Studio, DAU, retention, funnel, 留存, 轉換漏斗, or "what
  should we track".
---

# mobile-analytics

One plan, two platforms, every chart traceable to an event. Talk to the user in their language.
The owner decides what the business measures; you decide how it is named and wired.

- **Consumer (2C) apps**: the unit is one person on one device. No accounts, workspaces or seats.
  What matters: where people came from, whether they reach value on day 0, whether they come back,
  whether they pay.
- **Firebase Analytics (GA4) is the destination**, with the BigQuery export on. Crashlytics for
  crashes. Another vendor only if the owner already uses one; then the module in step 4 is the only
  file that changes.

Output in the app repo: `tracking-plan.yaml` (next to `DESIGN.md`), `Analytics.swift`,
`Analytics.kt`, the GA4 / Looker Studio dashboards. Start from
[tracking-plan-template.yaml](tracking-plan-template.yaml).

## 0. Read what exists

- Existing plan, `GoogleService-Info.plist` / `google-services.json` per build type, every
  `logEvent` / `setUserProperty` call on both platforms, Info.plist and manifest Firebase flags,
  GA4 custom definitions and key events, existing Explorations and Looker Studio reports. Live
  reports depend on current names: list renames and get the owner's yes first. Greenfield → the
  conventions below, no vote.
- `DESIGN.md` brief and primary flows (from `mobile-app-design`): they are the funnels.

## 1. Questions first, events second

Ask the owner for the 3–6 questions the data must answer ("do people who set an alert come back
in week 2?", "where does onboarding lose people?", "did 2.4 break the paywall on Android?"). Each
becomes a metric in `metrics:` with a written definition. An event that feeds no metric is not
added: GA4 caps names and custom dimensions, and every extra event is one more thing to keep
correct on two platforms.

Name the **core value action**: the one event that means the user got what they opened the app
for. Mark it a GA4 key event. Activation and retention are defined on it, never on `session_start`
or `user_engagement`.

## 2. Event standard

**Firebase collects these already; don't log them**: `first_open`, `session_start`,
`user_engagement`, `app_update`, `app_remove`, `os_update`, `notification_open` /
`notification_receive` (FCM), `in_app_purchase`, `app_store_subscription_*`. They are reserved;
list them under `auto_events`.

**GA4 recommended event when one fits**, exact name and parameters, so standard reports fill in:
`sign_up {method}`, `login {method}`, `tutorial_begin`, `tutorial_complete`,
`share {method, content_type, item_id}`, `select_content`, `view_item`, `screen_view`. Skip
`search {search_term}`: the term is free text (privacy); use a custom event without it.

**Custom events otherwise**:

| Rule | Standard |
|---|---|
| Name | `object_action`, snake_case, past tense: `alert_created`. Letters, digits, `_`; starts with a letter; ≤ 40 chars; no `firebase_` / `google_` / `ga_` prefix. No dots: Firebase rejects them. |
| Outcome, not UI | Fire after success (server confirmed, saved), not on tap. `alert_created`, not `save_button_tapped`. |
| Variants are parameters | `share {method: line}`, not `share_line`. One sentence covers all variants → one event. |
| Start + end only where people drop | Multi-step flows get begin/complete (+ `step` on a step event); single taps don't. |
| Screens | Turn auto screen reporting off (`FirebaseAutomaticScreenReportingEnabled = NO` in Info.plist; `google_analytics_automatic_screen_reporting_enabled = false` manifest meta-data): SwiftUI reports `UIHostingController`. Log `screen_view {screen_name}` once per appearance, `screen_name` from the plan's screen map. |
| Never | Scroll, keystroke, render, `button_clicked`, `api_called`, timers, errors (Crashlytics `recordError` / non-fatal instead). |

**Parameters**: snake_case, ≤ 40 chars; values ≤ 100 chars; ≤ 25 per event; `*_id`, `*_type`,
`*_count`, `*_source`, `is_*` suffixes; every one `required: true|false`; closed sets are `enum`;
same name = same meaning and type on every event; numbers as numbers. A parameter shows up in GA4
reports and Explorations only after it is registered as a **custom dimension or metric** (50
event-scoped dimensions, 50 metrics on a standard property), and only from that day on. Register
each one in the same change that ships it. BigQuery has every parameter regardless.

**User properties** (`setUserProperty`, set once, not per event): ≤ 25 per app, name ≤ 24 chars,
value ≤ 36 chars, registered as user-scoped custom dimensions (25 max). Standard set:
`is_logged_in`, `subscription_status`, `is_internal`. Don't re-send what GA4 has built in:
platform, app version, OS, device, country, language, first-user source / medium / campaign.

**2C moments** (only those the app has):

| Moment | How |
|---|---|
| Where they came from | GA4 first-user source / medium / campaign (BigQuery `traffic_source`). Android: Play install referrer, automatic. iOS: link Apple Search Ads in GA4; add UTM parameters to every campaign deep link and log `campaign_details` from them. Install cost stays in the ad tool. |
| First value | Core value action within 24h of `first_open`. Onboarding = `tutorial_begin` / `tutorial_complete`, plus a step event only if there are several pages. |
| Permission asks | `push_permission_answered {is_granted, prompt_source}`; same shape for ATT, location, camera. |
| Coming back | FCM pushes are logged automatically (`notification_open` with the message ID); pass a `campaign` / `label` in the FCM message so opens can be split. In-app result of a push: the core action's `entry_source: push`. |
| Sharing, deep links | `share {method, content_type, item_id}`; custom `deep_link_opened {link_type}`. |
| Paying | `paywall_viewed {paywall_source}` (custom). Purchases: link the Play and App Store apps in Firebase; Android purchases and subscription events are logged automatically; iOS StoreKit 2 calls `Analytics.logTransaction(transaction)` after verification. Revenue, renewals, refunds: Play Console / App Store Connect or RevenueCat, never summed from client events. |
| Rating prompt | Required whenever the app asks (`requestReview` / `launchReviewFlow`): `rating_prompt_requested {prompt_moment}` at the call, with a metric comparing it to new ratings in App Store Connect / Play Console. The stores never say whether it showed, so no conversion rate. |

## 3. Identity, consent, environments

- `Analytics.setUserID(<backend opaque ID>)` on signup and login; `setUserID(nil)` on logout.
  Never email or phone. `resetAnalyticsData()` only on account deletion or opt-out.
- No PII in events, parameters or user properties: no email, phone, name, address, exact location,
  free text. Google's terms forbid it; GA4 can't delete it selectively. `meta.pii_policy: none`.
- Consent: where required (EEA, UK), collection off by default
  (`FIREBASE_ANALYTICS_COLLECTION_ENABLED = NO` in Info.plist,
  `firebase_analytics_collection_enabled = false` in the manifest), then
  `setAnalyticsCollectionEnabled(true)` and Consent Mode v2 `setConsent` (`analytics_storage`,
  `ad_storage`, `ad_user_data`, `ad_personalization`) after the user answers.
- No advertising ID unless the app does ad attribution. iOS: don't link `AdSupport`; with it,
  Firebase reads the IDFA only after ATT is granted. Android: `google_analytics_adid_collection_enabled
  = false` in the manifest until consent.
- App Store privacy label and Play Data safety list what the plan collects; update them in the
  same change.
- Debug builds use their own Firebase project (a separate `GoogleService-Info.plist` /
  `google-services.json` per build config). TestFlight / internal testers set `is_internal=true`;
  every dashboard filters it.

## 4. Implementation

- `Analytics.swift` (an enum with `rawValue` names, a function per event with typed arguments)
  and `Analytics.kt` (the same in an object). Both are the only callers of `FirebaseAnalytics`;
  names and keys match `tracking-plan.yaml` exactly; no string literals at call sites. Use the
  SDK constants for recommended events (`AnalyticsEventSignUp` / `FirebaseAnalytics.Event.SIGN_UP`).
- `screen_view` from `.onAppear` / `LaunchedEffect(Unit)` of the screen root, not on recomposition.
- The SDK batches (about hourly, or on background) and queues offline. Don't build a queue, don't
  flush manually, don't block UI on a log call.

## 5. Verify

1. `uv run --with pyyaml python3 <this skill>/plan_check.py tracking-plan.yaml --src ios/ --src android/`.
   Errors: bad or reserved names, Firebase length and count limits, missing `required`, PII keys,
   metrics citing unknown events, charts citing unknown metrics or dimensions, plan events missing
   on a platform, events in the analytics module that the plan doesn't have. Exit 0 before merging.
2. DebugView, both platforms, every new or changed event: iOS launch argument `-FIRDebugEnabled`;
   Android `adb shell setprop debug.firebase.analytics.app <package>` (clear with `.none.`). Each
   fires once, at the right moment, with every required parameter, the same on iOS and Android.
3. Walk the primary flows once on each platform and read the event sequence back in DebugView.
4. After release: next day, the events appear in BigQuery `events_*` and the Data quality
   dashboard shows both platforms.

## 6. Dashboards

Build the standard set in [dashboards.md](dashboards.md): which charts, where each lives (GA4
reports, Explorations, Looker Studio on BigQuery), the rules every chart follows, and the BigQuery
queries. Every chart cites a metric from the plan. Add a chart only when it answers a step-1
question.

## Report

```
Plan: <n> events (<n> new, <n> renamed, <n> removed), <n> metrics, <n> dashboards
plan_check: pass | <errors>
GA4: custom dimensions registered <list>; key events <list>
Verified in DebugView: iOS <events> / Android <events>
Owner decisions needed: <renames, consent, PII>
```
