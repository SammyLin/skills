# brand-design-system

[English](README.md) · 繁體中文

從三款不同的 Logo 概念開始，依回饋調整，將確認後的品牌識別轉成 App 與網站共用的設計系統。

## 安裝

```bash
npx skills add SammyLin/skills -s brand-design-system --global
```

## Logo 產圖工具建議

優先使用 ChatGPT 的圖片生成功能，或具備圖片生成能力的 Codex 製作 Logo。ChatGPT 適合探索視覺方向與反覆微調；Codex 適合在 Repository 中管理素材及實作 Design System。若目前 agent 無法產圖，先提供可直接貼入 ChatGPT 的三款提示詞，將確認的原始圖片帶回流程，不以程式繪製的臨時圖案冒充正式 Logo。

## 使用方式

告訴 agent：「使用 brand-design-system 幫我的 App 設計 Logo 與 Design System，先提供三種不同方向。」

確認後保留 Logo 原始檔，區分品牌色與 UI 功能色，定義字體及元件，交付可離線開啟的 HTML、原始素材、JSON tokens、說明文件及 ZIP。產圖需具備相應工具，尚未製作的素材會明確標示。

品牌與基礎規範使用本 skill；完整原生 App 畫面與流程使用 mobile-app-design；實作後的版面跳動檢查使用 mobile-layout-stability。

詳見 [SKILL.md](SKILL.md)、[交付規範](references/delivery.md)與[實際案例](references/parkbird-example.md)。
