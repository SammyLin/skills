# store-screenshots

[English](README.md) · 繁體中文

給 Claude Code 用的 App Store 與 Google Play 上架圖 skill。它讀你的 App 程式碼，找出能說服人下載的使用者利益，規劃每張上架圖要傳達什麼，等你確認後，再用 App 的真實畫面產出符合商店規格的圖。

![範例上架圖，淺色與深色背景](../../docs/images/store-screenshots-sheet-zh-TW.webp)

*範例上架圖（示範用的假 App）在搜尋結果裡的樣子，上排淺色、下排深色。*

## 流程

1. **讀 App**：畫面、資料模型、付費牆、新手引導；App 已經上架的話，也會讀現有的商店頁。
2. **利益**：列出 3 到 5 個使用者利益，每個都要附上程式碼裡的依據，由你確認。
3. **截圖**：你的模擬器截圖會被評為 Great、Usable 或 Retake，再配對到各個利益；缺的畫面可以用深層連結自動截。
4. **概念與方向**：找一個只有這個 App 才有的概念，再從四種方向選一種：field、chapters、close-up、statement。
5. **分鏡表（停）**：每張圖一列，寫出它要讓人相信什麼、程式碼依據、標題、用哪張截圖、版型。你說好之前不會產任何圖，`render.py` 也會拒絕執行。
6. **第一張（停）**：先只產第一張給你確認，再產其他張。
7. **檢查與評分**：標題最多兩行、對比、邊界、字型、不能有表情符號、不能有沒確認過的「第一名」宣稱；接著以搜尋結果的縮圖尺寸評整組圖。

在 Claude Code 裡輸入 `/store-screenshots`，或 `/store-screenshots https://apps.apple.com/...`。

## 尺寸與語言

支援 iPhone 6.9 吋、6.7 吋、6.5 吋，iPad 13 吋，以及 Google Play 手機。標題可以寫成 `{語系: 文字}`，加上 `--locale ja` 就會產出到 `final/ja/`。日文會在詞組之間換行，韓文會在詞之間換行，不會從字中間斷開。

## 來源

改寫自 [adamlyttleapps/claude-skill-aso-appstore-screenshots](https://github.com/adamlyttleapps/claude-skill-aso-appstore-screenshots)，加入 [leonxlnx/taste-skill](https://github.com/leonxlnx/taste-skill) 的美術指導原則，並參考 [hypersocialinc/shots](https://github.com/hypersocialinc/shots)（讀取商店頁、競品用語、多語系）與 [LeeHueeng/store-screenshots](https://github.com/LeeHueeng/store-screenshots)（HTML 手機外框、深層連結截圖、先給一張樣本）。

| 原版 | 這一版 |
| --- | --- |
| 先用 Pillow 排版，再讓 Nano Banana 重畫，最後裁切縮放 | HTML/CSS 由無頭 Chrome 直接輸出成精確尺寸，App 畫面不會被重畫 |
| 突出的面板由影像模型想像出來 | 突出的面板是從截圖裁下來再放大的真實畫面 |
| 固定風格：純色背景、置中大寫動詞 | 四種方向，依 App 的概念挑選 |
| 利益確認後就直接產圖 | 先確認分鏡表，由產圖程式強制把關 |
| 進度散在多個記憶檔 | 專案裡一個 `screenshots/set.json` |
| 只有英文、只有 iPhone 6.7 吋 | 任何語系；iPhone、iPad、Google Play |
| 需要 Gemini MCP、SF Pro 字型檔、Pillow | Python 3 標準函式庫加 Chrome |

## 試跑

```bash
cd examples/store-screenshots   # 從 repo 根目錄
python3 ../../skills/store-screenshots/render.py set.json               # final/*.png 與 sheet.png
python3 ../../skills/store-screenshots/render.py set.json --locale ja   # final/ja/
```

MIT 授權，見 repo 根目錄的 LICENSE。
