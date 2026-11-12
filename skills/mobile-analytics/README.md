# mobile-analytics

English · [繁體中文](README.zh-TW.md)

A tracking and dashboard standard for consumer (2C) iOS (SwiftUI) and Android (Compose) apps on
Firebase Analytics / GA4. It starts from the questions the data must answer, then writes one `tracking-plan.yaml` both
platforms share: GA4 recommended events where they fit and `object_action` names otherwise,
typed parameters marked for GA4 custom-dimension registration, user properties, key events,
identity and consent rules (no PII, Consent Mode v2, store privacy labels), and every metric with
a written definition. Activation and retention are measured on the app's
core value action, not on app opens.

Dashboards come as a fixed set: health, acquisition, activation, retention, core value,
monetization, release and data quality, built in GA4 Explorations and Looker Studio on the
BigQuery export (queries included), each chart tied to a metric in the plan. `plan_check.py`
lints the plan against Firebase's limits and checks the iOS and Android code against it,
so an event missing on one platform or added outside the plan fails the check.

Start from [`tracking-plan-template.yaml`](tracking-plan-template.yaml). Pairs with
[`mobile-app-design`](../mobile-app-design/), whose primary flows become the funnels.

Use it in Claude Code: `/mobile-analytics`, or say "set up tracking for this app".

Ideas adapted from Accoil's [product-tracking-skills](https://github.com/Accoil/product-tracking-skills)
(MIT), rewritten for consumer mobile apps. MIT.
