# Dashboard standard (Firebase / GA4)

Eight dashboards for a consumer app, in this order. Skip one only when the app has nothing for it
(no paywall → no Monetization). Each chart cites a metric from `tracking-plan.yaml`; the metric's
definition goes in the chart description, word for word.

| Dashboard | Answers | Charts | Build in |
|---|---|---|---|
| Health | Is the app used and stable? | DAU / WAU / MAU, stickiness (DAU/MAU), new users, crash-free users. Split by platform. | GA4 Reports (user activity); Crashlytics |
| Acquisition | Which sources bring people who stay? | New users by first-user source / medium / campaign; day-0 activation and D7 core retention by source. Judge a source by D7, not by installs. | GA4 Explorations (free form, cohort); Looker Studio on BigQuery `traffic_source` |
| Activation | Do new users reach value, and where do they drop? | Closed funnel first_open → tutorial_begin → steps → tutorial_complete → core value action, within 1 day. Day-0 activation by install day. Push opt-in by prompt source. | GA4 Funnel exploration |
| Retention | Do they come back for value? | Cohort by install week, D1 / D7 / D30, return = core value action. Push return rate. | GA4 Cohort exploration (return criteria = the core event); Looker Studio on BigQuery for exact numbers |
| Core value | How much value per user? | Core actions per active user, weekly; distribution (1, 2–5, 6+) per user. | GA4 Explorations; BigQuery for distributions |
| Monetization | Does money come in, and from where? | Paywall → in_app_purchase funnel by paywall source; trial → paid; revenue. | GA4 Funnel exploration; revenue from Play Console / App Store Connect (or RevenueCat), not from client events |
| Release | Did the last release help or hurt? | Version adoption; crash-free users, activation and core retention per `app_version`, latest vs previous. | Crashlytics (release view); Looker Studio on BigQuery for per-version funnels |
| Data quality | Can we trust the rest? | Daily count per plan event per platform; events missing on one platform; share of events missing a required parameter. | Looker Studio on BigQuery |

Put the Looker Studio pages in one report, one page per dashboard, named as in the plan.
Save the GA4 explorations with the same names and share them with the property.

## GA4 setup the dashboards depend on

- **BigQuery export on** (Admin > Product links > BigQuery): daily, plus streaming if same-day
  numbers matter. Export starts the day it is linked; there is no backfill.
- **Custom definitions** for every parameter the plan marks `ga4: dimension | metric` and every
  user property. A parameter is blank in GA4 for all days before it was registered.
- **Key events**: the plan's `key_events` (core value action, `sign_up`, `in_app_purchase`).
- **Data retention** (Admin > Data settings): 14 months, otherwise Explorations only reach 2 months
  back. BigQuery keeps everything.
- **Internal traffic**: `is_internal` user property; a dashboard-level filter `is_internal != true`
  in every exploration and Looker Studio page. Debug builds report to the -dev Firebase project.
- **Reporting identity**: Google signals on causes thresholding (small rows hidden). For product
  dashboards use device-based or observed identity, or read from BigQuery.

## Rules for every chart

- **One question per chart**, written as its title or subtitle. No chart without a question.
- **Definition visible**: metric name, formula, events, time window, filters.
- **Internal excluded** on every chart.
- **Platform split** on every user count: iOS and Android differ, and a tracking bug usually hits
  one platform. A total hides it.
- **Users, not events**, for rates and funnels (`user_pseudo_id`, the app instance, in BigQuery).
- **Fixed time zone**: the GA4 property's; BigQuery `event_date` already uses it, `event_timestamp`
  is UTC micros.
- **Full periods only**: today and the current week are partial; mark or exclude them. The
  daily BigQuery table lands the next day, and late offline events keep arriving for up to 72 hours.
- **Compare**: previous period or previous version next to the number.
- **Release markers**: annotate each store release on time-series charts.
- **Small numbers**: show n. A 40% → 60% change on 10 users is noise; say so.
- **GA4 caveats**: Explorations sample above 10M events per query (the shield icon), rows can be
  thresholded, and GA4 "active users" counts `user_engagement`. Numbers that must be exact come
  from BigQuery.

## BigQuery (Firebase export)

Tables are `analytics_<property_id>.events_YYYYMMDD` (and `events_intraday_*` when streaming).
`user_pseudo_id` is the app instance; `user_id` is set after `setUserID`. Parameters are in
`event_params`, user properties in `user_properties`, each a key plus a typed value. First-touch
acquisition is `traffic_source.source / medium / name`. `platform` is `IOS` or `ANDROID`;
`app_info.version` is the app version.

DAU by platform, internal excluded:

```sql
SELECT PARSE_DATE('%Y%m%d', event_date) AS day, platform,
       COUNT(DISTINCT user_pseudo_id) AS dau
FROM `proj.analytics_123456789.events_*`
WHERE _TABLE_SUFFIX BETWEEN FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY))
                        AND FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE(), INTERVAL 1 DAY))
  AND event_name = 'user_engagement'
  AND NOT EXISTS (SELECT 1 FROM UNNEST(user_properties) p
                  WHERE p.key = 'is_internal' AND p.value.string_value = 'true')
GROUP BY day, platform
ORDER BY day;
```

Core retention (D1 / D7 / D30 on the core value action) by install week and source:

```sql
WITH installs AS (
  SELECT user_pseudo_id,
         MIN(PARSE_DATE('%Y%m%d', event_date)) AS install_day,
         ANY_VALUE(traffic_source.source) AS source
  FROM `proj.analytics_123456789.events_*`
  WHERE event_name = 'first_open'
  GROUP BY user_pseudo_id
),
core AS (
  SELECT DISTINCT user_pseudo_id, PARSE_DATE('%Y%m%d', event_date) AS day
  FROM `proj.analytics_123456789.events_*`
  WHERE event_name IN ('alert_created', 'price_drop_viewed')
)
SELECT DATE_TRUNC(i.install_day, WEEK(MONDAY)) AS cohort, i.source,
       COUNT(DISTINCT i.user_pseudo_id) AS users,
       COUNT(DISTINCT IF(DATE_DIFF(c.day, i.install_day, DAY) = 1,  i.user_pseudo_id, NULL)) / COUNT(DISTINCT i.user_pseudo_id) AS d1,
       COUNT(DISTINCT IF(DATE_DIFF(c.day, i.install_day, DAY) = 7,  i.user_pseudo_id, NULL)) / COUNT(DISTINCT i.user_pseudo_id) AS d7,
       COUNT(DISTINCT IF(DATE_DIFF(c.day, i.install_day, DAY) = 30, i.user_pseudo_id, NULL)) / COUNT(DISTINCT i.user_pseudo_id) AS d30
FROM installs i
LEFT JOIN core c USING (user_pseudo_id)
GROUP BY cohort, source
ORDER BY cohort, users DESC;
```

Cohorts younger than 30 days show a d30 of 0 that is really "not yet"; hide or mark those cells.
Add the `is_internal` filter from the first query to both CTEs, and a `_TABLE_SUFFIX` range so the
query doesn't scan the whole export.

Data quality, events per platform per day (one platform at 0 = broken tracking there):

```sql
SELECT PARSE_DATE('%Y%m%d', event_date) AS day, event_name, platform, COUNT(*) AS n
FROM `proj.analytics_123456789.events_*`
WHERE _TABLE_SUFFIX >= FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE(), INTERVAL 14 DAY))
GROUP BY day, event_name, platform
ORDER BY day, event_name, platform;
```

Other vendors (PostHog, Amplitude, Mixpanel): the same eight dashboards as Trends / Funnel /
Retention insights; only the "Build in" column changes.
