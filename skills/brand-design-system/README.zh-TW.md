# brand-design-system

[English](README.md) · 繁體中文

先像產品經理一樣訪談並確認產品設計簡報，再探索三款不同 Logo，將定案的品牌識別轉成 App 與網站共用的設計系統及可重複使用的產品插圖素材庫。

## 安裝

```bash
npx skills add SammyLin/skills -s brand-design-system --global
```

## Logo 產圖工具建議

優先使用 ChatGPT 的圖片生成功能，或具備圖片生成能力的 Codex 製作 Logo。ChatGPT 適合探索視覺方向與反覆微調；Codex 適合在 Repository 中管理素材及實作 Design System。若目前 agent 無法產圖，先提供可直接貼入 ChatGPT 的三款提示詞，將確認的原始圖片帶回流程，不以程式繪製的臨時圖案冒充正式 Logo。

## 使用方式

告訴 agent：「使用 brand-design-system 幫我的 App 設計 Logo 與 Design System，先像產品經理一樣訪談我，確認需求後才產圖，再提供三種 Logo 方向及產品插圖規劃。」

確認後保留 Logo 原始檔，區分品牌色與 UI 功能色，定義字體及元件，交付可離線開啟的 HTML、原始素材、JSON tokens、說明文件及 ZIP。產圖需具備相應工具，尚未製作的素材會明確標示。

產圖前必須確認需求；Logo 定案後，依實際產品流程規劃插圖清單，先確認樣圖風格再批次產製。交付獨立插圖檔、素材清單與離線預覽，不只提供一張素材總覽。

品牌與基礎規範使用本 skill；完整原生 App 畫面與流程使用 mobile-app-design；實作後的版面跳動檢查使用 mobile-layout-stability。

詳見 [SKILL.md](SKILL.md)、[需求訪談與插圖流程](references/discovery-and-illustrations.md)、[交付規範](references/delivery.md)與[實際案例](references/parkbird-example.md)。
