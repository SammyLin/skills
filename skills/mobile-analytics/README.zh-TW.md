# mobile-analytics

[English](README.md) · 繁體中文

消費者（2C）iOS（SwiftUI）和 Android（Compose）App 在 Firebase Analytics／GA4 上的埋點與 dashboard 標準。先問清楚資料要回答哪些問題，再寫一份兩個平台共用的 `tracking-plan.yaml`：能用 GA4 建議事件就用，其餘用 `object_action` 命名；有型別的參數並標明要註冊成 GA4 自訂維度、使用者屬性、關鍵事件、身分與同意規則（不收個資、Consent Mode v2、商店隱私標籤），以及每個指標的書面定義。啟用和留存看的是 App 的核心價值動作，不是開 App。

Dashboard 固定一組：健康度、獲客、啟用、留存、核心價值、營收、版本、資料品質，做在 GA4 探索和接 BigQuery 匯出的 Looker Studio（附查詢），每張圖都對到計畫裡的一個指標。`plan_check.py` 依 Firebase 的上限檢查計畫本身，也比對 iOS 和 Android 程式碼，某個平台漏埋或埋了計畫外的事件都會失敗。

從 [`tracking-plan-template.yaml`](tracking-plan-template.yaml) 開始。可以和 [`mobile-app-design`](../mobile-app-design/) 一起用，它的主要流程就是漏斗。

在 Claude Code 裡用 `/mobile-analytics`，或直接說「幫這個 App 規劃埋點」。

概念改編自 Accoil 的 [product-tracking-skills](https://github.com/Accoil/product-tracking-skills)（MIT），針對消費者手機 App 重寫。MIT。
